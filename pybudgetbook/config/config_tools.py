"""Contains tools to handle config read write and folder actions."""
from pathlib import Path
import shutil
import appdirs
import logging
import configparser

# TODO rel. import
import pybudgetbook.config.config as bbconfig


# TODO dynamic app name
logger = logging.getLogger(__name__)
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
            bbconfig.options[item] = val


def location():
    """Returns the default location of the configuration file."""
    return _c_file


def set_data_dir(new_dir):
    cparser = configparser.ConfigParser()
    _ = cparser.read(_c_file)
    new_dir = Path(new_dir)
    assert (new_dir.exists() and new_dir.is_dir()), 'New working directory root must exist'

    cparser.set('folders', 'data_folder', str(new_dir))

    with open(_c_file, 'w') as configfile:
        cparser.write(configfile)

    bbconfig.options['data_folder'] = str(new_dir)


# TODO add general flag changer
# def option(section=None, name=None, value=None):
#     """
#     Sets or returns the value of a configuration option.

#     If called without arguments, returns all configuration options as
#     a dictionary. Returns an option's value if only called with the
#     option's `name`. Otherwise sets the option to the given `value`.
#     """
#     if name is None:
#         return options

#     if name not in options:
#         error = f'Configuration option "{name}" does not exist.'
#         log.error(error)
#         raise LookupError(error)

#     if value is None:
#         return options[name]
#     else:
#         options[name] = value
