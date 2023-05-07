"""Contains tools to handle config read write and folder actions."""
from pathlib import Path
import shutil
import appdirs
import logging
import configparser
import json

# TODO rel. import
import pybudgetbook.config.config as bbconfig
import pybudgetbook.config.constants as bbconstants


logger = logging.getLogger(__package__)
# TODO package if its a package, else this wont work
# _config_path = Path(appdirs.user_config_dir(appname=__package__))
_config_path = Path(appdirs.user_config_dir(appname='pybudgetbook'))
_c_file = _config_path / 'pybb_conf.ini'


def _check_config():
    if not _c_file.parent.is_dir():
        _ = _c_file.parent.mkdir(parents=True)
        logger.info(f'Created new config dir at {_c_file.parent}')

    if not _c_file.is_file():
        shutil.copy2(Path(__file__).parent / 'config_template.ini', _c_file)
        logger.info(f'Created new config file at: {_c_file}')

    if _c_file.exists():
        logger.debug('Found config file')
    else:
        raise FileNotFoundError('Config file can neither be found nor created')


def _make_folder_structure(root, template):
    def one_directory(dic, path):
        for name, info in dic.items():
            next_path = path / Path(name)
            next_path.mkdir(parents=True, exist_ok=True)
            if isinstance(info, dict):
                one_directory(info, next_path)

    one_directory(template, Path(root))

    logging.info('New Folder structure created')


def _intelligent_converter(value):
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        try:
            return int(value)
        except ValueError:
            return value


def load_config(cfile=_c_file):
    """Loads the configuration from the given `.ini` file."""
    file = Path(_c_file)
    logger.debug(f'Loading configuration from "{file}".')
    cparser = configparser.ConfigParser()
    _ = cparser.read(file)

    for section in cparser.sections():
        for item, val in cparser[section].items():
            if item not in bbconfig.options:
                logger.info(f'Creating new config item on the fly: {item:s}')
            bbconfig.options[item] = _intelligent_converter(val)


def location():
    """Returns the default location of the configuration file."""
    return _c_file


def copy_group_templates(force=False):
    assert bbconfig.options['data_folder'] != 'none', 'Data directory invalid'
    # Get all files avaiable
    templates = (Path(__file__).parent.parent / 'group_templates/').glob('*.json')
    target = Path(bbconfig.options['data_folder'])
    for template in templates:
        if (target / template.name).exists() and not force:
            logger.info(f'Skipping file {str(template.name):s} - already available')
            continue

        # Negatives are copied full since there will be no active feedback
        if 'negative' in template.name:
            shutil.copy2(template, target / template.name)
        else:  # Create an empty template
            with open(template) as tmpl:
                tmpl_dict = json.load(tmpl)
            tmpl_dict = {key: [] for key in tmpl_dict.keys()}

            # And write
            with open(target / template.name, 'w') as trgt:
                json.dump(tmpl_dict, trgt, indent=4, ensure_ascii=False)

        logger.debug(f'Created new grouping template: {str(template.name):s}')


def set_data_dir(new_dir):
    cparser = configparser.ConfigParser()
    _ = cparser.read(_c_file)
    new_dir = Path(new_dir)
    assert (new_dir.exists() and new_dir.is_dir()), 'New working directory root must exist'

    cparser.set('folders', 'data_folder', str(new_dir))

    with open(_c_file, 'w') as configfile:
        cparser.write(configfile)

    bbconfig.options['data_folder'] = str(new_dir)
    _make_folder_structure(new_dir, bbconstants._FOLDER_STRUCT)
    copy_group_templates()


def set_option(name, value, persistent=True):
    """
    Sets the value of a configuration option.
    """
    if name not in bbconfig.options:
        error = f'Configuration option "{name}" does not exist.'
        logger.error(error)
        raise LookupError(error)

    bbconfig.options[name] = value
    if persistent:
        file = Path(_c_file)
        cparser = configparser.ConfigParser()
        _ = cparser.read(file)

        for section_name in cparser.sections():
            if name in cparser[section_name]:
                cparser.set(section_name, name, str(value))
                break

        with open(file, 'w') as configfile:
            cparser.write(configfile)

