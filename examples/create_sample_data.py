"""
Creates a data sample to play around. Please do not use your existing working
directory if there is data present that might mess it up.
"""
import logging
import pandas as pd
import numpy as np
import sys
import requests
from datetime import datetime, timedelta
from pybudgetbook.configs.constants import _CATEGORIES
from pybudgetbook.bb_io import _load_basic_match_data, save_with_metadata
from pybudgetbook.configs.config import options

try:
    from PySide6.QtWidgets import QMessageBox, QApplication
    from PySide6.QtCore import QCoreApplication
except ImportError:
    # Spyder support
    from PyQt5.QtWidgets import QMessageBox, QApplication
    from PyQt5.QtCore import QCoreApplication


def get_wordlist():
    """Currently only english for testing sorry"""
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    return [line.decode(errors='ignore') for line in response.content.splitlines()]


def create_sample_data(
        n_receipts=300, min_rows=15, max_rows=80,
        min_price=0.25, max_price=25.):
    """Imitates a dataset for shopping over the last year"""
    # List of common Attributes
    common_vedors = [f'Vendor {val:d}' for val in range(1, 11)]
    common_cats = _CATEGORIES
    words = get_wordlist()
    groups = sorted(list(_load_basic_match_data('deu')[0].keys()))

    # Generate random dates within the last year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    poss_dates = pd.date_range(start_date, end_date, freq='D')

    n_created = 0

    # Generate the data
    for _ in range(n_receipts):
        # Generate a random name from the common names list
        vendor = np.random.choice(common_vedors)

        # Generate a random number of rows for this repetition
        num_rows_repetition = np.random.randint(
            min_rows, max_rows + 1)

        n_created += num_rows_repetition
        # Generate random data
        repetition_dates = [np.random.choice(poss_dates)] * num_rows_repetition
        repetition_cat = [np.random.choice(common_cats)] * num_rows_repetition
        repetition_values = np.random.rand(num_rows_repetition) * (max_price - min_price) + min_price

        # Create the dataframe
        receipt = pd.DataFrame({'Date': repetition_dates})
        receipt['Vendor'] = vendor
        receipt['ArtNr'] = -1
        receipt['Name'] = np.random.choice(words, num_rows_repetition)
        receipt['Units'] = 1
        receipt['PricePerUnit'] = repetition_values
        receipt['Price'] = repetition_values
        receipt['TaxClass'] = 1
        receipt['Group'] = np.random.choice(groups, num_rows_repetition)
        receipt['Category'] = repetition_cat

        save_with_metadata(receipt, unique_name=True)

    logger.info(f'Create a sample dataset with {n_receipts} holding {n_created} samples')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s [%(name)s:%(filename)s:%(lineno)d] %(message)s',
    )
    logger = logging.getLogger()

    if QCoreApplication.instance() is None:
        app = QApplication(sys.argv)

    foldercheck = QMessageBox(
        QMessageBox.Warning,
        'Continue?',
        (f'Your current data folder is: {options["data_folder"]}\n\n'
         'Before you continue, please make sure that your working directory is '
         'either new and unused or set a new one. Use set_data_dir() from '
         'config tools to do so (No data will get lost if you dont but you '
         'could mess up your matching and have to clean your data folder).')
    )
    foldercheck.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort)
    sure = foldercheck.exec()

    if sure == QMessageBox.Abort:
        logger.warning('Aborting due to user request')
        sys.exit(1)

    create_sample_data()
