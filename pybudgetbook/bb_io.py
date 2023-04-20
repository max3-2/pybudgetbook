"""Manages folder structure of data folder and IO of data"""
from pathlib import Path
import logging
import json

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


def _housekeep_new_data(img_path, data_path):
    """
    Housekeeping for valid new data, moves the images and the dataframe to data
    folder.
    """


def _concatenate_to_main(dataframe, work_dir):
    """
    Loads main dataset and concatenates the new data to the main. Saves the
    main to have a single growing source of data for easy analysis. Metadata
    is lost in this case but kept for single data dataframes
    """
    ...


def save_with_metadata(dataframe, target):
    """
    Target is a path in this case, which will create a new hdf store with the
    pandas dataframe and metadata attached to the dataframe.
    """
    ...


def load_with_metadata(source):
    """
    Source is a path in this case, which will load the hdf store with the
    pandas dataframe and metadata and attach the metadata to the dataframe.
    """
    ...
