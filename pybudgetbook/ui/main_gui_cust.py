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
from pybudgetbook.receipt import Receipt, _type_check
from pybudgetbook import bb_io, fuzzy_match
from pybudgetbook.config.config import options
from pybudgetbook.config.config_tools import set_option

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
        self._current_data = None

        # Logger setup
        self.qt_logstream = uisupport.QLoggingThread()
        self.qt_log_window = uisupport.QLoggingWindow(self.parent)

        self.qt_logstream.setFormatter(_log_formatter)
        self.qt_logstream.popup_lvl = logging.WARNING
        self.qt_logstream.signals.log_record_signal.connect(self.qt_log_window.catch_message)
        self.qt_log_window.new_level_signal.connect(self.qt_logstream.set_new_loglvl)
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
        init_data_viewer = pd.DataFrame(columns=bbconstant._VIEWER_COLS)
        init_data_viewer.loc[0] = [0, 'New Article Name', 1., 1., 1., 0, 'none']

        table_model = uisupport.PandasTableModel(data=init_data_viewer)
        self.tableView_pandasViewer.setModel(table_model)
        poss_groups = list(bb_io.load_basic_match_data(options['lang'])[0].keys())
        self.tableView_pandasViewer.set_combo_column(7, poss_groups + ['none'])
        self.tableView_pandasViewer.model().combo_col = 7

        self.horizontalSliderFilterAmount.custom_setup(value_change_delay=500)
        self.horizontalSliderFilterAmount.slider.setValue(17)
        # Stop initial timer
        self.horizontalSliderFilterAmount.timer.stop()

        # Other configs for fields
        self.label_totalAmountDataValue.setTextFormat(Qt.RichText)
        self.comboBox_overalCat.addItems(bbconstant._CATEGORIES + ['n.a.'])
        self.lineEdit_totalAmountReceipt.setText('0.00')
        self.lineEdit_totalAmountReceipt.setReadOnly(False)
        self.dateEdit_shopDate.setDate(QtCore.QDate.currentDate())

        self.comboBox_baseLang.addItems(bbconstant._UI_LANG_SUPPORT)
        self.comboBox_diffParsingLang.addItems(bbconstant._UI_LANG_SUPPORT)
        index = self.comboBox_baseLang.findText(options['lang'])
        if index != -1:
            self.comboBox_baseLang.setCurrentIndex(index)
            self.comboBox_diffParsingLang.setCurrentIndex(index)

        # Set all values from the persistent config to UI checks
        self.actionMove_on_Save.setChecked(options['move_on_save'])
        self.actionGenerate_Unique_Name.setChecked(options['generate_unique_name'])
        self.actionAlways_Ask_for_Image.setChecked(options['ask_for_image'])
        self.actionShow_Logger_on_Start.setChecked(options['show_logger_on_start'])
        self.actionLogger_debug.setChecked(options['logger_show_debug'])

        # Attach menu handlers
        self.actionMove_on_Save.toggled.connect(
            lambda new_val: set_option('move_on_save', new_val)
        )
        self.actionGenerate_Unique_Name.toggled.connect(
            lambda new_val: set_option('generate_unique_name', new_val)
        )
        self.actionAlways_Ask_for_Image.toggled.connect(
            lambda new_val: set_option('ask_for_image', new_val)
        )
        self.actionShow_Logger_on_Start.toggled.connect(
            lambda new_val: set_option('show_logger_on_start', new_val)
        )
        self.actionLogger_debug.toggled.connect(
            lambda new_val: set_option('logger_show_debug', new_val)
        )

        # Attach all the handlers for custom functions
        self.pushButton_loadNewReceipt.clicked.connect(self.load_receipt)
        self.horizontalSliderFilterAmount.set_timer_callback(self.refilter_and_display)
        self.comboBox_receiptDisplayMode.currentIndexChanged.connect(self.update_rec_plot)
        self.checkBox_useDiffParsingLang.stateChanged.connect(self.comboBox_diffParsingLang.setEnabled)
        self.actionRaw_Text.triggered.connect(self.show_raw_text)
        self.tableView_pandasViewer.model().dataChanged.connect(self.recompute_diff)
        self.pushButton_detectVendor.clicked.connect(self.detect_vendor)
        self.pushButton_parseData.clicked.connect(self.parse_data)
        self.lineEdit_totalAmountReceipt.textChanged.connect(self.update_diff)
        self.pushButton_saveData.clicked.connect(self.save_data)

        # Do some post init stuff
        self.qt_log_window.debug_state_toggle.setChecked(
            options['logger_show_debug'])
        if options['show_logger_on_start']:
            self.qt_log_window.show()

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

        if self.receipt is None:
            self.raw_text_window.update_text('')
        else:
            self.raw_text_window.update_text(self.receipt.raw_text.replace('_', ' '))

        self.raw_text_window.show()
        self.raw_text_window.raise_()
        self.raw_text_window.closed.connect(self.on_text_window_closed)

    def on_text_window_closed(self):
        self.raw_text_window = None

    def load_receipt(self):
        file, ptn = QtWidgets.QFileDialog(self.parent).getOpenFileName(
            caption='Select a receipt file',
            dir=expanduser('~'),
            filter=('Valid files (*.pdf *.png *.PNG *.jpeg *.JPEG *.jpg *.JPG);;'
                    'Parsed Receipt (*.h5 *.hdf *.hdf5);;'
                    'FreeForAll (*.*)')
        )
        if file and Path(file).exists():
            self.statusbar.showMessage('New receipt loaded', 2000, color='green')
        else:
            self.statusbar.showMessage('Invalid File', 3000, color='red')
            return

        if 'hdf' in ptn or 'h5' in ptn or 'hdf5' in ptn:
            logger.info('Loading a parsed receipt')
            try:
                self.set_new_data(bb_io.load_with_metadata(file), has_meta=True)

            except Exception as ioe:
                logger.exception(f"Can't load file: {ioe:s}")
                return
        else:
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
        self.receipt.disp_ax = self.plot_area_receipts.ax
        self.display_receipt()

    def display_receipt(self):
        if self.receipt is None:
            return
        if self.comboBox_receiptDisplayMode.currentIndex() == 0:
            self.plot_area_receipts.ax.imshow(self.receipt.image)
        else:
            self.plot_area_receipts.ax.imshow(self.receipt.bin_img)

        self.plot_area_receipts.canvas.draw()
        if self.raw_text_window is not None:
            self.raw_text_window.update_text(self.receipt.raw_text.replace('_', ' '))

    def refilter_and_display(self):
        if self.receipt is None:
            return
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

    def set_new_data(self, new_data, has_meta=False):
        self._current_data = new_data

        # Update model
        self.tableView_pandasViewer.model().update_data(
                    self._current_data.loc[:, bbconstant._VIEWER_COLS]
                )
        self.tableView_pandasViewer.resizeColumnsToContents()
        self.tableView_pandasViewer.scrollToTop()

        # Update fields
        if has_meta:
            self.lineEdit_marketVendor.setText(self._current_data.loc[0, 'Vendor'])
            total = self._current_data.attrs.get("total_extracted", 0)
            self.lineEdit_totalAmountReceipt.setText(
                f'{total:.2f}')
            self.update_diff(total)

            self.dateEdit_shopDate.setDate(
                uisupport.convert_date(self._current_data.loc[0, 'Date']))

            if (this_cat := self._current_data.loc[0, 'Category']) in bbconstant._CATEGORIES:
                self.comboBox_overalCat.setCurrentIndex(
                    bbconstant._CATEGORIES.index(this_cat))
            else:
                self.comboBox_overalCat.setCurrentIndex(
                    self.comboBox_overalCat.findText('n.a.'))

    def update_diff(self, refval, baseval=None):
        try:
            refval = float(refval)
        except ValueError:
            logger.warning('Cant convert this new total price to float!')
            return

        if baseval is None:
            if self._current_data is None:
                return ''

            diff = refval - self._current_data['Price'].sum()
        else:
            diff = refval - baseval

        if abs(diff) > 0.05:
            color = 'red'
        elif diff == 0:
            color = 'green'
        else:
            color = 'black'

        self.label_totalAmountDataValue.setText(
            f'<font color="{color:s}">{diff:.2f}</font>')

    def recompute_diff(self, index1, index2, *args):
        col1, col2 = index1.column(), index2.column()
        if col1 == 5 or col2 == 5:
            self.update_diff(
                float(self.lineEdit_totalAmountReceipt.text()),
                self.tableView_pandasViewer.model()._data['Price'].sum()
            )

    def parse_data(self):
        if self.receipt is None:
            msg = 'Please load a receipt first'
            logger.info(msg)
            self.statusbar.showMessage(msg, timeout=3000)
            return

        if self.receipt.vendor is None:
            if self.lineEdit_marketVendor.text() == '':
                msg_box = QtWidgets.QMessageBox()
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setText(
                    'No vendor in receipt and no vendor added - this will default '
                    'to a general pattern set - continue?')
                msg_box.setWindowTitle('Vendor warning')
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                msg_box.setDefaultButton(QtWidgets.QMessageBox.No)

                if msg_box.exec() == QtWidgets.QMessageBox.Yes:
                    # TODO add lang support
                    self.receipt.set_vendor('General')
                else:
                    return

            else:
                self.receipt.set_vendor(self.lineEdit_marketVendor.text())

        self.detect_date()
        new_data, total_price = self.receipt.parse_data()
        new_data = fuzzy_match.find_groups(new_data)
        self.set_new_data(new_data)
        self.lineEdit_totalAmountReceipt.setText(f'{total_price:.2f}')
        self.update_diff(total_price)
        self.plot_area_receipts.canvas.draw()

    def detect_date(self):
        if self.receipt is None:
            msg = 'Please load a receipt first'
            logger.info(msg)
            self.statusbar.showMessage(msg, timeout=3000)
            return

        rec_date = self.receipt.parse_date()
        if rec_date is None:
            msg = 'No Date could be extracted'
            logger.info(msg)
            self.statusbar.showMessage(msg, timetout=3000)
            return

        self.dateEdit_shopDate.setDate(uisupport.convert_date(rec_date))
        self.statusbar.showMessage('Date extracted', timeout=2000, color='green')

    def detect_vendor(self):
        if self.receipt is None:
            msg = 'Please load a receipt first'
            logger.info(msg)
            self.statusbar.showMessage(msg, timeout=3000)
            return

        vendor = self.receipt.parse_vendor()
        self.lineEdit_marketVendor.setText(vendor)
        self.statusbar.showMessage('Vendor extracted', timeout=2000, color='green')

    def save_data(self):
        if (self.lineEdit_marketVendor.text() == 'General' or
            self.lineEdit_marketVendor.text() == ''):
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setText(
                'No vendor specified or just General - this is not optimal for '
                'archiving. It is recommended to add a vendor!')
            msg_box.setWindowTitle('Vendor warning')
            continueButton = QtWidgets.QPushButton("Continue")
            abortButton = QtWidgets.QPushButton("Abort")
            msg_box.addButton(continueButton, QtWidgets.QMessageBox.YesRole)
            msg_box.addButton(abortButton, QtWidgets.QMessageBox.NoRole)
            choice = msg_box.exec()
            if choice == QtWidgets.QMessageBox.NoRole.value:
                return

        retrieved_data = self.tableView_pandasViewer.get_final_data()
        retrieved_data = _type_check(retrieved_data)
        retrieved_data['Category'] = self.comboBox_overalCat.currentText()
        retrieved_data['Vendor'] = self.lineEdit_marketVendor.text()
        retrieved_data['Date'] = uisupport.convert_date(self.dateEdit_shopDate.date())
        try:
            total_ext = float(self.lineEdit_totalAmountReceipt.text())
        except ValueError:
            total_ext = 0
        metadata = {'tags': self.lineEdit_tags.text(),
                    'total_extracted': total_ext}
        retrieved_data.attrs = metadata
        retrieved_data = bb_io.resort_data(retrieved_data)
        if self.checkBox_feedbackMatch.isChecked():
            fuzzy_match.matcher_feedback(retrieved_data)

        if self.receipt is None:
            if options['ask_for_image']:
                file, _ = QtWidgets.QFileDialog().getOpenFileName(
                    parent=self.parent, caption='Select Image File',
                    dir=expanduser('~'),
                    filter=('Valid files (*.pdf *.png *.PNG *.jpeg *.JPEG *.jpg *.JPG)')
                )
                if not file:
                    logger.error('Cant save without valid image if option is set!')
                    return
                else:
                    this_img = Path(file)
            else:
                this_img = None
        else:
            this_img = self.receipt.file

        bb_io.save_with_metadata(retrieved_data, img_path=this_img,
                                 unique_name=options['generate_unique_name'])