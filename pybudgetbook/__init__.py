"""pybudgetbook main init"""
__version__ = '0.2.0'
name = 'pybudgetbook'

_top_package = __package__

from .configs.config_tools import _check_config, load_config

# On init, check config
_check_config()
load_config()
