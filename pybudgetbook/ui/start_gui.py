"""Starts the main GUI of the tool from the inherited and customized class"""
import sys
from PySide6 import QtWidgets

# TODO make package
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pybudgetbook.ui.main_gui_cust import main_window



def start_main_ui(sys_argv=[]):
    app = QtWidgets.QApplication(sys_argv)
    qt_main_window = QtWidgets.QMainWindow()
    _ = main_window(qt_main_window)

    qt_main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start_main_ui(sys.argv)
