"""Manages folder structure of data folder and IO of data"""
from pathlib import Path
import logging
import json

# TODO MAKE RELATIVE
import pybudgetbook.config.constants as bbconstant
import pybudgetbook.config.config as bbconfig


logger = logging.getLogger(__package__)


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
    ...


def save_with_metadata(dataframe):
    # TODO ideas are tags,
    ...


def load_with_metadata(dataframe):
    ...
