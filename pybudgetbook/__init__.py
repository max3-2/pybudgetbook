"""pybudgetbook main init"""
import warnings
__version__ = '0.2.0'
name = 'pybudgetbook'

_top_package = __package__

from .configs.config_tools import _check_config, load_config, _check_user_folder

# On init, check config
_check_config()
load_config()
try:
    _check_user_folder()
except (FileNotFoundError, IOError):
    warnings.warn('No user folder defined in user config or folder invalid.'
                  'Please add a folder to prevent issues using '
                  'config_tools.set_data_dir(target)!')
