"""Contains helpers to run customized UI functions, e.g. better logging"""
from typing import Optional
from pathlib import Path
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.pyplot import subplots, figure
from collections.abc import Iterable
import logging
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Signal, Slot, Qt
import numpy as np
import pandas as pd
from darkdetect import isDark

from ..configs.config import options
from ..configs.constants import icons
from ..configs.config_tools import set_option, set_data_dir


logger = logging.getLogger(__package__)


def _get_log_text_colors():
    """
    Returs text colors depending on dark mode setting in the order of
    DEBUG, INFO, WARNING, ERROR, EXCEPTION.
    """
    if isDark():
        return (QtGui.QColor(220, 220, 220, 170),
                QtGui.QColor(220, 220, 220, 255),
                QtGui.QColor(250, 170, 0, 255),
                QtGui.QColor(255, 80, 0, 255),
                QtGui.QColor(255, 0, 0, 255))
    else:
        return (QtGui.QColor(22, 22, 22, 170),
                QtGui.QColor(22, 22, 22, 255),
                QtGui.QColor(250, 170, 0, 255),
                QtGui.QColor(255, 80, 0, 255),
                QtGui.QColor(255, 0, 0, 255))


def _check_numeric(data):
    """
    Checks if data (a single data element) is of numeric type and thus can be
    handled differenly than a non numeric type in the table view.
    """
    if isinstance(data, (str, bool)):
        return False
    if np.isnan(data):
        return False

    return (
        np.issubdtype(data, int) or
        np.issubdtype(data, np.int32) or
        np.issubdtype(data, np.int64) or
        np.issubdtype(data, float) or
        np.issubdtype(data, np.float32) or
        np.issubdtype(data, np.float64) or
        np.issubdtype(data, complex) or
        np.issubdtype(data, np.complex64) or
        np.issubdtype(data, np.complex128)
    )


def convert_date(input_date):
    """
    Converts a date back and forth from `QDate` to `pd.datetime`

    Parameters
    ----------
    input_date : `QDate`, `pd.datetime`
        Input date

    Returns
    -------
    `QDate`, `pd.datetime`
        Output date in different format

    Raises
    ------
    ValueError
        If conversion is not possible
    """
    if isinstance(input_date, QtCore.QDate):
        return pd.to_datetime(input_date.toPython())
    elif isinstance(input_date, pd.Timestamp):
        return QtCore.QDate(input_date.year, input_date.month, input_date.day)
    else:
        raise ValueError('Input must be either a QDate or a pandas Timestamp')


# Build icons to reduce IO, only possible after App is started
def _create_icons():
    """Creates `QIcons` from icon image paths"""
    return {key: QtGui.QIcon(value) for key, value in icons.items()}


def set_new_conf_val(parent, name, valtype):
    """
    Opens a dialog to get a new config value and converts it for the use in a
    config.ini file type. Writes to config file and options.

    Parameters
    ----------
    parent : `QWidget`
        Parent widget, can be `None`
    name : `str`
        Config value name to change
    valtype : `str`
        Config calue type, decides what is asked by the UI

    Raises
    ------
    LookupError
    ValueError
    """
    try:
        curr_val = options[name]
    except KeyError:
        error = f'Configuration option "{name}" does not exist.'
        logger.error(error)
        raise LookupError(error)

    if valtype == 'int':
        retval, oked = QtWidgets.QInputDialog.getInt(
            parent, 'Specify new config value', 'Enter Int type config value',
            value=curr_val, step=1
        )
    elif valtype == 'str':
        retval, oked = QtWidgets.QInputDialog.getText(
            parent, 'Specify new config value', 'Enter string type config value',
            text=curr_val,
        )
    elif valtype == 'dir':
        retval = QtWidgets.QFileDialog.getExistingDirectory(
            parent, 'Select new data directory', curr_val)
        oked = True
        if not retval:
            oked = False
    else:
        raise ValueError('Unsupported config value type')

    if not oked:
        return

    if name == 'data_folder':
        set_data_dir(retval)
    else:
        set_option(name, retval)


