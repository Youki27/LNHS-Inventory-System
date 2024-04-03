from PyQt6.QtGui import QCloseEvent, QShowEvent, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QPushButton, QMainWindow, QApplication, QLineEdit,QTableView, QHeaderView, QDialog
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, QModelIndex
from add_item import AddItem
from database import Database
import mysql.connector

class Borrower_Mngmnt(QMainWindow):

    return_ = pyqtSignal()

    def __init__(self):
        super(Borrower_Mngmnt, self).__init__()

        uic.loadUi("Ui/items_window.ui", self)

        self.return_button = self.findChild(QPushButton, "return_button")
        self.add_items_button = self.findChild(QPushButton, "add_items_button")
        self.refresh_button = self.findChild(QPushButton, "refresh_button")
        self.main_table = self.findChild(QTableView, "main_table")
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.search_bar = self.findChild(QLineEdit, "search_bar")
        self.search_button = self.findChild(QPushButton, "search_button")

        self.return_button.clicked.connect(self.close)
        self.add_items_button.setVisible(False)
        self.refresh_button.clicked.connect(self.loadItems)
        self.search_button.clicked.connect(self.loadSearchedItem)

        self.loadItems()

    def closeEvent(self, event):
        self.return_.emit()
        super().closeEvent(event)

    def loadItems(self):
        db =  Database()

        connection = db.connect()
        cursor = connection.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM lnhsis.borrowers")
        except mysql.connector.Error as err:
            print("Error:", err)

        results = cursor.fetchall()
        connection.close()
        
        self.model = QStandardItemModel(0,6)
        self.model.setHorizontalHeaderLabels(['Name','Address','Item', 'Barcode','Purpose','Date Borrowed','Estimated Return','Returned Date'])

        items = []
        for row in results:

            items = [
                QStandardItem(row[1]),
                QStandardItem(row[2]),
                QStandardItem(row[3]),
                QStandardItem(row[4]),
                QStandardItem(row[5]),
                QStandardItem(str(row[6])),
                QStandardItem(str(row[7])),
                QStandardItem(str(row[8]))
            ]
            self.model.appendRow(items)

        self.view = self.main_table
        self.view.setModel(self.model)
        #self.main_table.selectionModel().selectionChanged.connect(self.tableItemClicked)

    def showEvent(self, event):
        super().showEvent(event)
        self.loadItems()

    def loadSearchedItem(self):
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        tbsearched = self.search_bar.text()

        try:
            cursor.execute(f"SELECT * FROM lnhsis.borrowers WHERE borrower_name LIKE '%{tbsearched}%' OR borrower_address LIKE '%{tbsearched}%' OR barcode LIKE '%{tbsearched}%' OR borrowed_item LIKE '%{tbsearched}%'")
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
                QStandardItem(row[3]),
                QStandardItem(row[4]),
                QStandardItem(row[5]),
                QStandardItem(str(row[6])),
                QStandardItem(str(row[7])),
                QStandardItem(str(row[8]))
            ]
            self.model.appendRow(items)

        self.view = self.main_table
        self.view.setModel(self.model)

if __name__ == "__main__":
    app = QApplication([])
    window = Borrower_Mngmnt()
    window.show()
    app.exec()