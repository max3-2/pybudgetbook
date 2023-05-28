"""Starts the main GUI of the tool from the inherited and customized class"""
import sys
import logging
from pathlib import Path
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon

from .main_gui_cust import main_window
from .. import _top_package

logger = logging.getLogger(_top_package)

_icon_loc = Path(__file__).parent.parent / 'img' / 'tray_icon.svg'

def start_main_ui(sys_argv=[]):
    """
    Starts the main UI. Creates the QApplication and handles some settings,
    then runs the UI.
    """
    app = QtWidgets.QApplication(sys_argv)

    if _icon_loc.exists():
        tray_icon = QIcon(str(_icon_loc))
        app.setWindowIcon(tray_icon)
    else:
        logger.warning(f'Tray icon file missing at: {_icon_loc}')

    qt_main_window = main_window()

    if _icon_loc.exists():
        qt_main_window.setWindowIcon(tray_icon)

    qt_main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start_main_ui(sys.argv)