class _LogSignalProxies(QtCore.QObject):
    """
    This is needed for signal namespace protection with logging emit calls -
    else there will be crazy untracable namespace bugs! Just creates the
    signals needed for logging.
    """
    log_record_signal = Signal(int, str)
    show_log_window = Signal()

    def __init__(self):
        QtCore.QObject.__init__(self)


class MplCanvas(FigureCanvas):
    """Creates a matplotlib plot in an empty `QFrame` widget."""
    def __init__(self, parent=None, *args, **kwargs):
        """
        Set up plotting frame.

        Parameters
        ----------
        parent : `QWidget`, optional
            Parent widget, by default None
        """
        self.qt_parent = parent  # Can't overload parent from FigureCanvas

        no_ax = kwargs.pop('no_ax', False)
        if no_ax:
            self.fig = figure()
            self.ax = None
        else:
            self.fig, self.ax = subplots(*args, **kwargs)

            if isinstance(self.ax, Iterable):
                for ax in self.ax:
                    ax.set_aspect('auto')
            else:
                self.ax.set_aspect('auto')

        super(FigureCanvas, self).__init__(self.fig)
        self.toolbar = NavigationToolbar(self, self.qt_parent)

        self.layout = QtWidgets.QVBoxLayout(self.qt_parent)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self)
        self.canvas = self.fig.canvas

    def draw_blit(self):
        """Redraw canvas using blit"""
        self.fig.canvas.blit()
        self.fig.canvas.draw()

    def add_subplot(self, *args, **kwargs):
        if self.ax is None:
            self.ax = [self.figure.add_subplot(*args, **kwargs)]
        else:
            self.ax += [self.figure.add_subplot(*args, **kwargs)]


class QLoggingThread(QtCore.QThread, logging.StreamHandler):
    """
    QLoggingThread does nothing else but run a background thread that catches
    all log messages and reroutes them with a signal to prevent any
    unregistered quantitites when using sub package, sub thread logging.
    """
    def __init__(self, **kwargs):
        QtCore.QThread.__init__(self)
        logging.StreamHandler.__init__(self, **kwargs)
        self.signals = _LogSignalProxies()

        self._popup_threshold = logging.WARNING

    @property
    def popup_lvl(self):
        """
        Level at which the window is `raise()` to show an important message to
        the user.
        """
        return self._popup_threshold

    @popup_lvl.setter
    def popup_lvl(self, new_lvl):
        if not isinstance(new_lvl, int):
            logging.error('New level for popup threshold must be INT')
            return
        self._popup_threshold = new_lvl

    def emit(self, record):
        # Only log if the message should be visible
        if record.levelno < self.level:
            return

        if record.levelno >= self._popup_threshold:
            self.signals.show_log_window.emit()

        lvl = record.levelno
        record = self.format(record)

        self.signals.log_record_signal.emit(lvl, record)

    @Slot(int)
    def set_new_loglvl(self, lvl):
        self.setLevel(lvl)


