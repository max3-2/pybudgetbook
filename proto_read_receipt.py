"""
@author: Max
@date: 2023-04-07

Prototyping the receipt recognition
"""
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QCoreApplication
import pandas as pd

# TODO make relative imports
from pybudgetbook.config.plotting_conf import set_style
from pybudgetbook import bb_io, fuzzy_match
from pybudgetbook.receipt import Receipt


set_style()


if QCoreApplication.instance() is None:
    app = QCoreApplication()
receipt_file = QFileDialog().getOpenFileName(caption='Select receipt')[0]

rec = Receipt(receipt_file)
rec.filter_image().extract_data()
rec.show_receipt()
_ = rec.parse_vendor()
retrieved_data, total_price = rec.parse_data()
rec_date = rec.parse_date()

retrieved_data = fuzzy_match.find_groups(retrieved_data)

# Quick sanity check
diff = total_price - retrieved_data['Price'].sum()
print(f'Price differece total to analyzed: {diff:.2f}')

# TODO Post process DM with weight info in text, maybe upcoming

# %% With no UI, do some manual processing
# Add more data. Some of this is not needed "per item" but this makes this
# data the most accessbile later on. This is mainly from UI so now its
# manual
retrieved_data['Category'] = 'Supermarket'

retrieved_data['Vendor'] = rec.vendor

if rec_date is None:
    rec_date = pd.to_datetime('13/04/2023', dayfirst=True)

retrieved_data['Date'] = rec_date

metadata = {'tags': 'real;general',
            'total_extracted': total_price}

retrieved_data.attrs = metadata

retrieved_data = bb_io.resort_data(retrieved_data)

# %% Do manual grouping and correct any data NOW!
# Then feed back the groups, get user data or warn
fuzzy_match.matcher_feedback(retrieved_data)

# %% And then save with metadata
bb_io.save_with_metadata(retrieved_data, img_path=rec.file)
