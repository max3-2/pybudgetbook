"""Manages folder structure of data folder and IO of data"""
from pathlib import Path
import logging
import json
import pandas as pd
import h5py
import warnings

# TODO MAKE RELATIVE
import pybudgetbook.config.config as bbconfig


logger = logging.getLogger(__package__)


def load_user_match_data(lang):
    """Loads user only match data"""
    user_data = Path(bbconfig.options['data_folder']) / f'item_groups_{lang:s}.json'

    if not user_data.is_file():
        error = (f'No matching data for {lang:s} in user folder, please '
                 'create template to enable feedback of data.')
        logger.error(error)
        raise FileNotFoundError(error)

    else:
        with open(user_data) as udd:
            result = json.load(udd)

    return result, user_data


def _save_user_match_data(data, target):
    """Saves user match data"""
    if not target.is_file():
        logger.info('No matching data for in user folder, new file '
                    'will be created.')

    with open(target, 'w') as udd:
        json.dump(data, udd, indent=4, ensure_ascii=False)


def load_basic_match_data(lang):
    """Loads basic only match data"""
    basic_data = Path(__file__).parent / 'group_templates' / f'item_groups_{lang:s}.json'

    if not basic_data.is_file():
        error = (f'No matching data for {lang:s} delivered with package, please '
                 'create PR if needed.')
        logger.error(error)
        raise FileNotFoundError(error)

    else:
        with open(basic_data) as bdd:
            result = json.load(bdd)

    return result, basic_data


def load_negative_match_data(lang):
    """Loads negative group match data for a given language"""
    neg_data = Path(bbconfig.options['data_folder']) / f'negative_match_{lang:s}.json'

    if not neg_data.is_file():
        error = (f'No negative match data found for {lang:s}, please check '
                 'data folder or recopy templates')
        logger.error(error)
        raise FileNotFoundError(error)

    else:
        with open(neg_data) as ndd:
            result = json.load(ndd)['neg_match_data']

    return result


def load_group_match_data(lang):
    """
    Load and merge match data from different locations.

    Parameters
    ----------
    lang : TYPE
        DESCRIPTION.

    Raises
    ------
    FileNotFoundError
        DESCRIPTION.

    Returns
    -------
    result : TYPE
        DESCRIPTION.

    """
    basic_data = Path(__file__).parent / 'group_templates' / f'item_groups_{lang:s}.json'
    user_data = Path(bbconfig.options['data_folder']) / f'item_groups_{lang:s}.json'

    if not basic_data.is_file() and not user_data.is_file():
        error = ('Neither basic package matching data nor user matching data '
                 f'found for language {lang:s}')
        logger.error(error)
        raise FileNotFoundError(error)

    if not basic_data.is_file():
        logger.warning(f'No matching data for {lang:s} included with package')
        with open(user_data) as udd:
            result = json.load(udd)

    elif not user_data.is_file():
        logger.warning(f'No matching data for {lang:s} in user folder')
        with open(basic_data) as bdd:
            result = json.load(bdd)

    else:
        with open(basic_data) as bdd:
            bd = json.load(bdd)

        with open(user_data) as udd:
            ud = json.load(udd)

        result = dict()
        for key in ud.keys():
            if key in bd:
                result[key] = list(set(ud[key].copy()).union(set(bd[key].copy())))
            else:
                result[key] = ud[key].copy()
        for key in bd:
            if key not in result:
                result[key] = bd[key].copy()

    return result


def _concatenate_to_main(dataframe, work_dir):
    """
    Loads main dataset and concatenates the new data to the main. Saves the
    main to have a single growing source of data for easy analysis. Metadata
    is lost in this case but kept for single data dataframes
    """
    ...


def save_with_metadata(dataframe, target=None, img_path=None):
    """
    Target is a path in this case, which will create a new hdf store with the
    pandas dataframe and metadata attached to the dataframe.
    """
    if target is None:
        year = dataframe.loc[0, 'Date'].strftime('%Y')
        mon_day = dataframe.loc[0, 'Date'].strftime('%m_%d')

        target = Path(bbconfig.options['data_folder']) / 'data' / year
        if not target.exists() or not target.is_dir():
            target.mkdir(parents=True, exist_ok=True)

        target = target / f'{mon_day:s}_{dataframe.loc[0, "Vendor"]:s}.hdf5'

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        dataframe.to_hdf(target, 'receipt', 'w')

        with h5py.File(target, 'a') as hdfstore:
            # rec_grp = hdfstore['receipt']
            for name, val in dataframe.attrs.items():
                hdfstore.attrs.create(name, val)


def load_with_metadata(source):
    """
    Source is a path in this case, which will load the hdf store with the
    pandas dataframe and metadata and attach the metadata to the dataframe.
    """
    receipt = pd.read_hdf(source)
    with h5py.File(source) as hdfstore:
        att_dict = dict()
        for key, val in hdfstore.attrs.items():
            if not key.isupper():
                att_dict[key] = val

    receipt.attrs = att_dict

    return receipt