class QLoggingWindow(QtWidgets.QDialog):
    """
    Pattern class to generate a buffered logging stream handler to display
    and format logging messages during execution of the UI.
    """
    new_level_signal = Signal(int)

    def __init__(self, parent=None):
        """
        Creates the window `QDialog` that holds the logging messages.

        Parameters
        ----------
        parent : `QWidget`, optional
            Parent widget, by default None
        """
        super().__init__(parent)
        self._show_debug = False
        self.create_logging_dialog()
        self.debug_state_toggle.setChecked(False)
        self.console.setReadOnly(True)
        self.hide()

    def _set_show_debug(self, new_val):
        self._show_debug = new_val
        if new_val:
            self.new_level_signal.emit(logging.DEBUG)
        else:
            self.new_level_signal.emit(logging.INFO)

    @Slot()
    def show_logging_window(self):
        self.show()
        self.raise_()

    @Slot()
    def catch_message(self, levelno, msg):
        colors = _get_log_text_colors()
        cursor = self.console.textCursor()
        old_fmt = cursor.charFormat()

        # Conditional format depending on level
        if levelno <= logging.DEBUG:  # Debug
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(12)
            fmt.setForeground(colors[0])
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        elif levelno <= logging.INFO:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(50)
            fmt.setFontItalic(True)
            fmt.setForeground(colors[1])
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        elif levelno <= logging.WARNING:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(50)
            fmt.setForeground(colors[2])
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        elif levelno <= logging.ERROR:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(75)
            fmt.setForeground(colors[3])
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        elif levelno <= logging.CRITICAL:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(100)
            fmt.setForeground(colors[4])
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        self.console.append(msg)

        self.move_to_end(old_fmt)

    def move_to_end(self, old_fmt=None):
        # Reset style and move to end
        c = self.console.textCursor()
        if old_fmt is not None:
            c.setCharFormat(old_fmt)
        c.atEnd()
        self.console.setTextCursor(c)
        sb = self.console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def create_logging_dialog(self):
        self.setWindowTitle('Console output')
        self.setWindowModality(QtCore.Qt.NonModal)

        mainLayout = QtWidgets.QGridLayout()

        self.console = QtWidgets.QTextEdit(self)

        label1 = QtWidgets.QLabel('Show debug log: ')
        clearButton = QtWidgets.QPushButton()
        clearButton.setText('Clear')
        clearButton.clicked.connect(self.console.clear)

        self.debug_state_toggle = QtWidgets.QCheckBox()
        self.debug_state_toggle.setChecked(self._show_debug)
        self.debug_state_toggle.stateChanged.connect(self._set_show_debug)

        # Assemble window
        self.console.show()
        self.move_to_end()

        mainLayout.addWidget(label1, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        mainLayout.addWidget(self.debug_state_toggle, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(clearButton, 0, 2, 1, 1, QtCore.Qt.AlignRight)
        mainLayout.addWidget(self.console, 1, 0, 1, 3)
        mainLayout.setContentsMargins(2, 5, 2, 0)
        self.setLayout(mainLayout)
        self.show()
        self.resize(640, 480)
        self.hide()


class ComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    """
    A delegate to display a combo box in a table view. Supports presetting
    possible groups to display and a color highlight if the group is *none*.
    """
    def __init__(self, parent=None, possible_groups=[]):
        super(ComboBoxDelegate, self).__init__(parent)
        self.possible_groups = possible_groups

    def createEditor(self, parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        combo.addItems(self.possible_groups)
        combo.setAutoFillBackground(True)
        return combo

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if str(value) in self.possible_groups:
            editor.setCurrentText(
                self.possible_groups[self.possible_groups.index(str(value))])
        else:
            editor.setCurrentText('none')

    # That changes the displayed value but not the underlying data
    def displayText(self, value, locale):
        if str(value) in self.possible_groups:
            return self.possible_groups[self.possible_groups.index(str(value))]
        else:
            return 'none'

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def paint(self, painter, option, index):
        value = str(index.model().data(index, Qt.DisplayRole))

        if value == 'none':
            painter.fillRect(option.rect, QtGui.QColor(255, 0, 0, 170))
            option.font.setBold(True)
            option.palette.setColor(QtGui.QPalette.Text, QtGui.QColor(240, 240, 240))

        super().paint(painter, option, index)


class PandasTableModel(QtCore.QAbstractTableModel):
    """
    The main table model backend to handle the display and edit of a fairly
    complex `pd.DataFrame`. Supports header display, sorting, group icons,
    type specific format, insert and removal of rows.
    """
    def __init__(self, data=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._ref_idx = 'Orig. Index'
        self._data = data.copy().reset_index(names=self._ref_idx)
        self._dtypes = self._data.dtypes
        self.combo_col = -1
        self.icons = _create_icons()

        # Fix invalid group columns
        # self._data['Group'] = self._data['Group'].apply(_fix_group)

        # Sorting
        self._sort_column = 0
        self._sort_order = Qt.AscendingOrder

    def sort(self, column, order=Qt.AscendingOrder):
        self.layoutAboutToBeChanged.emit()

        self._sort_column = column
        self._sort_order = order
        column_name = self._data.columns[column]
        self._data = self._data.sort_values(
            column_name, ascending=order == Qt.AscendingOrder).reset_index(drop=True)

        self.layoutChanged.emit()

    def sortColumn(self):
        return self._sort_column

    def sortOrder(self):
        return self._sort_order

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._data.shape[0]

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        row = self._data.iloc[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            return str(row[col])

        elif role == Qt.EditRole:
            return str(row[col])

        elif role == Qt.TextAlignmentRole:
            if _check_numeric(row[col]):
                return Qt.AlignVCenter + Qt.AlignRight
            else:
                return Qt.AlignVCenter + Qt.AlignLeft

        elif role == Qt.DecorationRole and col == self.combo_col:
            if (this_val := self._data.iat[index.row(), self.combo_col]) != 'none':
                try:
                    return QtGui.QIcon(self.icons[this_val])
                except KeyError:
                    logger.debug(f'No icon for group {this_val:s}')

            else:
                return None

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and (0 <= section < self.columnCount()):
            return self._data.columns[section]

        elif role == Qt.DisplayRole and orientation == Qt.Vertical:
            return section

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        elif index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < self.rowCount():
            try:
                if np.issubdtype(self._dtypes[index.column()], float):
                    value = float(value)
                elif np.issubdtype(self._dtypes[index.column()], int):
                    value = int(value)
            except ValueError:
                logger.debug("Wrong dtype in tableview column")
                return False

            self._data.iat[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self._data.loc[row + i, :] = [
                int(self._data[self._ref_idx].max() + 1), -1,
                'New Article Name', 1, 1, 1, 0, 'none']
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        self._data = self._data.drop(self._data.index[row]).reset_index(drop=True)
        self.endRemoveRows()

    def update_data(self, new_data):
        self.beginResetModel()
        self._data = new_data.copy().reset_index(names=self._ref_idx)
        self._dtypes = self._data.dtypes
        self.endResetModel()


class PandasViewer(QtWidgets.QTableView):
    """
    The main viewer class that displays the data the custom model holds and
    allows high level access to the data.
    """
    def __init__(self, parent=None, model=None):
        QtWidgets.QTableView.__init__(self, parent)
        self._combo_delegate = None

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        if model is not None:
            self.setModel(model)

    def setModel(self, model, vert_header=False):
        super().setModel(model)
        self.setSortingEnabled(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.model().sort)

        self.verticalHeader().setDefaultSectionSize(18)
        self.verticalHeader().setMinimumSectionSize(18)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setVisible(vert_header)

        self.model().sort(0)

    def showContextMenu(self, pos):
        menu = QtWidgets.QMenu(self)
        add_action = menu.addAction("Add row")
        remove_row_action = menu.addAction("Remove Row")
        action = menu.exec(self.mapToGlobal(pos))

        # Evaluate menu
        if action == add_action:
            self._menu_insert_row()

        elif action == remove_row_action:
            self._menu_remove_row()

    def _menu_insert_row(self):
        self.model().insertRows(self.model().rowCount(), 1)

    def _menu_remove_row(self):
        selected_indexes = self.selectedIndexes()
        if selected_indexes:
            selected_rows = sorted(list(set(index.row() for index in selected_indexes)), reverse=True)
            for row in selected_rows:
                self.model().removeRow(row)

    def set_combo_column(self, column, poss_col):
        self._combo_delegate = ComboBoxDelegate(self, possible_groups=poss_col)
        self.setItemDelegateForColumn(column, self._combo_delegate)

    def get_final_data(self, remove_orig_index=True):
        if remove_orig_index:
            return self.model()._data.copy().drop(
                columns=[self.model()._ref_idx])
        else:
            return self.model()._data.copy()


class SliderWithVal(QtWidgets.QWidget):
    """
    A slider that displays its val to the user. Also allows scaling to float
    since the basic slider does not support that.
    Has a callback that is timed at `self.delay`
    """
    def __init__(
            self, parent=None, layout='v'):
        """See above for info

        Parameters
        ----------
        parent : `QWidget`, optional
            parent widget, by default None
        layout : `str`, optional
            Can be `h` or `v` for slider layout horizontal or vertical, by
            default 'h'
        """
        super().__init__(parent)

        # Dummy init
        self.step = 1
        self.labeltext = ''
        self.delay = 1000
        self._timer_cb = None

        # Create a layout for slider and label
        if layout == 'h':
            slider_layout = QtWidgets.QHBoxLayout(self)
        elif layout == 'v':
            slider_layout = QtWidgets.QVBoxLayout(self)
        else:
            raise RuntimeError('Invalid slider layout')

        # Create a slider widget
        self.slider = QtWidgets.QSlider(self)
        self.slider.setSingleStep(1)   # Set step size of slider
        self.slider.valueChanged.connect(self.slider_moved)  # Connect signal to slot
        if layout == 'h':
            self.slider.setOrientation(Qt.Horizontal)
        else:
            self.slider.setOrientation(Qt.Vertical)

        self.slider_value_label = QtWidgets.QLabel(parent=self)
        # Add the slider and label to the horizontal layout
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.slider_value_label)

        # Create a timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timer_callback)

        # Show
        self.setLayout(slider_layout)

    # Expose Slider Core methods so the init from designer works
    def setMinimum(self, val):
        self.minval = val
        self.slider.setMinimum(val)

    def setMaximum(self, val):
        self.maxval = val
        self.slider.setMaximum(val)

    def setSingleStep(self, val):
        self.step = val
        self.slider.setSingleStep(val)

    def setSliderPosition(self, val):
        self.slider.setSliderPosition(val)

    def setValue(self, val):
        self.slider.setValue(val)

    def setOrientation(self, val):
        self.slider.setOrientation(val)

    def setTickPosition(self, val):
        self.slider.setTickPosition(val)

    def custom_setup(self, minval=0.5, maxval=2., step=0.05,
                     label='Amount: ', value_change_delay=1500):
        """
        Sets up the sliders main values for scaling and callback

        Parameters
        ----------
        minval : `float`, optional
            Minimum scale value, by default 0.5
        maxval : `float`, optional
            Maximum scale value, by default 2
        step : `float`, optional
            Scaled step, by default 0.05
        label : `str`, optional
            Slider label, by default 'Amount: '
        value_change_delay : `int`, optional
            Timer delay before callback in millis, by default 1500
        """
        self.labeltext = label
        self.delay = value_change_delay
        self.minval = minval
        self.maxval = maxval
        self.step = step
        self.timer.setInterval(self.delay)

        self.slider.setRange(
            int(self.minval // self.step) + 1,
            int(self.maxval // self.step) + 1)   # Set range of slider in int

        # Create a label for slider value
        self.slider_value_label.setText(
            f'{ self.labeltext:s}{self.slider.value() * step:.2f}')

    def _remove_label(self):
        self.slider_value_label.setVisible(False)
        self.layout().removeWidget(self.slider_value_label)

    def get_scaled_val(self):
        return self.slider.value() * self.step

    def slider_moved(self):
        self.timer.stop()  # Stop the timer if running
        slider_value = self.get_scaled_val()
        self.slider_value_label.setText(
            f'{ self.labeltext:s}{slider_value:.2f}')
        self.timer.start()  # Start the timer again

    def set_timer_callback(self, new_cb):
        """
        Sets a new timer callback

        Parameters
        ----------
        new_cb : `callable`
            New slider callback
        """
        if callable(new_cb):
            self._timer_cb = new_cb
        else:
            logger.warning(
                'This function input must be callable. Not set, try again')

    def timer_callback(self):
        self.timer.stop()
        if self._timer_cb is not None:
            self._timer_cb()

    def closeEvent(self, event):
        self.timer.stop()  # Stop the timer
        self.timer.deleteLater()  # Delete the timer
        event.accept()  # Accept the close event


class ColoredStatusBar(QtWidgets.QStatusBar):
    """
    A nice colored statusbar that supports the same functionality as the
    default implementation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a label with rich text format
        self.statusLabel = QtWidgets.QLabel()
        self.statusLabel.setTextFormat(Qt.RichText)

        # Add the label to the status bar
        self.addWidget(self.statusLabel)

    def showMessage(self, message, timeout=0, color='black'):
        self.statusLabel.setText(
            f'<font color="{color:s}">{message:s}</font>')

        if timeout > 0:
            self.timer = QtCore.QTimer(self)
            self.timer.setInterval(timeout)
            self.timer.timeout.connect(self.clearMessage)
            self.timer.start()

    def clearMessage(self):
        self.statusLabel.setText('')


class TextDisplayWindow(QtWidgets.QWidget):
    """
    A simple `QDialog` that displays long text with correct special char
    parsing. Has a closed signal to prevent lingering windows if called from
    a main UI loop.
    """
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Raw Text Display')
        self.setGeometry(100, 50, 500, 700)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        scroll_bar_policy = Qt.ScrollBarAsNeeded
        self.text_edit.setVerticalScrollBarPolicy(scroll_bar_policy)
        self.text_edit.setHorizontalScrollBarPolicy(scroll_bar_policy)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

    def update_text(self, text, show=False):
        self.text_edit.setText(text)
        if show:
            self.raise_()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


class CustomFadeDialog(QtWidgets.QDialog):
    """
    A small fading out dialog to show a quick confirmations message without
    too much obstruction for the user.
    """
    def __init__(self, parent=None, text='Confirmation message'):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        layout = QtWidgets.QVBoxLayout(self)

        # Create and center-align the custom icon
        icon_label = QtWidgets.QLabel(self)
        style = self.style()
        pixmap = style.standardPixmap(QtWidgets.QStyle.SP_DialogOkButton)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Create and center-align the text
        text_label = QtWidgets.QLabel(text, self)
        text_label.setAlignment(Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        text_label.setFont(font)
        layout.addWidget(text_label)

        self.setLayout(layout)

        self.fade_out_dialog()

    def fade_out_dialog(self):
        # Create a fade-out animation for the dialog
        self.animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(3000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.animation.finished.connect(self.close)

        # Start the animation
        self.animation.start()


class ModernButton(QtWidgets.QToolButton):
    """
    TODO
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the highlight effect on mouseover and frame
        self.setStyleSheet(
            """
            ModernButton {
                border: 2px solid gray;
                border-radius: 4px;
            }

            ModernButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid black;
                border-radius: 4px;
            }
            """
        )

    def set_scaled_icon_and_text(self, icon, text):
        """
        Icon can be a path (prio 1), if this is not valid tries to use the inp
        as a QIcon standard. Takes pkg rel. path and assumes icon in icon in img.
        """
        try:
            icon = Path(__file__).parent.parent / 'img' / icon
            icon = QtGui.QIcon(str(icon))
        except TypeError:
            icon = self.style().standardIcon(icon)

        self.setIcon(icon)
        icon_size = int(self.size().width() * 0.65)
        logger.debug(f'Sclaed icon to {icon_size:d}')
        self.setIconSize(QtCore.QSize(icon_size, icon_size))

        self.setText(text)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

class AskComboDialog(QtWidgets.QDialog):
    """
    Displays a dialog with two labels and a combo box and handles the users
    custom choice on return. Currently this is used once and thus ahs fixed
    strings, but this could be generalized easily."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.result = (False, None)

        # Create the UI elements
        self.label1 = QtWidgets.QLabel()
        self.label2 = QtWidgets.QLabel()
        self.label1.setTextFormat(Qt.RichText)
        self.label2.setTextFormat(Qt.RichText)
        self.label_combo = QtWidgets.QLabel('Select export type: ')
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(["csv", "hdf", "zip"])
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        # Set the layouts
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)

        combo_layout = QtWidgets.QHBoxLayout()
        combo_layout.addWidget(self.label_combo)
        combo_layout.addWidget(self.combo)
        layout.addLayout(combo_layout)

        layout.addWidget(self.button_box)
        self.setLayout(layout)

        # Connect the signals
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def accept(self):
        # Return True and combo value on 'Ok'
        self.result = (True, self.combo.currentText())
        super().accept()

    def reject(self):
        # Return False on 'Cancel'
        self.result = (False, None)
        super().reject()

    def exec(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        super().exec()
        return self.result