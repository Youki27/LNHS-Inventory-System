from PyQt6.QtGui import QCloseEvent, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QPushButton, QMainWindow, QApplication, QLineEdit,QTableView, QHeaderView, QDialog
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, QModelIndex
from add_item import AddItem
from database import Database
import mysql.connector

class ViewLogs(QMainWindow):

    return_ = pyqtSignal()

    def __init__(self):
        super(ViewLogs, self).__init__()

        uic.loadUi("Ui/items_window.ui", self)

        self.return_button = self.findChild(QPushButton, "return_button")
        self.add_items_button = self.findChild(QPushButton, "add_items_button")
        self.refresh_button = self.findChild(QPushButton, "refresh_button")
        self.main_table = self.findChild(QTableView, "main_table")
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.search_bar = self.findChild(QLineEdit, "search_bar")
        self.search_button = self.findChild(QPushButton, "search_button")

        self.return_button.clicked.connect(self.close)
        self.add_items_button.setVisible(False)
        self.refresh_button.clicked.connect(self.loadLogs)
        self.search_button.clicked.connect(self.loadSearchedItem)

        self.loadLogs()

    def closeEvent(self, event):
        self.return_.emit()
        super().closeEvent(event)

    def loadLogs(self):
        db =  Database()

        connection = db.connect()
        cursor = connection.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM lnhsis.logs")
        except mysql.connector.Error as err:
            print("Error:", err)

        results = cursor.fetchall()
        connection.close()

        self.model = QStandardItemModel(0,3)
        self.model.setHorizontalHeaderLabels(['User','Actions','Date Time'])

        items = []
        for row in results:

            items = [
                QStandardItem(row[1]),
                QStandardItem(row[2]),
                QStandardItem(str(row[3]))
            ]
            self.model.appendRow(items)

        self.view = self.main_table
        self.view.setModel(self.model)
        #self.main_table.selectionModel().selectionChanged.connect(self.tableItemClicked)    
    def loadSearchedItem(self):
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        tbsearched = self.search_bar.text()

        try:
            cursor.execute(f"SELECT * FROM lnhsis.logs WHERE user LIKE '%{tbsearched}%' OR action LIKE '%{tbsearched}%'")
        except mysql.connector.Error as err:
            print("Error:", err)
            connection.rollback()

        results = cursor.fetchall()
            
        db.close()

        self.model.removeRows(0, self.model.rowCount())


        
        for row in results:

            items = [
                QStandardItem(row[1]),
                QStandardItem(row[2]),
                QStandardItem(str(row[3])),
            ]
            self.model.appendRow(items)

        self.view = self.main_table
        self.view.setModel(self.model)

if __name__ == "__main__":
    app = QApplication([])
    window = ViewLogs()
    window.show()
    app.exec()