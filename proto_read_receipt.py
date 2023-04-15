"""
@author: Max
@date: 2023-04-07

Prototyping the receipt recognition
"""
from pathlib import Path
import pytesseract as ocr
from PIL import Image
import imghdr
import pypdfium2 as pdfium

from skimage.color import rgb2gray
from skimage import io as skio
from skimage.filters import threshold_otsu, rank
from skimage.transform import rescale
from skimage.filters import unsharp_mask
from skimage.segmentation import clear_border
from skimage.morphology import disk, diamond, binary_erosion

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib as mpl
import re
import pandas as pd
import numpy as np

mpl.rcParams.update({
    'figure.constrained_layout.use': True,

    'axes.grid': True,

    'grid.linewidth': 0.7,
    'grid.color': '#808080',

    'image.cmap': 'gray',
    'image.interpolation': 'none',
})


_TARGET_DPI = 600
_tess_options = r'--psm 6'
_lang = 'deu'
# TODO move re to dicts with lang spec. names and load single one in config
# Search aliases for receipts
_receipt_aliases = {
    'DM Drogerie': ['DM-Drogerie', 'dm.de', 'dm-'],
    'Edeka': ['lieben[ _]lebensmittel'],
}

# Maps receipt types to pattern types
_receipt_types = {
    'Aldi': 'gen',
    'Edeka': 'gen',
    'Nahkauf': 'gen',
    'DM Drogerie': 'dm',
    'Unverpackt': 'unverpackt',
}

# Maps pattern with lang to set of regexp, general is alwazs used and the
# rest is updated on top!
_patterns = {
    'gen_deu': {'simple_price_pattern': re.compile(r'(\d{1,3},\d{2})'),
                'price_with_class': re.compile(r'(\d{1,3},\d{2,3}_[AB12])'),
                'mult_pattern': re.compile(r'((?<=[xX*]_)\d{1,3},\d{2})'),
                'weight_pattern': re.compile(r'(\d{1,3},\d{1,3}(?=_EUR\/kg))'),
                'valid_article_pattern': re.compile(r'(.*?(?=(\d{1,3},\d{2})))'),
                'amount_in_weight': re.compile(r'(\b\d{1,2},\d{1,3})'),
                'total_sum_pattern': re.compile(
                    r'((?<=total_eur.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=betrag_eur.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=summe_eur.)\d{1,3}_*?,_*?\d{2})'
                    r'((?<=total.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=betrag.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=summe.)\d{1,3}_*?,_*?\d{2})',
                    re.IGNORECASE)
                },
    'dm_deu': {'mult_pattern': re.compile(r'(\d{1,4}_*?(?=[xX*]))|((?<=[xX*])_*?\d{1,2},\d{1,3})'),
               'valid_article_pattern_mult': re.compile(
                   r'(?=_[a-zA-Z]).*?(?=_\d{1,2},\d{1,3})')
               },
    'unverpackt_deu': {'article_number': re.compile(r'\d{1,}'),
                       'mult_pattern': re.compile(r'\d{1,2},\d{1,3}')},
}


# cid = fig.canvas.mpl_connect(
#     'key_press_event', lambda event: rot_event(ax[1], event))
# TODO Rotation is the most important factor to get a good ocr!
def rot_event(act_ax, event):
    if event.inaxes is act_ax:
        if event.key == 'right':
            print('rot right')
        elif event.key == 'left':
            print('rot left')
        elif event.key == 'shift+right':
            print('rot right much')
        elif event.key == 'shift+left':
            print('rot left much')
        else:
            return


def get_vendor(raw_text):
    for rec_t in _receipt_types.keys():
        check_strings = [rec_t] + _receipt_aliases.get(rec_t, [])
        this_check = any([re.search(rf'(\b{cs:s}|{cs:s}\b)', raw_text, re.IGNORECASE) is not None
                          for cs in check_strings])

        if this_check:
            patterns = _receipt_types[rec_t]
            print('Vendor found: ', rec_t)
            return rec_t, patterns

    print('No vendor found, using general')
    return None, 'gen'


