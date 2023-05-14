"""Inherits from the UI design and adapts the class with some core features"""
import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
import pandas as pd
from os.path import expanduser

from .. import __version__ as bbvers
from . import ui_support
from .main_gui import Ui_pybb_MainWindow

from ..configs.plotting_conf import set_style
from ..configs import constants
from ..configs.config import options
from ..configs.config_tools import set_option

from ..receipt import Receipt, _type_check
from .. import bb_io, fuzzy_match


# This might need to be moved into init...currently it works here!
_log_formatter = logging.Formatter(
    '%(asctime)s,%(msecs)d %(levelname)-8s [%(name)s:%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d_%H:%M:%S')

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)

set_style()


def _default_data():
    init_data_viewer = pd.DataFrame(columns=constants._VIEWER_COLS)
    init_data_viewer.loc[0] = [-1, 'New Article Name', 1., 1., 1., 0, 'none']
    return init_data_viewer


class main_window(Ui_pybb_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        """
        Todo
        """
        super().__init__()
        self.setupUi(self)

        # Setup splitter default
        c_wi = self.tabWidgetPage1.width()
        self.splitter_mainPage.setSizes(
            [int(c_wi * 1 / 4), int(c_wi * 3 / 4)])

        # Additional vars
        self.receipt = None
        self.raw_text_window = None
        self._current_data = None
        self._rotate_event = None
        self._focus_event = None
        self.rotate_timer = QtCore.QTimer(self)
        self.rotate_timer.setInterval(3000)
        self.rotate_timer.setSingleShot(True)
        self.rotate_timer.stop()
        self.rotate_timer.timeout.connect(
            lambda: self.refilter_and_display(keep_lim=False))

        # Logger setup
        self.qt_logstream = ui_support.QLoggingThread()
        self.qt_log_window = ui_support.QLoggingWindow(self)

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
        self.plot_area_receipts = ui_support.MplCanvas(
            self.frame_plotReceipt, 1, constrained_layout=True)

        self.plot_area_receipts.draw_blit()
        logger.debug("Created plotting area 1")

        # Setup plot area, 2
        self.plot_area_data = ui_support.MplCanvas(
            self.frame_dataAnalysis, 2, 1, constrained_layout=False)

        self.plot_area_data.draw_blit()
        logger.debug("Created plotting area 2")

        # Create data viewer and attach to frame
        init_data_viewer = _default_data()

        table_model = ui_support.PandasTableModel(data=init_data_viewer)
        self.tableView_pandasViewer.setModel(table_model)
        poss_groups = list(bb_io._load_basic_match_data(options['lang'])[0].keys())
        self.tableView_pandasViewer.set_combo_column(7, poss_groups + ['none'])
        self.tableView_pandasViewer.model().combo_col = 7

        self.horizontalSliderFilterAmount.custom_setup(value_change_delay=500)
        self.horizontalSliderFilterAmount.slider.setValue(23)
        # Stop initial timer
        self.horizontalSliderFilterAmount.timer.stop()

        # Other configs for fields
        self.label_totalAmountDataValue.setTextFormat(Qt.RichText)
        self.comboBox_overalCat.addItems(constants._CATEGORIES + ['n.a.'])
        self.lineEdit_totalAmountReceipt.setText('0.00')
        self.lineEdit_totalAmountReceipt.setReadOnly(False)
        self.dateEdit_shopDate.setDate(QtCore.QDate.currentDate())

        self.comboBox_baseLang.addItems(constants._UI_LANG_SUPPORT)
        self.comboBox_diffParsingLang.addItems(constants._UI_LANG_SUPPORT)
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
        self.actionLogger_Popup_Level.triggered.connect(
            lambda _: ui_support.set_new_conf_val(
                self, 'logger_popup_level', 'int')
        )
        self.actionData_Directory.triggered.connect(
            lambda _: ui_support.set_new_conf_val(
                self, 'data_folder', 'dir')
        )
        self.actionDefault_Language.triggered.connect(
            lambda _: ui_support.set_new_conf_val(
                self, 'lang', 'str')
        )

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
        self.pushButton_reClassify.clicked.connect(self.re_match_data)
        self.pushButton_saveData.clicked.connect(self.save_data)
        self.comboBox_baseLang.currentTextChanged.connect(self.refilter_and_display)

        # Do some post init stuff
        self.qt_log_window.debug_state_toggle.setChecked(
            options['logger_show_debug'])
        if options['show_logger_on_start']:
            self.qt_log_window.show()
        self.qt_logstream.popup_lvl = options['logger_popup_level']

    def closeEvent(self, event):
        """Handle additional open windows"""
        if self.raw_text_window is not None:
            self.raw_text_window.close()
            self.raw_text_window = None

        super().closeEvent(event)

    def _about(self):
        """
        Build and display about box
        """
        self.about_box = QtWidgets.QMessageBox()
        self.about_box.setIcon(QtWidgets.QMessageBox.Information)

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
            self.raw_text_window = ui_support.TextDisplayWindow()

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
        file, ptn = QtWidgets.QFileDialog(self).getOpenFileName(
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
                    unsharp_ma=(5, self.horizontalSliderFilterAmount.get_scaled_val())).extract_data(
                    lang=self.comboBox_baseLang.currentText())

                # Reset events on new load
                if self._rotate_event is not None:
                    self.plot_area_receipts.canvas.mpl_disconnect(self._rotate_event)
                    self.frame_plotReceipt.setFocusPolicy(Qt.NoFocus)
                    self.plot_area_receipts.canvas.mpl_disconnect(self._focus_event)

                # Set rotate and focus events
                if self.receipt.type == 'img':
                    self._rotate_event = self.plot_area_receipts.canvas.mpl_connect(
                        'key_press_event', self.rotate_event)
                    self._focus_event = self.plot_area_receipts.canvas.mpl_connect(
                        'axes_enter_event', lambda event: self.plot_area_receipts.setFocus())

                    self.frame_plotReceipt.setFocusPolicy(Qt.StrongFocus)
                    self.plot_area_receipts.setFocus()

                elif self.receipt.type == 'pdf':
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

        self.plot_area_receipts.canvas.draw_blit()
        if self.raw_text_window is not None:
            self.raw_text_window.update_text(self.receipt.raw_text.replace('_', ' '))

    def refilter_and_display(self, keep_lim=True):
        if self.receipt is None:
            return
        self.receipt.filter_image(
            unsharp_ma=(5, self.horizontalSliderFilterAmount.get_scaled_val())).extract_data(
            lang=self.comboBox_baseLang.currentText())
        self.statusbar.showMessage('Refiltering image', timeout=2000, color='green')
        self.update_rec_plot(keep_lim)

    def update_rec_plot(self, keep_lim=True):
        current_lim = (
            self.plot_area_receipts.ax.get_xlim(),
            self.plot_area_receipts.ax.get_ylim())
        self.display_receipt()
        if keep_lim:
            self.plot_area_receipts.ax.set_xlim(current_lim[0])
            self.plot_area_receipts.ax.set_ylim(current_lim[1])

    def rotate_event(self, event, minor_step=0.1, major_step=0.5):
        if event.inaxes is self.plot_area_receipts.ax:
            if event.key == 'right':
                self.receipt.rotation = -minor_step
            elif event.key == 'left':
                self.receipt.rotation = minor_step
            elif event.key == 'shift+right':
                self.receipt.rotation = -major_step
            elif event.key == 'shift+left':
                self.receipt.rotation = major_step
            elif event.key == 'r':
                self.receipt.reset_rotation()
                self.update_rec_plot(False)
            else:
                ...

        if self.receipt.rotation is not None:
            self.comboBox_receiptDisplayMode.setCurrentIndex(0)
            self.update_rec_plot(False)
            self.rotate_timer.start()

    def set_new_data(self, new_data, has_meta=False):
        self._current_data = new_data

        # Update model
        self.tableView_pandasViewer.model().update_data(
            self._current_data.loc[:, constants._VIEWER_COLS]
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
                ui_support.convert_date(self._current_data.loc[0, 'Date']))

            if (this_cat := self._current_data.loc[0, 'Category']) in constants._CATEGORIES:
                self.comboBox_overalCat.setCurrentIndex(
                    constants._CATEGORIES.index(this_cat))
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
            try:
                diff = refval - self._current_data['Price'].sum()
            except Exception as compute_exc:
                logger.exception(f'{compute_exc}')

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

        # Get the reference lang.
        if self.checkBox_useDiffParsingLang.isChecked():
            lang = self.comboBox_diffParsingLang.currentText()
        else:
            lang = self.comboBox_baseLang.currentText()

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
                    self.receipt.set_vendor('General', lang)
                else:
                    return

            else:
                self.receipt.set_vendor(self.lineEdit_marketVendor.text(), lang)

        self.detect_date()
        new_data, total_price = self.receipt.parse_data()

        if self.checkBox_useDiffParsingLang.isChecked():
            lang = self.comboBox_diffParsingLang.currentText()
        else:
            lang = self.comboBox_baseLang.currentText()

        try:
            new_data = fuzzy_match.find_groups(new_data, lang=lang)
        except FileNotFoundError as missing_data:
            logger.error(f'{missing_data}')
            new_data['Group'] = 'none'

        self.set_new_data(new_data)
        self.lineEdit_totalAmountReceipt.setText(f'{total_price:.2f}')
        self.update_diff(total_price)
        self.plot_area_receipts.canvas.draw_blit()

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

        self.dateEdit_shopDate.setDate(ui_support.convert_date(rec_date))
        self.statusbar.showMessage('Date extracted', timeout=2000, color='green')

    def detect_vendor(self):
        if self.receipt is None:
            msg = 'Please load a receipt first'
            logger.info(msg)
            self.statusbar.showMessage(msg, timeout=3000)
            return

        if self.checkBox_useDiffParsingLang.isChecked():
            lang = self.comboBox_diffParsingLang.currentText()
        else:
            lang = self.comboBox_baseLang.currentText()

        vendor = self.receipt.parse_vendor(lang)
        self.lineEdit_marketVendor.setText(vendor)
        self.statusbar.showMessage('Vendor extracted', timeout=2000, color='green')

    def re_match_data(self):
        if self.tableView_pandasViewer.model().rowCount() > 0:
            data = self.tableView_pandasViewer.get_final_data()

        else:
            return

        if self.checkBox_useDiffParsingLang.isChecked():
            lang = self.comboBox_diffParsingLang.currentText()
        else:
            lang = self.comboBox_baseLang.currentText()

        try:
            data = fuzzy_match.find_groups(data, lang=lang)
        except FileNotFoundError as missing_data:
            logger.error(f'{missing_data}')
            data['Group'] = 'none'

        self.set_new_data(data)

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
        retrieved_data['Date'] = ui_support.convert_date(self.dateEdit_shopDate.date())
        try:
            total_ext = float(self.lineEdit_totalAmountReceipt.text())
        except ValueError:
            total_ext = 0
        metadata = {'tags': self.lineEdit_tags.text(),
                    'total_extracted': total_ext}
        retrieved_data.attrs = metadata
        retrieved_data = bb_io.resort_data(retrieved_data)

        if self.checkBox_feedbackMatch.isChecked():
            if self.checkBox_useDiffParsingLang.isChecked():
                lang = self.comboBox_diffParsingLang.currentText()
            else:
                lang = self.comboBox_baseLang.currentText()
            fuzzy_match.matcher_feedback(retrieved_data, lang)

        if self.receipt is None:
            if options['ask_for_image']:
                file, _ = QtWidgets.QFileDialog().getOpenFileName(
                    parent=self, caption='Select Image File',
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
                                 unique_name=options['generate_unique_name'],
                                 move_on_save=options['move_on_save'])

        dialog = ui_support.CustomFadeDialog(self, text='Receipt Saved Successful')
        dialog.show()

        self.set_new_data(_default_data())
