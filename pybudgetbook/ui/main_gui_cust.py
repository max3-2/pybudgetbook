"""Inherits from the UI design and adapts the class with some core features"""
import logging
from PySide6 import QtWidgets

# TODO relative
import pybudgetbook.ui.ui_support as uisupport
from pybudgetbook.ui.main_gui import Ui_pybb_MainWindow
import pybudgetbook.config.plotting_conf

# This might need to be moved into init...currently it works here!
_log_formatter = logging.Formatter(
    '%(asctime)s,%(msecs)d %(levelname)-8s [%(name)s:%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d_%H:%M:%S')

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)


class main_window(Ui_pybb_MainWindow):
    """
    Todo
    """

    def __init__(self, parent):
        self.parent = parent
        self.setupUi(self.parent)

        # Logger setup
        self.qt_logstream = uisupport.QLoggingThread()
        self.qt_log_window = uisupport.QLoggingWindow(self.parent)

        self.qt_logstream.setFormatter(_log_formatter)
        self.qt_logstream.popup_lvl = logging.WARNING
        self.qt_logstream.signals.log_record_signal.connect(self.qt_log_window.catch_message)
        self.qt_log_window.new_level_signal.connect(self.qt_logstream.set_new_loglvl)
        self.qt_log_window.set_show_debug(False)
        self.qt_logstream.signals.show_log_window.connect(self.qt_log_window.show_logging_window)

        # The warnings reroute handler is added here..
        logging.getLogger('py.warnings').addHandler(self.qt_logstream)
        logger.addHandler(self.qt_logstream)

        # Custom Connections
        self.actionAbout.triggered.connect(self._about)
        self.actionShow_Logger.triggered.connect(self.qt_log_window.show_logging_window)

        # Setup plot area
        self.plot_area_receipts = uisupport.MplCanvas(
            self.frame_plotReceipt, 1, dpi=300, constrained_layout=True)

        self.plot_area_receipts.draw()
        logger.info("Created plotting area")

    def _about(self):
        """
        Build and display about box
        """
        self.about_box = QtWidgets.QMessageBox()
        self.about_box.setIcon(QtWidgets.QMessageBox.Information)

        # TODO Add dynamic version
        about_main = 'This is the about information of this UI.'
        about_sub = (
            'CR @ Whatever. Please see licensing for more details.\n'
            f'Version: {0.1}'
        )

        self.about_box.setWindowTitle('About...')
        self.about_box.setText(about_main)
        self.about_box.setDetailedText(about_sub)
        self.about_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

        self.about_box.exec()
