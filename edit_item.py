from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QMainWindow, QApplication, QComboBox, QDateTimeEdit
from PyQt6 import uic
from database import Database
import mysql.connector
from warning_dialog import Warning
from datetime import datetime

class EditItems(QMainWindow):
    
    def __init__(self):
        super(EditItems, self).__init__()

        uic.loadUi("Ui/add_item_window.ui", self)

        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT user FROM lnhsis.logs ORDER BY log_date DESC LIMIT 1")
        except mysql.connector.Error as err:
            print("Error:", err)

        self.current_user = cursor.fetchone()
        db.close()

        self.warning = Warning()

        self.barcode = self.findChild(QLineEdit, "barcode")
        self.item_name = self.findChild(QLineEdit, "item_name")
        self.quality = self.findChild(QComboBox, "quality_box")
        self.datetime = self.findChild(QDateTimeEdit, "datetime_added")
        self.save_button = self.findChild(QPushButton, "save_button")
        self.label = self.findChild(QLabel, "label")

        self.quality.addItem("Good")
        self.quality.addItem("Bad")
        self.quality.addItem("Broken")

        self.label.setText("Edit User")

        self.save_button.clicked.connect(self.saveEdit)

    def editItem(self, creds):

        self.item = creds[0]
        self.qual = creds[1]
        self.brcd = creds[2]
        self.date = creds[3]
        self.stat = creds[4]
        self.borrower = creds[5]

        self.curr_datetime = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")

        self.item_name.setText(self.item)
        self.quality.setCurrentText(self.qual)
        self.barcode.setText(self.brcd)
        self.datetime.setDateTime(self.curr_datetime)

    def saveEdit(self):

        if not self.verifyItem():
            return
        
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        if self.item_name.text() != self.item or self.quality.currentText() != self.qual or self.datetime.text() != self.date:
            try:
                cursor.execute(f"SELECT item_id FROM lnhsis.items WHERE item_name = '{self.item}'")
            except mysql.connector.Error as err:
                print("Error: ", err)

            item_id = cursor.fetchall()

            try:
                cursor.execute(f"UPDATE lnhsis.items SET item_name = '{self.item_name.text()}', quality = '{self.quality.currentText()}', date_added = '{self.datetime.text()}' WHERE item_id = {item_id[0][0]}")
            except mysql.connector.Error as err:
                print("Error:", err)

            connection.commit()

        try:
            action = f"Edited the item with the barcode {self.brcd}"
            cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{self.datetime.text()}')")
        except mysql.connector.Error as err:
            print("Error:", err)
        connection.commit()
        db.close()


        db.close()
        self.close()
        self.warning.setWarning("Edit Saved!")
        self.warning.show()

        
    def verifyItem(self):

        if not self.item_name.text():
            self.warning.setWarning("Item Name Field is empty!")
            self.warning.show()
            return
        
        return True

        
if __name__ == "__main__":
    app = QApplication([])
    window = EditItems()
    window.show()
    app.exec()