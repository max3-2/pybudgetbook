"""Test pyqt df display"""
import pandas as pd
import numpy as np
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QHeaderView, QAbstractItemView, QApplication, QTableView, QVBoxLayout, QWidget, QComboBox, QMenu, QStyledItemDelegate
from PySide6.QtGui import QPalette, QColor


_possible_groups = ['Type 1', 'Type C', 'Täst', 'none']


def _fix_group(value):
    if str(value) not in _possible_groups:
        return _possible_groups[-1]
    return str(value)


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ComboBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(_possible_groups)
        combo.setAutoFillBackground(True)
        return combo

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if str(value) in _possible_groups:
            editor.setCurrentText(
                _possible_groups[_possible_groups.index(str(value))])
        else:
            editor.setCurrentText(_possible_groups[-1])

    # That changes the displayed value but not the undelying data
    def displayText(self, value, locale):
        if str(value) in _possible_groups:
            return _possible_groups[_possible_groups.index(str(value))]
        else:
            return _possible_groups[-1]

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def paint(self, painter, option, index):
        value = str(index.model().data(index, Qt.DisplayRole))

        if value == 'none':
            painter.fillRect(option.rect, QColor(255, 0, 0, 170))
            option.font.setBold(True)
            option.palette.setColor(QPalette.Text, QColor(240, 240, 240))

        super().paint(painter, option, index)


class MyTableModel(QAbstractTableModel):
    def __init__(self, data=None, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._ref_idx = 'Orig. Index'
        self._data = data.copy().reset_index(names=self._ref_idx)
        self._dtypes = self._data.dtypes

        # Fix invalid group columns
        self._data['Group'] = self._data['Group'].apply(_fix_group)

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

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
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

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self._data.loc[row + i] = [
                self._data[self._ref_idx].max() + 1, 'New Date', 0, 'New name', 'Option 1']
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        self._data = self._data.drop(self._data.index[row]).reset_index(drop=True)
        self.endRemoveRows()


class MyTableView(QTableView):
    def __init__(self, model, parent=None, vert_header=False):
        QTableView.__init__(self, parent)
        self._combo_delegate = None

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.setModel(model)
        self.setSortingEnabled(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.model().sort)

        self.verticalHeader().setDefaultSectionSize(18)
        self.verticalHeader().setMinimumSectionSize(18)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setVisible(vert_header)

        self.model().sort(0)

    def showContextMenu(self, pos):
        menu = QMenu(self)
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

    def set_combo_column(self, column):
        self._combo_delegate = ComboBoxDelegate(self)
        self.setItemDelegateForColumn(column, self._combo_delegate)

    def get_final_data(self, remove_orig_index=True):
        if remove_orig_index:
            return self.model()._data.copy().drop(
                columns=[self.model()._ref_idx])
        else:
            return self.model()._data.copy()


if __name__ == '__main__':
    dataframe = pd.DataFrame(columns=['Date', 'id', 'Name', 'Group'])
    dataframe.loc[0] = ['Date value 1', 3, 'Name one', 'Type C']
    dataframe.loc[1] = ['Date value 2', 4., 'Name two', 'none']
    dataframe.loc[2] = ['Date value 3', 5, 'Name three', 'notpossbible']

    if QApplication.instance() is None:
        app = QApplication([])

    table_model = MyTableModel(dataframe)
    table_view = MyTableView(table_model)

    table_view.set_combo_column(4)

    layout = QVBoxLayout()
    layout.addWidget(table_view)

    widget = QWidget()
    widget.setLayout(layout)
    widget.setGeometry(50, 50, 600, 400)
    widget.show()
    widget.activateWindow()

    import sys
    sys.exit(app.exec())
