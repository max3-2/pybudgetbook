"""Inherits from the UI design and adapts the class with some core features"""
import logging
from pathlib import Path
from os.path import expanduser
from shutil import make_archive
import datetime

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt

import pandas as pd
import numpy as np

from .. import __version__ as bbvers
from . import ui_support
from .main_gui import Ui_pybb_MainWindow

from .. import plotting
from ..configs import constants
from ..configs.config import options
from ..configs.config_tools import set_option, _check_user_folder, set_data_dir

from ..receipt import Receipt, _type_check
from .. import bb_io, fuzzy_match, parsers
from .. import _top_package

# This might need to be moved into init...currently it works here!
_log_formatter = logging.Formatter(
    '%(asctime)s,%(msecs)d %(levelname)-8s [%(name)s:%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d_%H:%M:%S')


logger = logging.getLogger(_top_package)
logger.setLevel(logging.DEBUG)

plotting.set_style()


def _default_data():
    """Default data for first row in data viewer and new row template."""
    init_data_viewer = pd.DataFrame(columns=constants._VIEWER_COLS)
    init_data_viewer.loc[0] = [-1, 'New Article Name', 1., 1., 1., 0, 'none']
    return init_data_viewer


class main_window(Ui_pybb_MainWindow, QtWidgets.QMainWindow):
    """
    Creates the main window that handles all UI tasks. The window design is
    created in designer and the inherited as base class.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

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

        self.conc_data = None
        self.pieplot = None
        self.piehandler = None

        # Logger setup
        self.qt_logstream = ui_support.QLoggingThread()
        self.qt_log_window = ui_support.QLoggingWindow(self)

        self.qt_logstream.setFormatter(_log_formatter)
        self.qt_logstream.popup_lvl = options['logger_popup_level']
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
        self.plot_area_receipts.ax.grid(True)

        self.plot_area_receipts.draw_blit()
        # logger.debug("Created plotting area 1")

        # Setup plot area, 2
        self.plot_area_data = ui_support.MplCanvas(
            self.frame_dataAnalysis, no_ax=True, constrained_layout=False)

        self.plot_area_data.draw_blit()
        # logger.debug("Created plotting area 2")

        # Create data viewer and attach to frame
        init_data_viewer = _default_data()

        table_model = ui_support.PandasTableModel(data=init_data_viewer)
        self.tableView_pandasViewer.setModel(table_model)
        self.set_group_options(sender=-1)
        self.tableView_pandasViewer.model().combo_col = 7

        self.slider_FilterAmount.custom_setup(value_change_delay=500)
        self.slider_FilterAmount.slider.setValue(23)
        # Stop initial timer
        self.slider_FilterAmount.timer.stop()
        # Hide label
        self.slider_FilterAmount._remove_label()

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
        self.actionCurrency.triggered.connect(
            lambda _: ui_support.set_new_conf_val(
                self, 'currency', 'str')
        )

        # Layout button bar tab data left
        self.frame_buttonsMainLeft.layout().setAlignment(Qt.AlignTop)
        # Center all
        for widget in [
            self.frame_buttonsMainLeft.layout().itemAt(i)
            for i in range(self.frame_buttonsMainLeft.layout().count())]:
            self.frame_buttonsMainLeft.layout().setAlignment(
                widget.widget(), Qt.AlignHCenter)

        # Layout button bar tab data right
        self.frame_buttonsMainRight.layout().setAlignment(Qt.AlignTop)
        # Center all
        for widget in [
            self.frame_buttonsMainRight.layout().itemAt(i)
            for i in range(self.frame_buttonsMainRight.layout().count())]:
            self.frame_buttonsMainRight.layout().setAlignment(
                widget.widget(), Qt.AlignHCenter)

        # Configure second tab: Plotting
        self.frame_plotButtonbar.layout().setAlignment(Qt.AlignTop)
        # Center all
        for widget in [
            self.frame_plotButtonbar.layout().itemAt(i)
            for i in range(self.frame_plotButtonbar.layout().count())]:
            self.frame_plotButtonbar.layout().setAlignment(
                widget.widget(), Qt.AlignHCenter)

        self.comboBox_PiePlotType.addItems(
            ['Vendors', 'Categories', 'Groups'])

        # Add modern buttons
        self.modernButton_loadReceipt.set_scaled_icon_and_text(
            'load_rec.png', 'Load'
        )

        self.modernButton_detectVendor.set_scaled_icon_and_text(
            'parse_vendor.png', 'Vendor'
        )
        self.modernButton_parseData.set_scaled_icon_and_text(
            'parse_data.png', 'Parse'
        )
        self.modernButton_addRow.set_scaled_icon_and_text(
            'add_row.png', 'Add'
        )
        self.modernButton_classData.set_scaled_icon_and_text(
            'classify.png', 'Group'
        )
        self.modernButton_fillData.set_scaled_icon_and_text(
            'fill_data.png', 'Fill'
        )
        self.modernButton_saveData.set_scaled_icon_and_text(
            'save.png', 'Save'
        )

        self.modernButton_loadPlotData.set_scaled_icon_and_text(
            'reload_data.png', 'Load'
        )
        self.modernButton_plotStem.set_scaled_icon_and_text(
            'stem.png', 'Plot Stem'
        )
        self.modernButton_plotPie.set_scaled_icon_and_text(
            'pie.png', 'Plot Pie'
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
        self.modernButton_loadReceipt.clicked.connect(self.load_receipt)
        self.slider_FilterAmount.set_timer_callback(self.refilter_and_display)
        self.comboBox_receiptDisplayMode.currentIndexChanged.connect(self.update_rec_plot)
        self.checkBox_useDiffParsingLang.stateChanged.connect(self.comboBox_diffParsingLang.setEnabled)
        self.actionRaw_Text.triggered.connect(self.show_raw_text)
        self.tableView_pandasViewer.model().dataChanged.connect(self.recompute_diff)
        self.modernButton_detectVendor.clicked.connect(self.detect_vendor)
        self.modernButton_parseData.clicked.connect(self.parse_data)
        self.lineEdit_totalAmountReceipt.textChanged.connect(self.update_diff)
        self.modernButton_classData.clicked.connect(self.re_match_data)
        self.modernButton_fillData.clicked.connect(self.refill_data)
        self.modernButton_saveData.clicked.connect(self.save_data)
        self.comboBox_baseLang.currentTextChanged.connect(self.refilter_and_display)
        self.actionExport_to_CSV.triggered.connect(lambda: self.save_data(target='csv'))
        self.actionCreate_data_backup.triggered.connect(
            lambda _: self.show_backup_dialog())
        self.modernButton_loadPlotData.clicked.connect(self.load_conc_data)
        self.modernButton_plotStem.clicked.connect(self.create_stem_plot)
        self.modernButton_plotPie.clicked.connect(
            lambda _: self.create_pie_plot())
        self.comboBox_PiePlotType.currentTextChanged.connect(
            lambda _: self.create_pie_plot())
        self.modernButton_addRow.clicked.connect(self.tableView_pandasViewer._menu_insert_row)
        self.comboBox_baseLang.currentTextChanged.connect(
            lambda text: self.set_group_options(0))
        self.comboBox_diffParsingLang.currentTextChanged.connect(
            lambda text: self.set_group_options(1))

        # Do some post init stuff
        self.qt_log_window.debug_state_toggle.setChecked(
            options['logger_show_debug'])
        if options['show_logger_on_start']:
            self.qt_log_window.show()
        self.qt_logstream.popup_lvl = options['logger_popup_level']

        # Check user folder
        try:
            _check_user_folder()
        except (IOError, FileNotFoundError):
            logger.warning('No valid data folder, please select existing or new!')
            folder = QtWidgets.QFileDialog.getExistingDirectory(
                self, 'Select data directory', dir=expanduser('~'),
            )
            if not folder:
                raise IOError("Invalid folder")
            set_data_dir(Path(folder))
            logger.info('New data directory created')

        # Center labels in menu
        self.label_baseLang.setAlignment(Qt.AlignCenter)
        self.label_receiptDisplayMode.setAlignment(Qt.AlignCenter)
        self.label_filterSlider.setAlignment(Qt.AlignCenter)
        self.label_pieType.setAlignment(Qt.AlignCenter)

        # Fix init tab
        self.centralTabWidget.setCurrentIndex(0)

        # Setup splitter default
        c_wi = self.width() - 180
        self.splitter_mainPage.setSizes(
            [int(c_wi * 1 / 3), int(c_wi * 2 / 3)])

        # Finally, double check that the logger level is correct
        if options['logger_show_debug']:
            self.qt_logstream.setLevel(logging.DEBUG)
        else:
            self.qt_logstream.setLevel(logging.INFO)

    def closeEvent(self, event):
        """Handle additional open windows"""
        if self.raw_text_window is not None:
            self.raw_text_window.close()
            self.raw_text_window = None

        super().closeEvent(event)

    def _about(self):
        """Build and display about box with dynamic version info"""
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
        """
        Builds and displays the raw text window if a receipt with raw data is
        successfully loaded.
        """
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
        """Destroy reference"""
        self.raw_text_window = None

    def load_receipt(self):
        """
        Tries to load a new receipt for processing. If a receipt is loaded,
        tries to reset everything. Filters and displays the new receipt if
        loading was successful.
        """
        file, ptn = QtWidgets.QFileDialog(self).getOpenFileName(
            caption='Select a receipt file',
            dir=expanduser('~'),
            filter=('Valid files (*.pdf *.png *.PNG *.jpeg *.JPEG *.jpg *.JPG);;'
                    'Parsed Receipt (*.h5 *.hdf *.hdf5);;'
                    'FreeForAll (*.*)')
        )
        if file and Path(file).exists():
            self.statusbar.showMessage('Loading receipt...', 2000, color='green')
        else:
            self.statusbar.showMessage('Invalid File', 3000, color='red')
            return

        if Path(file).suffix in ('.hdf', '.h5', '.hdf5'):
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
                    unsharp_ma=(5, self.slider_FilterAmount.get_scaled_val())).extract_data(
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
                    self.slider_FilterAmount.setEnabled(False)
                    self.comboBox_receiptDisplayMode.setEnabled(False)

            except (IOError, FileNotFoundError):
                logger.warning('Invalid file type for a new receipt!')
                return

        self.comboBox_receiptDisplayMode.setCurrentIndex(0)
        if self.receipt is not None:
            self.receipt.disp_ax = self.plot_area_receipts.ax
            self.display_receipt()

    def display_receipt(self):
        """Displays the receipt in the plot window."""
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
        """Reapplies filters with updated settings and calls the display routine"""
        if self.receipt is None:
            return
        self.receipt.filter_image(
            unsharp_ma=(5, self.slider_FilterAmount.get_scaled_val())).extract_data(
            lang=self.comboBox_baseLang.currentText())
        self.statusbar.showMessage('Refiltering image', timeout=2000, color='green')
        self.update_rec_plot(keep_lim)

    def update_rec_plot(self, keep_lim=True):
        """
        Updates the core plot with possible same limits, used to update filter
        params without destroying the current zoom view.
        """
        current_lim = (
            self.plot_area_receipts.ax.get_xlim(),
            self.plot_area_receipts.ax.get_ylim())
        self.display_receipt()
        if keep_lim:
            self.plot_area_receipts.ax.set_xlim(current_lim[0])
            self.plot_area_receipts.ax.set_ylim(current_lim[1])

    def rotate_event(self, event, minor_step=0.1, major_step=0.5):
        """
        Event that adds a rotation to the receipt. Left and right are switched
        due to the usual positive definition of mathematical rotation.
        """
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
        """
        Sets new data to the UI elements, in case of loading a parsed receipt
        or adding the data manually(?)

        Parameters
        ----------
        new_data : `pd.DataFrame`
            New data, must have the default format
        has_meta : `bool`, optional
            If meta is expected in the data, then update all meta fields. By
            default False
        """
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
        """
        Updates the difference display between total value and current data
        sum.
        """
        try:
            refval = float(refval)
        except ValueError:
            logger.warning('Cant convert this new total price to float!')
            return

        if baseval is None:
            try:
                diff = refval - self._current_data['Price'].sum()
            except Exception as compute_exc:
                diff = refval - self.tableView_pandasViewer.get_final_data()['Price'].sum()

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
        """
        Recomputes the difference value if data in the numeric columns
        containing the price data is changed. Column number is hard coded,
        **CAREFUL**!
        """
        col1, col2 = index1.column(), index2.column()
        if col1 == 5 or col2 == 5:
            self.update_diff(
                float(self.lineEdit_totalAmountReceipt.text()),
                self.tableView_pandasViewer.model()._data['Price'].sum()
            )

    def set_group_options(self, sender):
        if self.checkBox_useDiffParsingLang.isChecked() and sender == 0:
            # This catched a possible language change if the second is active
            # but the first has been changed
            return

        if sender == 0:
            lang = self.comboBox_baseLang.currentText()
        elif sender == 1:
            lang = self.comboBox_diffParsingLang.currentText()
        elif sender == -1:
            lang = options['lang']
        else:
            raise RuntimeError('Invalid siganture')

        # Read in a dict with possible language based groups
        try:
            _possible_groups = bb_io._load_basic_match_data(lang)[0]
        except FileNotFoundError:
            try:
                _possible_groups = bb_io._load_user_match_data(lang)[0]
            except FileNotFoundError:
                logger.exception('No group data for current language ')
                return

        # If found, reset group boxes
        _possible_groups = sorted(list(_possible_groups.keys()))
        self.tableView_pandasViewer.set_combo_column(7, _possible_groups + ['none'])

    def parse_data(self):
        """
        Parses a loaded receipt and displays the extracted data in the table
        view. Since all the core functions are implemented in the `Receipt`
        class this is just a wrapper handling UI settings and data display.
        """
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

        # Remove old rects
        for patch in self.plot_area_receipts.ax.patches:
            patch.remove()

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
        """Parses date from receipt, converts it and sets the date selector."""
        if self.receipt is None:
            msg = 'Please load a receipt first'
            logger.info(msg)
            self.statusbar.showMessage(msg, timeout=3000)
            return

        rec_date = self.receipt.parse_date()
        if rec_date is None:
            msg = 'No Date could be extracted'
            logger.info(msg)
            self.statusbar.showMessage(msg, timeout=3000, color='red')
            return

        self.dateEdit_shopDate.setDate(ui_support.convert_date(rec_date))
        self.statusbar.showMessage('Date extracted', timeout=3000, color='green')

    def detect_vendor(self):
        """Parses vendor and sets the vendor text."""
        if self.receipt is None:
            msg = 'Please load a receipt first'
            logger.info(msg)
            self.statusbar.showMessage(msg, timeout=3000)
            return

        if self.checkBox_useDiffParsingLang.isChecked():
            lang = self.comboBox_diffParsingLang.currentText()
        else:
            lang = self.comboBox_baseLang.currentText()

        curr_vendor = self.lineEdit_marketVendor.text()
        if curr_vendor == '' or curr_vendor == 'General':
            vendor = self.receipt.parse_vendor(lang)
            self.lineEdit_marketVendor.setText(vendor)
            self.statusbar.showMessage(
                'Vendor extracted', timeout=2000, color='green')

        else:
            logger.info(f'Manually setting vendor to {curr_vendor}')
            self.receipt.set_vendor(curr_vendor)

    def re_match_data(self):
        """
        Re-Runs the group matcher if data has been changed or on manual request,
        e. g. with manual data entered by the user.
        """
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

    def refill_data(self):
        """
        Re-Runs data fill computation for units and unit prices if data has
        been changed or on manual request, e. g. with manual data entered by
        the user.
        """
        if self.tableView_pandasViewer.model().rowCount() > 0:
            data = self.tableView_pandasViewer.get_final_data()

        else:
            return

        data = parsers.fill_missing_data(data)

        self.set_new_data(data)

    def save_data(self, target='hdf'):
        """
        Saves the data currently displayed in the metadata fields and the
        table view. Has a hook to export data to a simple format, currently
        only `csv`.

        Parameters
        ----------
        target : `str`, optional
            Hook to write the data to a simple format (export data), currently
            supports `csv` only. By default 'hdf' which creates the default
            files.
        """
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

        if target == 'csv':
            year = retrieved_data.loc[0, 'Date'].strftime('%Y')
            mon_day = retrieved_data.loc[0, 'Date'].strftime('%m_%d')
            target = Path(options['data_folder']) / 'export'

            data_target = bb_io._unique_file_name(
                Path(target) / f'{year}_{mon_day:s}_{retrieved_data.loc[0, "Vendor"]:s}.csv')

            retrieved_data = bb_io.resort_data(retrieved_data)
            retrieved_data.to_csv(data_target)
            logger.info(f'Exported data to csv: {str(data_target.name)}')
            return

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

    def show_backup_dialog(self, target_folder=options['data_folder']):
        """
        Creates and shows the dialog to backup data. Usually this is placed in
        data folder / backup but this can be changed.
        """
        full_dataset, n_files = bb_io.load_concatenad_data()

        backup_dialog = ui_support.AskComboDialog(self)
        backup_dialog.label1.setText(
            'Backup Data: Please select the best format. Using csv and hdf '
            'will combine all data into one file.<br>This is good for exporting '
            'and archival purposes but <b>removes any metadata as receipt '
            'specific tags</b>'
        )
        backup_dialog.label2.setText(
            f'Currently there are <font color="red">{full_dataset.shape[0]:d}'
            f'</font> datasets in <font color="red">{n_files:d}</font> files. '
            'The overall total amounts to '
            f'<font color="red">{full_dataset["Price"].sum():.2f}€</font>!'
        )
        ok, format = backup_dialog.exec()

        if not ok:
            logger.info('Export stopped')
            return

        today = datetime.date.today().strftime('%Y_%m_%d_')

        if Path(target_folder).resolve() == Path(options['data_folder']).resolve():
            target_folder = Path(target_folder) / 'backup'

        if not target_folder.is_dir():
            logger.error("Target Folder does not exists")
            return

        target = target_folder / f'{today:s}full_export.{format:s}'

        if format == 'csv':
            full_dataset.to_csv(target)
        elif format == 'hdf':
            bb_io.save_with_metadata(full_dataset, target)
        elif format == 'zip':
            # Get all files and images
            to_zip = Path(options['data_folder']) / 'data'
            _ = make_archive(target.parent / target.stem, 'zip', to_zip)

        else:
            logger.warning("Invalid backup format")
            return

        logger.info(f'Export finished to: {target}')

    def load_conc_data(self):
        """
        Loads all available data from the data folder into a single dataframe.
        """
        conc_data = bb_io.load_concatenad_data()[0]
        if conc_data.shape[0] == 0:
            logger.error('Loaded dataset seems to be empty')
            return

        self.conc_data = conc_data
        self.modernButton_plotStem.setEnabled(True)
        self.modernButton_plotPie.setEnabled(True)
        logger.debug(f'Dataset loaded with {conc_data.shape[0]:d} elements')

    def create_stem_plot(self):
        """Parses data, clears axes and calls backend to create a stem plot."""
        for ax in self.plot_area_data.fig.get_axes():
            ax.remove()
        self.plot_area_data.ax = None
        self.plot_area_data.add_subplot(111)
        plotting.create_stem(self.conc_data, self.plot_area_data.ax[0])
        self.plot_area_data.draw_blit()

    def create_pie_plot(self):
        """Parses data, clears axes and calls backend for pie plot."""
        def _fmt_pie_label(number, cutoff):
            if number < cutoff:
                return ''
            return f'{number:.1f} %'

        # Check setup
        if self.comboBox_PiePlotType.currentText() == 'Vendors':
            pie_by = 'Vendor'
            bar_by = 'Group'
            label_cutoff = 4.

        elif self.comboBox_PiePlotType.currentText() == 'Categories':
            pie_by = 'Category'
            bar_by = 'Group'
            label_cutoff = 1.

        elif self.comboBox_PiePlotType.currentText() == 'Groups':
            pie_by = 'Group'
            bar_by = 'Vendor'
            label_cutoff = 1.

        else:
            logger.error('Pie / Bar setup invalid')
            return

        # Reset area
        for ax in self.plot_area_data.fig.get_axes():
            ax.remove()

        self.pieplot = None
        self.piehandler = None

        self.plot_area_data.ax = None
        self.plot_area_data.draw_blit()
        self.plot_area_data.add_subplot(1, 2, 1)
        self.plot_area_data.add_subplot(1, 2, 2)
        self.plot_area_data.draw_blit()

        # Create plot
        data_pie = self.conc_data.groupby(pie_by)['Price'].sum().abs()
        total = data_pie.sum()
        labels = np.array(data_pie.index)
        labels[data_pie * 100 / total < label_cutoff] = ''
        self.pieplot = self.plot_area_data.ax[0].pie(
            data_pie, labels=labels,
            autopct=lambda num: _fmt_pie_label(num, label_cutoff),
            pctdistance=0.75)

        self.piehandler = plotting.PieEventHandler(
            self.pieplot, self.conc_data,
            self.plot_area_data.ax[1], bar_labels='both',
            reduce_df=(pie_by, bar_by), label_cutoff=label_cutoff)

        self.plot_area_data.draw_blit()