"""Inherits from the UI design and adapts the class with some core features"""
import logging
from PySide6 import QtWidgets
import pandas as pd
from copy import copy

# TODO relative and change plot import
import pybudgetbook.ui.ui_support as uisupport
from pybudgetbook.ui.main_gui import Ui_pybb_MainWindow
import pybudgetbook.config.plotting_conf
import pybudgetbook.config.constants as bbconstant

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

        # Setup plot area, 1
        self.plot_area_receipts = uisupport.MplCanvas(
            self.frame_plotReceipt, 1, constrained_layout=True)

        self.plot_area_receipts.draw()
        logger.debug("Created plotting area 1")

        # Setup plot area, 2
        self.plot_area_data = uisupport.MplCanvas(
            self.frame_dataAnalysis, 2, 1, constrained_layout=False)

        self.plot_area_data.draw()
        logger.debug("Created plotting area 2")

        # Create data viewer and attach to frame, TODO
        viewer_cols = list(copy(bbconstant._MANDATORY_COLS))
        viewer_cols.remove('Vendor')
        viewer_cols.remove('Date')
        viewer_cols.remove('Category')
        init_data_viewer = pd.DataFrame(columns=viewer_cols)
        init_data_viewer.loc[0] = [0, 'New Article Name', 1, 1, 1, 0, 'none']
        
        
        table_model = uisupport.PandasTableModel(data=init_data_viewer)
        self.tableView_pandasViewer.setModel(table_model)
        self.tableView_pandasViewer.set_combo_column(7, ["test1", "test2"])

        self.horizontalSliderFilterAmount.custom_setup()

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
