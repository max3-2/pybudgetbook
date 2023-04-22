"""
@author: Max
@date: 2023-04-07

Prototyping the receipt recognition
"""
import logging

import pandas as pd

# TODO make relative imports
import pybudgetbook.config.constants as bbconstants
import pybudgetbook.config.config as bbconfig
from pybudgetbook import bb_io, fuzzy_match

logger = logging.getLogger(__name__)

# %% Get a Dataframe template
retrieved_data = pd.DataFrame(columns=bbconstants._MANDATORY_COLS)
total_price = 0.

# %% Add Data here

# %% Now match the groups
match_data = bb_io.load_group_match_data(bbconfig.options['lang'])

retrieved_data['Group'] = retrieved_data.apply(
    lambda data: fuzzy_match.match_group(data, match_data), axis=1)

# %% With no UI, do some manual processing
# Add more data. Some of this is not needed "per item" but this makes this
# data the most accessbile later on. This is mainly from UI so now its
# manual
retrieved_data['Category'] = 'Supermarket'

retrieved_data['Vendor'] = 'Vendor'
retrieved_data['Date'] = pd.to_datetime('02/11/2022', dayfirst=True)

metadata = {'tags': 'adli;general;supermarket',
            'total_extracted': total_price}

retrieved_data.attrs = metadata

# %% Resort
additional_cols = tuple(
    set(retrieved_data.columns).difference(set(bbconstants._MANDATORY_COLS)))
retrieved_data = retrieved_data[list(bbconstants._MANDATORY_COLS + additional_cols)]

diff = total_price - retrieved_data['Price'].sum()
print(f'Price differece total to analyzed: {diff:.2f}')

# %% Do manual grouping and correct any data NOW!
# Then feed back the groups, get user data or warn
fuzzy_match.matcher_feedback(retrieved_data)

# %% And then save with metadata
bb_io.save_with_metadata(retrieved_data)
