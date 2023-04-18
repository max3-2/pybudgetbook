"""Contains helpers to run customized UI functions, e.g. better logging"""
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.pyplot import subplots
from collections.abc import Iterable
import logging
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Signal, Slot, QObject


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