def get_patterns(pattern, lang):
    pats = _patterns['gen' + '_' + _lang]
    pats.update(_patterns[pattern + '_' + _lang])
    return pats


def extract_image_text(bin_img):
    tess_in = Image.fromarray(bin_img)
    tess_in.format = 'TIFF'
    data = ocr.image_to_data(tess_in, lang='deu', output_type='data.frame',
                             config=_tess_options).dropna(
        subset=['text']).reset_index()

    data['height_plus_top'] = data['height'] + data['top']
    data['width_plus_left'] = data['width'] + data['left']

    # Collapse into single lines
    data_by_line = data.groupby('line_num')
    data_combined = pd.concat((
        data_by_line['text'].apply('_'.join),
        data_by_line['top'].min(),
        data_by_line['left'].min(),
        data_by_line['height_plus_top'].max(),
        data_by_line['width_plus_left'].max()),
        axis=1).reset_index()

    # Make BBox format for MPL
    data_combined['width'] = data_combined['width_plus_left'] - data_combined['left']
    data_combined['height'] = data_combined['height_plus_top'] - data_combined['top']
    data_combined.drop(['height_plus_top', 'width_plus_left'], axis=1)

    # Re-Get raw text instead of tesseract twice
    raw_text = '\n'.join(data_combined.text)
    for _, grp in data.groupby('line_num'):
        raw_text += ' '.join(grp.text.ravel()) + '\n'

    return data_combined, raw_text


def extract_pdf_data(file, page=0):
    # Split line-wise
    pdf = pdfium.PdfDocument(file)
    pagedata = pdf.get_page(page)
    txt = pagedata.get_textpage().get_text_range().split('\n')

    txt = [line.strip() for line in txt if line.strip()]
    # txt_depr = [line.strip() for line in extract_text(file).split('\n') if line.strip()]

    # Remove  many spaces, dont need the layout
    txt = [' '.join(line.split()) for line in txt]
    # Spaces to underscore, better visible
    txt = [line.replace(' ', '_') for line in txt]

    # Create raw and parse the rest into the DataFrame format which is used
    # in the main text parser
    raw_text = '\n'.join(txt)

    data = pd.DataFrame(columns=['line_num', 'text'])
    data['text'] = txt
    data['line_num'] = [i + 1 for i in range(len(txt))]

    scale = _TARGET_DPI / pagedata.get_width() * (80 / 25.4)
    ref_img = rgb2gray(pagedata.render(scale=scale).to_numpy())

    # Text BB
    txtpage = pagedata.get_textpage()
    rects = np.array([txtpage.get_rect(i) for i in range(txtpage.count_rects())])
    # Now this is left, bottom, right and top in pdf, so scale, invert y
    # and convert for MPL
    data['left'] = rects[:, 0] * scale
    data['top'] = ref_img.shape[0] - rects[:, 3] * scale
    data['width'] = (rects[:, 2] - rects[:, 0]) * scale
    data['height'] = (rects[:, 3] - rects[:, 1]) * scale

    return data, raw_text, ref_img


