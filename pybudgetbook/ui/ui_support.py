"""Contains helpers to run customized UI functions, e.g. better logging"""
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.pyplot import subplots
from collections.abc import Iterable
import logging
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Signal, Slot, Qt
import numpy as np

logger = logging.getLogger(__package__)


class _LogSignalProxies(QtCore.QObject):
    """
    Signal namespace protection with logging emit calls - else there will be
    crazy untracable namespace bugs!
    """

    log_record_signal = Signal(int, str)
    show_log_window = Signal()

    def __init__(self):
        QtCore.QObject.__init__(self)


class MplCanvas(FigureCanvas):
    """
    TODO
    """

    def __init__(self, parent=None, *args, **kwargs):
        self.qt_parent = parent  # Can't overload parent from FigureCanvas

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


class QLoggingThread(QtCore.QThread, logging.StreamHandler):
    """
    QLoggingThread does nothing else but run a background thread that catches all log
    messages and reroutes them with a signal to prevent any unregistered
    quantitites when using sub package, sub thread logging.
    """

    def __init__(self, **kwargs):
        QtCore.QThread.__init__(self)
        logging.StreamHandler.__init__(self, **kwargs)
        self.signals = _LogSignalProxies()

        self._popup_threshold = logging.WARNING

    @property
    def popup_lvl(self):
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
        super().__init__(parent)
        self._show_debug = False
        self.create_logging_dialog()
        self.console.setReadOnly(True)
        self.hide()

    def set_show_debug(self, new_val):
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
        cursor = self.console.textCursor()
        old_fmt = cursor.charFormat()

        # Conditional format depending on level
        if levelno <= logging.DEBUG:  # Debug
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(12)
            fmt.setForeground(QtGui.QColor(220, 220, 220, 170))
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        elif levelno <= logging.INFO:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(50)
            fmt.setFontItalic(True)
            fmt.setForeground(QtGui.QColor(220, 220, 220, 254))
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        elif levelno <= logging.WARNING:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(50)
            fmt.setForeground(QtGui.QColor(250, 170, 0, 254))
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        elif levelno <= logging.ERROR:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(75)
            fmt.setForeground(QtGui.QColor(255, 50, 0, 254))
            cursor.setCharFormat(fmt)
            self.console.setTextCursor(cursor)

        elif levelno <= logging.CRITICAL:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(100)
            fmt.setForeground(QtGui.QColor(255, 0, 0, 254))
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

        stateToggle = QtWidgets.QCheckBox()
        stateToggle.setChecked(self._show_debug)
        stateToggle.stateChanged.connect(self.set_show_debug)

        # Assemble window
        self.console.show()
        self.move_to_end()

        mainLayout.addWidget(label1, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        mainLayout.addWidget(stateToggle, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(clearButton, 0, 2, 1, 1, QtCore.Qt.AlignRight)
        mainLayout.addWidget(self.console, 1, 0, 1, 3)
        mainLayout.setContentsMargins(2, 5, 2, 0)
        self.setLayout(mainLayout)
        self.show()
        self.resize(640, 480)
        self.hide()


def _fix_group(value, possibles):
    if str(value) not in possibles:
        return 'none'
    return str(value)


class ComboBoxDelegate(QtWidgets.QStyledItemDelegate):
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

    # That changes the displayed value but not the undelying data
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
    def __init__(self, data=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._ref_idx = 'Orig. Index'
        self._data = data.copy().reset_index(names=self._ref_idx)
        self._dtypes = self._data.dtypes

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
        row = self._data.loc[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            return str(row[col])

        elif role == Qt.EditRole:
            return row[col]

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter + Qt.AlignLeft

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
                print("Wrong dtype")
                return False

            self._data.iat[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self._data.loc[row + i] = [
                self._data[self._ref_idx].max() + 1, -1,
                'New Article Name', 1, 1, 1, 0, 'none']
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        self._data = self._data.drop(self._data.index[row]).reset_index(drop=True)
        self.endRemoveRows()


class PandasViewer(QtWidgets.QTableView):
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
            self.model().insertRows(self.model().rowCount(), 1)

        elif action == remove_row_action:
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
    def __init__(
            self, parent=None):
        super().__init__(parent)

        # Dummy init
        self.step = 1
        self.labeltext = ''
        self.delay = 1000

        # Create a horizontal layout for slider and label
        slider_layout = QtWidgets.QHBoxLayout(self)

        # Create a slider widget
        self.slider = QtWidgets.QSlider(self)
        self.slider.setSingleStep(1)   # Set step size of slider
        self.slider.valueChanged.connect(self.slider_moved)  # Connect signal to slot
        self.slider.setOrientation(Qt.Horizontal)

        self.slider_value_label = QtWidgets.QLabel(parent=self)
        # Add the slider and label to the horizontal layout
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.slider_value_label)

        # Create a timer
        self.timer = QtCore.QTimer()

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

    def setValue(self, val):
        self.slider.setValue(val)

    def setOrientation(self, val):
        self.slider.setOrientation(val)

    def setTickPosition(self, val):
        self.slider.setTickPosition(val)

    def custom_setup(self, minval=0.5, maxval=2, step=0.05,
                     label='Amount: ', value_change_delay=750,
                     def_callback=False):
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

        if def_callback:
            self.timer.timeout.connect(self.timer_callback)

    def slider_moved(self):
        self.timer.stop()  # Stop the timer if running
        slider_value = self.slider.value() * self.step
        self.slider_value_label.setText(
            f'{ self.labeltext:s}{slider_value:.2f}')
        self.timer.start()  # Start the timer again

    def timer_callback(self):
        self.timer.stop()

    def closeEvent(self, event):
        self.timer.stop()  # Stop the timer
        self.timer.deleteLater()  # Delete the timer
        event.accept()  # Accept the close event
