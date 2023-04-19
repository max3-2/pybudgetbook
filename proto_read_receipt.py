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
import json
import logging

from skimage.color import rgb2gray
from skimage import io as skio
from skimage.filters import threshold_otsu, rank
from skimage.transform import rescale
from skimage.filters import unsharp_mask
from skimage.segmentation import clear_border
from skimage.morphology import disk, diamond, binary_erosion

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# TODO make relative imports
import pybudgetbook.config.constants as bbconstants
import pybudgetbook.config.config as bbconfig
from pybudgetbook import parsers
from pybudgetbook.config.plotting_conf import set_style
from pybudgetbook import bb_io


set_style()
logger = logging.getLogger(__name__)


def extract_image_text(bin_img, lang):
    tess_in = Image.fromarray(bin_img)
    tess_in.format = 'TIFF'
    data = ocr.image_to_data(tess_in, lang=lang, output_type='data.frame',
                             config=bbconstants._TESS_OPTIONS).dropna(
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

    scale = bbconstants._TARGET_DPI / pagedata.get_width() * (80 / 25.4)
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
    proc_img = rgb2gray(skio.imread(imgpath))
    if rescale_image:
        scale = bbconstants._TARGET_DPI / proc_img.shape[1] * (80 / 25.4)
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


# %% Main process
receipts = [Path(f) for f in [
    r'examples/IMG_5991.JPG',
    r'examples/IMG_6006.JPG',
    r'examples/IMG_6277.jpg',
]]

pdfs = [Path(f) for f in [
    r'examples/dm-eBon_2023-04-06_09-32-32.pdf.pdf',
    r'examples/dm-eBon_2023-04-12_09-08-06.pdf.pdf'
]]

# for rec in receipts:
# rec = pdfs[0]
rec = receipts[1]

if imghdr.what(rec) is not None:
    proc_img, bin_img, fig = preprocess_image(rec, show=True, final_er_dil=1)
    data, raw_text = extract_image_text(bin_img, bbconfig.options['lang'])
    plot_ax = fig.axes[0]

else:
    if rec.suffix == '.pdf':
        data, raw_text, proc_img = extract_pdf_data(rec)
        fig, ax = plt.subplots(1, 2)
        ax[0].imshow(proc_img)
        plot_ax = ax[0]
    else:
        raise IOError('Only image files and pdf are supported!')


# Analyze vendor and get pattern
vendor, pattern = parsers.get_vendor(raw_text)
pats = parsers.get_patterns(pattern, bbconfig.options['lang'])
if vendor is None:
    vendor = input("No vendor detected - please add: ")
    assert vendor in bbconfig.receipt_types.keys(), "Invalid vendor"

if pattern == 'unverpackt':
    retrieved_data, total_price = parsers.parse_receipt_unverpackt(
        data, pats, pattern, plot_ax)
else:
    retrieved_data, total_price = parsers.parse_receipt_general(
        data, pats, pattern, plot_ax)

# TODO Post process DM with weight info in text, maybe upcoming

# Post process, general
units_nan = retrieved_data['Units'].isna()
retrieved_data.loc[units_nan, 'Units'] = (retrieved_data.loc[units_nan, 'Price'] /
                                          retrieved_data.loc[units_nan, 'PricePerUnit'])

retrieved_data['Units'] = retrieved_data['Units'].fillna(1)

ppu_nan = retrieved_data['PricePerUnit'].isna()
retrieved_data.loc[ppu_nan, 'PricePerUnit'] = (retrieved_data.loc[ppu_nan, 'Price'] /
                                               retrieved_data.loc[ppu_nan, 'Units'])

# %% Now match the groups
match_data = bb_io.load_group_match_data(bbconfig.options['lang'])

retrieved_data['Group'] = retrieved_data.apply(
    lambda data: parsers.match_group(data, match_data), axis=1)

# %% With no UI, do some manual processing
# Add more data. Some of this is not needed "per item" but this makes this
# data the most accessbile later on. This is mainly from UI so now its
# manual
retrieved_data['Category'] = 'Supermarket'

retrieved_data['Vendor'] = vendor
retrieved_data['Date'] = pd.to_datetime('02/11/2022', dayfirst=True)

metadata = {'tags': 'adli;general;suerpmarket',
            'total_extracted': total_price}

# %% Resort
additional_cols = tuple(
    set(retrieved_data.columns).difference(set(bbconstants._MANDATORY_COLS)))
retrieved_data = retrieved_data[list(bbconstants._MANDATORY_COLS + additional_cols)]

# %% Do manual grouping and correct any data NOW!
# Then feed back the groups, get user data or warn
# TODO Add flag if category does not exist to catch typos
user_match_data, user_match_file = bb_io.load_user_match_data(bbconfig.options['lang'])
basic_match_data, _ = bb_io.load_basic_match_data(bbconfig.options['lang'])

feed_data = list(zip(retrieved_data.Name, retrieved_data.Group))
# make for loop
feedname, feedgroup = feed_data[0]
if feedgroup not in user_match_data:
    error = ('Group does not exist and creating is not enabled, check for '
             'typos and / enable flag!')
    logger.error(error)
    raise RuntimeError(error)

# Strip article name as best as possible, check if in base data and if not
# run set with group

# TODO strip

if feedgroup in basic_match_data:
    if feedname in basic_match_data[feedgroup]:
        logger.debug('This article is already matched in the basic data set')
        # continue

user_match_data[feedgroup] = list(set(user_match_data[feedgroup]).union([feedname]))

print('Updated data: ')
print(user_match_data)

# %% And then save with metadata