def preprocess_image(imgpath, otsu='global',
                     rescale_image=True, unsharp_ma=True, final_er_dil=1,
                     remove_border_art=True, receipt_width=80, show=False):
    """
    Assumes portrait mode. Filter factors are designed after scaling!

    width in mm
    """
    proc_img = rgb2gray(skio.imread(rec))
    if rescale_image:
        scale = _TARGET_DPI / proc_img.shape[1] * (80 / 25.4)
        proc_img = rescale(proc_img, scale)

    if unsharp_ma:
        proc_img = unsharp_mask(proc_img, radius=3, amount=0.5)

    # Convert to binary
    if otsu == 'global':
        threshold = threshold_otsu(proc_img)

    elif otsu == 'local':
        radius = 29
        selem = disk(radius)
        threshold = rank.otsu(proc_img, selem) / 254

    bin_img = proc_img >= threshold

    # If final filters are set, do the best to get strong black letters
    if final_er_dil >= 1:
        for i in range(final_er_dil):
            bin_img = binary_erosion(bin_img, diamond(final_er_dil))
        # bin_img = gaussian(bin_img, sigma=1) > threshold

    if remove_border_art:
        bin_img = ~clear_border(~bin_img, 30)

    # Pad the image, grayscale with nan for plotting and binary with ones
    # Padding is set to approx. 10pt ~ 50px
    proc_img = np.pad(proc_img, ((50, 50), (50, 50)), constant_values=np.nan)
    bin_img = np.pad(bin_img, ((50, 50), (50, 50)), constant_values=1)

    fig = None
    if show:
        fig, ax = plt.subplots(1, 2, sharex=True, sharey=True)
        ax[0].imshow(proc_img)
        ax[1].imshow(bin_img)

    return proc_img, bin_img, fig


def parse_unverpackt(data, pats, retrieved_data, fig=None):
    total_price = 0
    line_buffer = []
    # First item is usually first price - 2
    first_item = 0
    first_item = data['text'].str.extract(pats['simple_price_pattern']).first_valid_index()
    first_item = max(0, first_item - 2)
    for _, group in data.loc[first_item:, :].iterrows():
        this_line = group['text']
        print('Analyzing: ', this_line)

        # Is there a price with tax class? Then the line before is ArtNr
        # and the one before that name
        if (re_res := pats['price_with_class'].search(this_line)) is not None:
            price, tax_class = re_res.group(0).split('_')

            try:
                price = float(price.replace(',', '.'))
            except ValueError:
                price = 0.

            tax_class = int(tax_class.upper().replace('A', '1').replace('B', '2'))
            article_number = int(pats['article_number'].search(line_buffer[-1]).group(0))
            article_name = line_buffer[-2].replace('_', ' ')

            print('Item: ', article_number, article_name, price, tax_class)

            # extract units and price per unit
            weight_info = pats['mult_pattern'].findall(this_line)
            try:
                amount = float(weight_info[0].replace(',', '.'))
                price_per_unit = float(weight_info[1].replace(',', '.'))
            except ValueError:
                print("Add this to logger")
                amount = 0
                price_per_unit = 0

            line_buffer = []

            retrieved_data = pd.concat(
                [retrieved_data, pd.DataFrame({
                    'ArtNr': article_number,
                    'Name': article_name,
                    'Price': price,
                    'TaxClass': tax_class,
                    'Units': amount,
                    'PricePerUnit': price_per_unit
                }, index=[0])],
                ignore_index=True)

            if fig is not None:
                box_xy = group['left'], group['top']
                box_height = group['height_plus_top'] - box_xy[1]
                box_width = group['width_plus_left'] - box_xy[0]
                text_rec = Rectangle(box_xy, box_width, box_height,
                                     ec='green', fc='none', lw=0.3)

                fig.axes[0].add_patch(text_rec)

        line_buffer.append(this_line)

        # Finally, is there a final price? If so break the loop
        if (re_res := pats['total_sum_pattern'].search(this_line)) is not None:
            try:
                total_price = float(re_res.group(0).replace(',', '.').replace('_', ''))
                print('Found total price: ', total_price)
                break
            except ValueError:
                ...

    return retrieved_data, total_price

# TODO DM negative prices

# %% Main process
receipts = [Path(f) for f in [
    r'examples/IMG_5991.JPG',
    r'examples/IMG_6005.JPG',  # meh
    r'examples/IMG_6006.JPG',
    r'examples/IMG_6277.jpg',
]]

pdfs = [Path(f) for f in [
    r'examples/dm-eBon_2023-04-06_09-32-32.pdf.pdf',
    r'examples/dm-eBon_2023-04-12_09-08-06.pdf.pdf'
]]

