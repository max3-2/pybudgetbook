"""
@author: Max
@date: 2023-04-07

Prototyping the receipt recognition
"""
from pathlib import Path
import pytesseract as ocr
from PIL import Image

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

# Maps receipt types to pattern types
_receipt_types = {
    'Aldi': 'gen',
    'Nahkauf': 'gen',
    'DM Drogerie': 'gen',
    'Unverpackt': 'unverpackt',
}

# Maps pattern with lang to set of regexp
_patterns = {
    'gen_deu': {'simple_price_pattern': re.compile(r'(\d{1,3},\d{2})'),
                'price_with_class': re.compile(r'(\d{1,3},\d{2}_[AB12])'),
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
                }
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


def preprocess_image(imgpath, otsu='global',
                     rescale_image=True, unsharp_ma=True, final_er_dil=True,
                     remove_border_art=True, receipt_width=80, show=False):
    """
    Assumes portrait mode. Filter factors are designed after scaling!

    width in mm
    """
    proc_img = rgb2gray(skio.imread(rec))
    # TODO  remove AA, final Gauss
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
    if final_er_dil:
        bin_img = binary_erosion(bin_img, diamond(1))
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


# TODO Add compile for regexp in loops!
# TODO move re to dicts with lang spec. names and load single one in config

receipts = [Path(f) for f in [
    r'examples/IMG_5991.JPG',
    r'examples/IMG_6005.JPG',
    r'examples/IMG_6006.JPG',
]]

# for rec in receipts:
rec = receipts[1]

proc_img, bin_img, fig = preprocess_image(rec, show=True)

tess_in = Image.fromarray(bin_img)
tess_in.format = 'TIFF'
data = ocr.image_to_data(tess_in, lang='deu', output_type='data.frame', config=_tess_options).dropna(
    subset=['text']).reset_index()

# Re-Get raw text instead of tesseract twice
raw_text = ''
for _, grp in data.groupby('line_num'):
    raw_text += ' '.join(grp.text.ravel()) + '\n'

# Analyze vendor
# TODO force this before running into the analysis!
has_vendor = np.argmax(
    [re.search(rf'(\b{sh:s}|{sh:s}\b)', raw_text, re.IGNORECASE) is not None
     for sh in _receipt_types.keys()])
if has_vendor.any():
    vendor = list(_receipt_types.keys())[has_vendor]
    pats = _patterns[_receipt_types[vendor] + '_' + _lang]
    print("Vendor found: ", vendor)
else:
    print('No vendor found, using general')
    pats = _patterns['gen_' + _lang]


# Get patterns by language and receipt
# ToDo T/EXC in final code


# First item is usually first price, if not let it 0 so get everything
# Move tis to beginning of line so to catch all on this line if price
# is not the first item
first_item = 0
first_item = data['text'].str.extract(pats['simple_price_pattern']).first_valid_index()
first_item = data.loc[(data['block_num'] == data.loc[first_item, 'block_num']) & (
    data['line_num'] == data.loc[first_item, 'line_num'])].first_valid_index()

# Initialize variables
retrieved_data = pd.DataFrame(
    columns=['ArtNr', 'Name', 'Units', 'PricePerUnit', 'Price', 'TaxClass'])
this_row_exists = False
total_price = 0
unused_lines = []

# Parse line by line and see what can be classified
for line, group in data.loc[first_item:, :].groupby('line_num'):
    has_price, has_weight, has_mult = False, False, False

    # Smash the line and regexp to victory
    this_line = '_'.join(group.text.str.strip())
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

    # If no weight, is there a multiplier
    elif (re_res := pats['mult_pattern'].search(this_line)) is not None:
        try:
            price_per_unit = float(re_res.group(0).replace(',', '.'))
        except ValueError:
            price_per_unit = 0
        has_mult = True
        print('Found mult: ', price_per_unit)

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
    if has_price:
        box_xy = (group['left'].min(), group['top'].min())
        box_height = (group['height'] + group['top']).max() - box_xy[1]
        box_width = (group['width'] + group['left']).max() - box_xy[0]
        text_rec = Rectangle(box_xy, box_width, box_height,
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

# Post process
units_nan = retrieved_data['Units'].isna()
retrieved_data.loc[units_nan, 'Units'] = (retrieved_data.loc[units_nan, 'Price'] /
                                          retrieved_data.loc[units_nan, 'PricePerUnit'])

ppu_nan = retrieved_data['PricePerUnit'].isna()
retrieved_data.loc[ppu_nan, 'PricePerUnit'] = (retrieved_data.loc[ppu_nan, 'Price'] /
                                               retrieved_data.loc[ppu_nan, 'Units'])

retrieved_data['Units'] = retrieved_data['Units'].fillna(1)
