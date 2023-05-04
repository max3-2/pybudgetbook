"""Inherits from the UI design and adapts the class with some core features"""
import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
import pandas as pd
from copy import copy
from os.path import expanduser

# TODO relative and change plot import
import pybudgetbook.ui.ui_support as uisupport
from pybudgetbook.ui.main_gui import Ui_pybb_MainWindow
from pybudgetbook.config.plotting_conf import set_style
import pybudgetbook.config.constants as bbconstant
from pybudgetbook import __version__ as bbvers
from pybudgetbook.receipt import Receipt

# This might need to be moved into init...currently it works here!
_log_formatter = logging.Formatter(
    '%(asctime)s,%(msecs)d %(levelname)-8s [%(name)s:%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d_%H:%M:%S')

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)
set_style()

class main_window(Ui_pybb_MainWindow):
    """
    Todo
    """

    def __init__(self, parent):
        self.parent = parent
        self.setupUi(self.parent)

        # Additional vars
        self.receipt = None
        self.raw_text_window = None

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

        # Create data viewer and attach to frame
        # TODO change Column setup with new constant
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
        self.horizontalSliderFilterAmount.slider.setValue(13)
        # Stop initial timer
        self.horizontalSliderFilterAmount.timer.stop()

        # Other configs for fields
        self.label_totalAmountDataValue.setTextFormat(Qt.RichText)

        # Attach all the handlers for custom functions
        self.pushButton_loadNewReceipt.clicked.connect(self.load_receipt)
        self.horizontalSliderFilterAmount.set_timer_callback(self.refilter_and_display)
        self.comboBox_receiptDisplayMode.currentIndexChanged.connect(self.update_rec_plot)
        self.checkBox_useDiffParsingLang.stateChanged.connect(self.comboBox_diffParsingLang.setEnabled)
        self.actionRaw_Text.triggered.connect(self.show_raw_text)

    def _about(self):
        """
        Build and display about box
        """
        self.about_box = QtWidgets.QMessageBox()
        self.about_box.setIcon(QtWidgets.QMessageBox.Information)

        # TODO Add dynamic version
        about_main = ('PyBudgetbook UI. Use to scan and categorize your '
                      'receipts.')
        about_sub = (
            'CR @ M. Elfner. MIT license.\n Have fun, report issues and '
            'improve!\n'
            f'Version: {bbvers}'
        )

        self.about_box.setWindowTitle('About...')
        self.about_box.setText(about_main)
        self.about_box.setDetailedText(about_sub)
        self.about_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

        self.about_box.exec()

    def show_raw_text(self):
        if self.raw_text_window is None:
            self.raw_text_window = uisupport.TextDisplayWindow()
            self.raw_text_window.closed.connect(self.on_text_window_closed)

        if self.receipt is None:
            self.raw_text_window.update_text('')
        else:
            self.raw_text_window.update_text(self.receipt.raw_text.replace('_', ' '))

        self.raw_text_window.show()
        self.raw_text_window.raise_()

    def on_text_window_closed(self):
        self.raw_text_window = None

    def load_receipt(self):
        file, ok = QtWidgets.QFileDialog(self.parent).getOpenFileName(
            caption='Select a receipt file',
            dir=expanduser('~'),
            filter=('Valid files (*.pdf *.png *.PNG *.jpeg *.JPEG *.jpg *.JPG);;'
                    'FreeForAll (*.*)')
        )
        if file and Path(file).exists():
            self.statusbar.showMessage('New receipt loaded', 2000, color='green')
        else:
            self.statusbar.showMessage('Invalid File', 3000, color='red')
            return

        try:
            self.receipt = Receipt(file)
            self.receipt.filter_image(
                unsharp_ma=(5, self.horizontalSliderFilterAmount.get_scaled_val())).extract_data()
            if self.receipt.type == 'pdf':
                self.horizontalSliderFilterAmount.setEnabled(False)
                self.comboBox_receiptDisplayMode.setEnabled(False)

        except (IOError, FileNotFoundError):
            logger.warning('Invalid file type for a new receipt!')
            return

        self.comboBox_receiptDisplayMode.setCurrentIndex(0)
        self.display_receipt()

    def display_receipt(self):
        if self.receipt is None:
            return
        if self.comboBox_receiptDisplayMode.currentIndex() == 0:
            self.plot_area_receipts.ax.imshow(self.receipt.image)
        else:
            self.plot_area_receipts.ax.imshow(self.receipt.bin_img)

        self.plot_area_receipts.canvas.draw()

    def refilter_and_display(self):
        self.receipt.filter_image(
            unsharp_ma=(5, self.horizontalSliderFilterAmount.get_scaled_val())).extract_data()
        self.statusbar.showMessage('Refiltering image', timeout=2000, color='green')
        self.update_rec_plot()

    def update_rec_plot(self):
        current_lim = (
            self.plot_area_receipts.ax.get_xlim(),
            self.plot_area_receipts.ax.get_ylim())
        self.display_receipt()
        self.plot_area_receipts.ax.set_xlim(current_lim[0])
        self.plot_area_receipts.ax.set_ylim(current_lim[1])