# for rec in receipts:
rec = pdfs[0]
# rec = receipts[2]

if imghdr.what(rec) is not None:
    proc_img, bin_img, fig = preprocess_image(rec, show=True, final_er_dil=1)
    data, raw_text = extract_image_text(bin_img)


else:
    if rec.suffix == '.pdf':
        data, raw_text, proc_img = extract_pdf_data(rec)
        fig, ax = plt.subplots(1, 2)
        ax[0].imshow(proc_img)
    else:
        raise IOError('Only image files and pdf are supported!')


# Analyze vendor and get pattern
vendor, pattern = get_vendor(raw_text)
pats = get_patterns(pattern, _lang)

# Initialize, general
# TODO replace by mandatory cols from config
retrieved_data = pd.DataFrame(
    columns=['ArtNr', 'Name', 'Units', 'PricePerUnit', 'Price', 'TaxClass'])


if vendor == 'Unverpackt':
    retrieved_data, total_price = parse_unverpackt(
        data, pats, retrieved_data, fig)

# And this will be something like "general" function
# First item is usually first price, if not let it 0 so get everything
first_item = 0
first_item = data['text'].str.extract(pats['simple_price_pattern']).first_valid_index()

# Initialize variables, special
this_row_exists = False
bonus = 0
unused_lines = []
total_price = 0
# Parse line by line and see what can be classified
for _, group in data.loc[first_item:, :].iterrows():
    has_price, has_weight, has_mult = False, False, False
    this_line = group['text']
    print('Analyzing: ', this_line)

    # Is there a price with tax class?
    if (re_res := pats['price_with_class'].search(this_line)) is not None:
        price, tax_class = re_res.group(0).split('_')

        try:
            price = float(price.replace(',', '.'))
        except ValueError:
            price = 0.

        tax_class = int(tax_class.upper().replace('A', '1').replace('B', '2'))
        has_price = True
        print('Normal item: ', this_line, price, tax_class)

    # Is there a kg price, e.g. weight multiplier (then skip normal mult.)
    if (re_res := pats['weight_pattern'].search(this_line)) is not None:
        price_per_unit = float(re_res.group(0).replace(',', '.'))
        try:
            amount = float(
                pats['amount_in_weight'].search(this_line).group(0).replace(',', '.'))
        except ValueError:
            amount = 0

        has_weight = True
        print('Found weight: ', amount, price_per_unit)

    # If no weight, is there a multiplier?
    elif (re_res := pats['mult_pattern'].search(this_line)) is not None:
        if pattern == 'dm':
            re_res = pats['mult_pattern'].findall(this_line)
            try:
                amount = float(re_res[0][0].replace(',', '.'))
                price_per_unit = float(re_res[1][1].replace(',', '.').replace('_', ''))
            except ValueError:
                amount = 0
                price_per_unit = 0
        else:
            try:
                price_per_unit = float(re_res.group(0).replace(',', '.'))
            except ValueError:
                price_per_unit = 0
        has_mult = True
        print('Found mult: ', price_per_unit)

    if pattern == 'dm':
        # TODO parse negative values into bonus
        ...

    # Analysis done, now extract and sort the data, this is the most
    # critical part and, as the search above, vendor specific!
    if not (has_price or has_mult or has_weight):
        unused_lines.append(this_line)
        # Dont continue due to final price analysis

    # Has mult, e.. weight (before item): pre-create row and set flag
    if has_mult and not has_price:
        retrieved_data = pd.concat(
            [retrieved_data, pd.DataFrame({
                'PricePerUnit': price_per_unit,
            }, index=[0])],
            ignore_index=True)
        this_row_exists = True

    # Found weight but no price with tax class: Lookbehind and assemble
    if has_weight and not has_price:
        retrieved_data.loc[
            retrieved_data.index[-1], ['Units', 'PricePerUnit']] = [amount, price_per_unit]

    # Found weight and price - this is a style where the name was in the row
    # before but not matched (get it from unused_lines). This is Rewe receipt
    # TODO fill -1 if present
    elif has_weight and has_price:
        retrieved_data = pd.concat(
            [retrieved_data, pd.DataFrame({
                'ArtNr': -1,
                'Name': unused_lines[-1].replace('_', ' '),
                'Price': price,
                'TaxClass': tax_class,
                'PricePerUnit': price_per_unit,
                'Units': amount
            }, index=[0])],
            ignore_index=True)

    # Price and mult in a singleline: DM
    if has_price and has_mult:
        article_data = pats['valid_article_pattern_mult'].search(this_line).group(0).split('_')
        article_name = ' '.join([art for art in article_data if art])
        retrieved_data = pd.concat(
            [retrieved_data, pd.DataFrame({
                'ArtNr': -1,
                'Name': article_name,
                'Price': price,
                'TaxClass': tax_class,
                'Units': amount,
                'PricePerUnit': price_per_unit
            }, index=[0])],
            ignore_index=True)

    # If this has a price and nothing else, then try to extract the name,
    # a possible article id and with that creating a new item
    if has_price and not (has_mult or has_weight):
        article_data = pats['valid_article_pattern'].match(this_line).group(0).split('_')
        if (re_res := re.match(r'\d{1,}', article_data[0])) is not None:
            article_number = int(re_res.group(0))
            article_name = ' '.join(article_data[1:]).strip()
        else:
            article_number = -1
            article_name = ' '.join(article_data).strip().lower().title()
        print('Final: ', article_number, article_name)

        # Lookahead from before if price was missing for a mult line
        if this_row_exists:
            retrieved_data.loc[retrieved_data.index[-1],
                               ['ArtNr', 'Name', 'Price', 'TaxClass']] = [
                                   article_number, article_name, price, tax_class]
            this_row_exists = False
        else:
            retrieved_data = pd.concat(
                [retrieved_data, pd.DataFrame({
                    'ArtNr': article_number,
                    'Name': article_name,
                    'Price': price,
                    'TaxClass': tax_class
                }, index=[0])],
                ignore_index=True)

    # Heavy lifting done, phew! Now just plot if this was valid
    # Plot box if this line is a valid price around the full line
    if has_price and 'left' in group:
        text_rec = Rectangle((group['left'], group['top']), group['width'], group['height'],
                             ec='green', fc='none', lw=0.3)

        fig.axes[0].add_patch(text_rec)

    # Finally, is there a final price? If so break the loop
    elif (re_res := pats['total_sum_pattern'].search(this_line)) is not None:
        try:
            total_price = float(re_res.group(0).replace(',', '.').replace('_', ''))
            print('Found total price: ', total_price)
            break
        except ValueError:
            ...

    print(20 * '-')

# TODO Post process, DM with weight info in text
if vendor == 'DM Drogerie':
    ...

# Post process, general
units_nan = retrieved_data['Units'].isna()
retrieved_data.loc[units_nan, 'Units'] = (retrieved_data.loc[units_nan, 'Price'] /
                                          retrieved_data.loc[units_nan, 'PricePerUnit'])

retrieved_data['Units'] = retrieved_data['Units'].fillna(1)

ppu_nan = retrieved_data['PricePerUnit'].isna()
retrieved_data.loc[ppu_nan, 'PricePerUnit'] = (retrieved_data.loc[ppu_nan, 'Price'] /
                                               retrieved_data.loc[ppu_nan, 'Units'])

# Add more data. Some of this is not needed "per item" but this makes this
# data the most accessbile later on
retrieved_data['Category'] = 'Supermarket'
retrieved_data['Group'] = 'na'
retrieved_data['Vendor'] = vendor
retrieved_data['Date'] = pd.to_datetime('02/11/2022', dayfirst=True)
