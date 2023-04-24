"""
@author: Max
@date: 2023-04-07

Prototyping the receipt recognition
"""
from pathlib import Path
import imghdr
import logging

import matplotlib.pyplot as plt
import pandas as pd

# TODO make relative imports
import pybudgetbook.config.constants as bbconstants
import pybudgetbook.config.config as bbconfig
from pybudgetbook import parsers
from pybudgetbook.config.plotting_conf import set_style
from pybudgetbook import bb_io, fuzzy_match
from pybudgetbook.receipt import Receipt

set_style()
logger = logging.getLogger(__name__)


# %% Main process
# receipts = [Path(f) for f in [
#     r'examples/IMG_5991.JPG',
#     r'examples/IMG_6006.JPG',
#     r'examples/IMG_6277.jpg',
# ]]

# pdfs = [Path(f) for f in [
#     r'examples/dm-eBon_2023-04-06_09-32-32.pdf.pdf',
#     r'examples/dm-eBon_2023-04-12_09-08-06.pdf.pdf'
# ]]

# # for rec in receipts:
# # rec = pdfs[0]
# rec = receipts[1]

# TODO create that in console!
if rec is None:
    rec = Path('')

recc = Receipt(rec)
recc.filter_image().extract_data()
recc.show_receipt()
_ = recc.parse_vendor()
retrieved_data, total_price = recc.parse_data()

# # Analyze vendor and get pattern
# vendor, pattern = parsers.get_vendor(raw_text)
# pats = parsers.get_patterns(pattern, bbconfig.options['lang'])
# if vendor is None:
#     vendor = input("No vendor detected - please add: ")
#     assert vendor in bbconfig.receipt_types.keys(), "Invalid vendor"

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
    lambda data: fuzzy_match.match_group(data, match_data), axis=1)

# %% With no UI, do some manual processing
# Add more data. Some of this is not needed "per item" but this makes this
# data the most accessbile later on. This is mainly from UI so now its
# manual
retrieved_data['Category'] = 'Supermarket'

retrieved_data['Vendor'] = vendor
retrieved_data['Date'] = pd.to_datetime('13/04/2023', dayfirst=True)

metadata = {'tags': 'aldi;general',
            'total_extracted': total_price}

retrieved_data.attrs = metadata

# %% Resort
additional_cols = tuple(
    set(retrieved_data.columns).difference(set(bbconstants._MANDATORY_COLS)))
retrieved_data = retrieved_data[list(bbconstants._MANDATORY_COLS + additional_cols)]

# Quick sanity check
diff = total_price - retrieved_data['Price'].sum()
print(f'Price differece total to analyzed: {diff:.2f}')

# %% Do manual grouping and correct any data NOW!
# Then feed back the groups, get user data or warn
fuzzy_match.matcher_feedback(retrieved_data)

# %% And then save with metadata
bb_io.save_with_metadata(retrieved_data, img_path=rec)
