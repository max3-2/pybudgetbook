"""
A small helper that shows how to use a manual script to build a data entry.
This will be adapted as soon as a stable API is finalized!
"""
import logging
import pandas as pd

import pybudgetbook.config.constants as bbconstants
import pybudgetbook.config.config as bbconfig
from pybudgetbook import bb_io, fuzzy_match

logger = logging.getLogger(__name__)

# %% Get a Dataframe template
retrieved_data = pd.DataFrame(columns=bbconstants._MANDATORY_COLS)
total_price = 0.

# %% Add Data here, this can be used as template!
# retrieved_data.loc[0] = [0, 0, -1, "Name", 1, 1, 1, 1, '', '']
# total_price = 0.

# %% Then edit and adapt data as needed...

# %% Now match the groups
retrieved_data = fuzzy_match.find_groups(retrieved_data)

# %% With no UI, do some manual processing
# Add more data. Some of this is not needed "per item" but this makes this
# data the most accessbile later on. This is mainly from UI so now its
# manual
retrieved_data['Category'] = 'Small Stores'

retrieved_data['Vendor'] = 'Store name'
retrieved_data['Date'] = pd.to_datetime('05/05/2023', dayfirst=True)

metadata = {'tags': 'other;tag2',
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
# Add an image please
imp = Path()
bb_io.save_with_metadata(retrieved_data, img_path=imp,
                         unique_name=True, move_on_save=True)
