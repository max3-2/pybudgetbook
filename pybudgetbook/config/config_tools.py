"""Contains tools to handle config read write and folder actions."""
from pathlib import Path
import shutil
import appdirs
import logging

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
