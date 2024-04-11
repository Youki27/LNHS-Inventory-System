from PyQt6.QtGui import QCloseEvent, QFocusEvent, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QPushButton, QMainWindow, QApplication, QLineEdit,QTableView, QHeaderView, QDialog
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, QModelIndex
from add_item import AddItem
from edit_item import EditItems
from database import Database
import mysql.connector, datetime, os, sys

class Item_Mngmnt(QMainWindow):

    return_ = pyqtSignal()

    def __init__(self):
        super(Item_Mngmnt, self).__init__()

        uic.loadUi("Ui/items_window.ui", self)

        self.return_button = self.findChild(QPushButton, "return_button")
        self.add_items_button = self.findChild(QPushButton, "add_items_button")
        self.refresh_button = self.findChild(QPushButton, "refresh_button")
        self.main_table = self.findChild(QTableView, "main_table")
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.search_bar = self.findChild(QLineEdit, "search_bar")
        self.search_button = self.findChild(QPushButton, "search_button")
        self.print_table = self.findChild(QPushButton, "print_table")

        self.return_button.clicked.connect(self.close)
        self.add_items_button.clicked.connect(self.addItem)
        self.refresh_button.clicked.connect(self.loadItems)
        self.search_button.clicked.connect(self.loadSearchedItem)
        self.datetime = datetime.datetime.now()
        self.print_table.clicked.connect(self.printTable)

        
        self.add_item_window = AddItem()
        self.add_item_window.update_.connect(self.loadItems)
        self.edit_item_window = EditItems()
        self.edit_item_window.update_.connect(self.loadItems)
        self.loadItems()

    def closeEvent(self, event):
        self.return_.emit()
        super().closeEvent(event)

    def addItem(self):
        self.add_item_window = AddItem()
        self.add_item_window.show()

    def loadItems(self):
        db =  Database()

        connection = db.connect()
        cursor = connection.cursor()
        
        try:
            cursor.execute(f"SELECT item_name, quality, barcode, date_added,donor,status, owner FROM lnhsis.items")
        except mysql.connector.Error as err:
            print("Error:", err)

        results = cursor.fetchall()
        connection.close()
        self.model = QStandardItemModel(0,6)
        self.model.setHorizontalHeaderLabels(['Item','Quality','Barcode', 'Date Added','Status','Borrower','Donor','Owner','','',''])

        items = []
        for row in results:
            stat = 'Available'
            name = ''
            if row[5]:
                stat = 'Borrowed'
                connection = db.connect()
                cursor = connection.cursor()
                try:
                    cursor.execute(f"SELECT borrower_name FROM lnhsis.borrowers WHERE barcode = '{row[2]}' AND date_returned IS NULL")
                except mysql.connector.Error as err:
                    print("Error: ", err)

                borrower = cursor.fetchone()
                connection.close()
                name = borrower[0]

            items = [
                QStandardItem(row[0]),
                QStandardItem(row[1]),
                QStandardItem(row[2]),
                QStandardItem(str(row[3])),
                QStandardItem(stat),
                QStandardItem(name),
                QStandardItem(row[4]),
                QStandardItem(row[6])
            ]
            items.append(QStandardItem("Edit"))
            items.append(QStandardItem("Delete"))
            items.append(QStandardItem("Print"))
            self.model.appendRow(items)

        self.view = self.main_table
        self.view.setModel(self.model)
        self.view.setColumnWidth(0, 175)
        self.view.setColumnWidth(1, 75)
        self.view.setColumnWidth(2, 250)
        self.view.setColumnWidth(3, 150)
        self.view.setColumnWidth(5, 175)
        self.view.setColumnWidth(6, 125)
        self.view.setColumnWidth(7, 50)
        self.view.setColumnWidth(8, 50)
        self.view.setColumnWidth(9, 50)
        self.view.setColumnWidth(10, 50)
        self.main_table.selectionModel().selectionChanged.connect(self.tableItemClicked)

    def printTable(self):
        
        from print_table import PrintTable

        self.print_ = PrintTable()
        self.print_.print_document(self.view)

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
        donor_index = self.model.index(selected_item.row(),6)
        owner_index = self.model.index(selected_item.row(),7)

        selected_itemname = self.model.data(itemname_index)
        selected_quality = self.model.data(quality_index)
        selected_barcode = self.model.data(barcode_index)
        selected_date = self.model.data(date_index)
        selected_status = self.model.data(status_index)
        selected_borrower = self.model.data(borrower_index)
        selected_donor = self.model.data(donor_index)
        selected_owner = self.model.data(owner_index)

        if selected_item_data == "Edit":

            creds = [selected_itemname, selected_quality, selected_barcode, selected_date, selected_status, selected_borrower, selected_donor, selected_owner]

            
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

                try:
                    action = f"Deleted the item {selected_itemname}"
                    cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{self.datetime}')")
                except mysql.connector.Error as err:
                    print("Error:", err)
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
            import os
            from barcode import codex
            from barcode.writer import ImageWriter
            from PIL import Image, ImageFont, ImageDraw

            if not os.path.exists('Barcodes'):
                os.makedirs('Barcodes')

            filepath = f'Barcodes/{selected_itemname}_{selected_barcode}'

            try:
                Code128 = codex.Code128(selected_barcode, writer=ImageWriter())

                Code128.save(filepath, options={'write_text':False})
                img = Image.open(filepath+".png")
                
                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except IOError:
                    font = ImageFont.load_default()

                width, height = img.size
                new_height = height+100

                new_img = Image.new('RGB', (width, new_height), 'white')
                new_img.paste(img, (0,50))

                draw = ImageDraw.Draw(new_img)
                draw.text((150, 250), selected_barcode ,(0,0,0), font=font)
                draw.text((150, 0), selected_itemname ,(0,0,0), font=font)
                new_img.save(filepath+".png")
                
                from printbarcode import PrintBarcode

                self.printBarcode = PrintBarcode()
                self.printBarcode.print_document(filepath)
            finally:
                os.remove(f"{filepath}.png")

    def resource_path(self,relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def showEvent(self, event):
        super().showEvent(event)
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT user FROM lnhsis.logs ORDER BY log_date DESC LIMIT 1")
        except mysql.connector.Error as err:
            print("Error:", err)

        self.current_user = cursor.fetchone()
        db.close()
        self.loadItems()

    def loadSearchedItem(self):
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        tbsearched = self.search_bar.text()
        status = 0
        if tbsearched.lower() == 'available':
            status = 0
        elif tbsearched.lower() == 'borrowed':
            status = 1
        else:
            status = 2

        try:
            cursor.execute(f"SELECT * FROM lnhsis.items WHERE item_name LIKE '%{tbsearched}%' OR quality LIKE '%{tbsearched}%' OR barcode LIKE '%{tbsearched}%' OR status = {status} OR donor LIKE '%{tbsearched}%' OR owner LIKE '%{tbsearched}%'")
        except mysql.connector.Error as err:
            print("Error:", err)
            connection.rollback()

        results = cursor.fetchall()
            
        db.close()

        self.model.removeRows(0, self.model.rowCount())


        for row in results:
            stat = 'Available'
            name = ''
            if row[5]:
                stat = 'Borrowed'
                
                connection = db.connect()
                cursor = connection.cursor()
                try:
                    cursor.execute(f"SELECT borrower_name FROM lnhsis.borrowers WHERE barcode = '{row[3]}' AND date_returned IS NULL")
                except mysql.connector.Error as err:
                    print("Error: ", err)

                borrower = cursor.fetchone()
                connection.close()
                name = borrower[0]

            items = [
                QStandardItem(row[1]),
                QStandardItem(row[2]),
                QStandardItem(row[3]),
                QStandardItem(str(row[4])),
                QStandardItem(stat),
                QStandardItem(name),
                QStandardItem(row[6]),
                QStandardItem(row[7])
            ]
            items.append(QStandardItem("Edit"))
            items.append(QStandardItem("Delete"))
            items.append(QStandardItem("Print"))
            self.model.appendRow(items)

        self.view.setModel(self.model)

if __name__ == "__main__":
    app = QApplication([])
    window = Item_Mngmnt()
    window.show()
    app.exec()