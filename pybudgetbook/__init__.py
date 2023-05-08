"""pybudgetbook main init"""
__version__ = '0.2.0'
__name__ = 'pybudgetbook'

from pybudgetbook.config.config_tools import _check_config, load_config

# On init, check config
_check_config()
load_config()
