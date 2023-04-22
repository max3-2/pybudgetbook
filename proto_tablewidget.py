"""Demonstrate and test the table widget"""
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableView, QHeaderView, QMenu, QAction, QTableWidgetItem
from PyQt5.QtCore import QAbstractTableModel, Qt
from pybudgetbook.bb_io import load_with_metadata
from PyQt5.QtGui import QCursor

df = load_with_metadata(r'/Users/Max/pybudgetbook_data/data/2023/04_21_Aldi.hdf5')

# df = pd.DataFrame({'a': ['Mary', 'Jim', 'John', 'Jack'],
#                    'b': [100, 200, 300, 600],
#                    'cat': ['a', 'b', 'c', 'b']})


class pandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if index.isValid():
                if role == Qt.DisplayRole:
                    return str(self._data.iloc[index.row(), index.column()])

        elif role == Qt.EditRole:
            if index.isValid():
                return str(self._data.iloc[index.row(), index.column()])

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            this_value = self._data.iat[index.row(), index.column()]
            if isinstance(this_value, pd._libs.tslibs.timestamps.Timestamp):
                print("logger warning: Cant change datetime")
                return False

            if index.isValid():
                # TODO catch invalid typecast
                self._data.iloc[index.row(), index.column()] = value
                return True

        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def flags(self, index):
        """Set flags"""
        return Qt.ItemFlags(int(QAbstractTableModel.flags(self, index) |
                                Qt.ItemIsEditable))


class pandasView(QTableView):
    def __init__(self, data):
        QTableView.__init__(self)
        self.model = pandasModel(data)
        self.setModel(self.model)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.resize(1000, 700)

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        renameAction = QAction('Add new row', self)
        renameAction.triggered.connect(self.add_new_row)

        self.menu.addAction(renameAction)
        self.menu.popup(QCursor.pos())

    def add_new_row(self):

        prev = self.model._data.iloc[-1]
        rowPosition = self.model.rowCount()
        self.model.insertRow(rowPosition)

        self.model.setItemData(rowPosition, 1, QTableWidgetItem(prev[1]))

        # self.model.insertRow(at_row)
        # self.model._data.loc[at_row] = [prev['Date'], prev['Vendor'], -1,
        #                                 'New Name', 1, 1, 1, 1, 'none', prev['Category']]


if __name__ == '__main__':
    app = QApplication(sys.argv)

    view = pandasView(df)
    view.show()

    sys.exit(app.exec_())
