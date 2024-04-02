from PyQt6.QtGui import QCloseEvent, QStandardItem, QStandardItemModel
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
    '''
    def tableItemClicked(self, item:QModelIndex):

        selected_item = ""

        for index in item.indexes():
            selected_item = index
        
        if isinstance(selected_item, str):
            return

        selected_item_data = selected_item.data()

        itemname_index = self.model.index(selected_item.row(),0)
        quality_index = self.model.index(selected_item.row(),1)
        barcode_index = self.model.index(selected_item.row(),2)
        date_index = self.model.index(selected_item.row(),3)
        status_index = self.model.index(selected_item.row(),4)
        borrower_index = self.model.index(selected_item.row(),5)

        selected_itemname = self.model.data(itemname_index)
        selected_quality = self.model.data(quality_index)
        selected_barcode = self.model.data(barcode_index)
        selected_date = self.model.data(date_index)
        selected_status = self.model.data(status_index)
        selected_borrower = self.model.data(borrower_index)

        if selected_item_data == "Edit":

            creds = [selected_itemname, selected_quality, selected_barcode, selected_date, selected_status, selected_borrower]

            from edit_item import EditItems

            self.edit_item_window = EditItems()
            self.edit_item_window.editItem(creds)
            self.edit_item_window.show()
            
        if selected_item_data == "Delete":
            
            from warning_dialog import Warning

            self.warning = Warning()

            self.warning.setWarning(f"Delete {selected_itemname} and their data?")

            res = self.warning.exec()

            if res == QDialog.DialogCode.Accepted:
                db = Database()

                connection = db.connect()
                cursor = connection.cursor()

                try:
                    cursor.execute(f"SELECT item_id FROM lnhsis.items WHERE barcode = '{selected_barcode}'")
                except mysql.connector.Error as err:
                    print("Error 1: ", err)

                result = cursor.fetchall()


                for item in result:
                    try:
                        cursor.execute(f"DELETE FROM lnhsis.items WHERE item_id = {item[0]}")
                    except mysql.connector.Error as err:
                        print("Error 2: ", err)
                        connection.rollback()
                    connection.commit()

                db.close()
                self.warning.setWarning(f"{selected_itemname} was Deleted Successfully")
                self.warning.show()
                self.loadItems()

            else:
                self.warning.setWarning("Deletion Cancelled!")
                self.warning.show()

        if selected_item_data == "Print":



            from printbarcode import PrintBarcode
            import barcode, os
            from barcode.writer import ImageWriter

            filepath = f'Barcodes/{selected_itemname}_{selected_barcode}'

            if os.path.exists(filepath) and os.path.isfile(filepath):
                PrintBarcode.printCode(self,filepath)
                return

            Code128 = barcode.get_barcode_class('code128')
            code128 = Code128(selected_barcode, writer = ImageWriter())

            code128.save(filepath, options={'write_text' : True})

            from printbarcode import PrintBarcode

            PrintBarcode.printCode(self,filepath)
    '''        
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