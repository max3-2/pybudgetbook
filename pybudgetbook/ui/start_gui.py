"""Starts the main GUI of the tool from the inherited and customized class"""
import sys
import logging
from pathlib import Path
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon

from .main_gui_cust import main_window


logger = logging.getLogger(__package__)


def start_main_ui(sys_argv=[]):
    app = QtWidgets.QApplication(sys_argv)
    app.setStyle('Light')

    icon = Path('img/tray_icon.svg')
    if icon.exists():
        tray_icon = QIcon(str(icon))
        app.setWindowIcon(tray_icon)
    else:
        logger.warning('Tray icon file missing')

    qt_main_window = main_window()

    qt_main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start_main_ui(sys.argv)
