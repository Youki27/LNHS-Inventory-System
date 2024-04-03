from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit, QMainWindow, QDialog, QApplication, QComboBox, QDateTimeEdit, QFileDialog
from PyQt6 import uic
from database import Database
import mysql.connector
import datetime
from warning_dialog import Warning

class BorrowerInfo(QMainWindow):

    def __init__(self):
        super(BorrowerInfo, self).__init__()

        uic.loadUi("Ui/borrower_window.ui", self)

        self.warning = Warning()

        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT user FROM lnhsis.logs ORDER BY log_date LIMIT 1")
        except mysql.connector.Error as err:
            print("Error:", err)

        self.current_user = cursor.fetchone()
        db.close()

        self.barcode = self.findChild(QLineEdit, "barcode")
        self.item_name = self.findChild(QLineEdit, "item_name")
        self.borrower = self.findChild(QLineEdit, "borrower")
        self.address = self.findChild(QLineEdit, "address")
        self.date_borrowed = self.findChild(QDateTimeEdit, "date_borrowed")
        self.date_to_return = self.findChild(QDateTimeEdit, "date_to_return")
        self.purpose = self.findChild(QTextEdit, "purpose")
        self.save_button = self.findChild(QPushButton, "save_button")

    def addBorrowerInfo(self, barcode):

        self.current_datetime = datetime.datetime.now()

        self.barcode.setText(barcode)
        self.date_borrowed.setDateTime(self.current_datetime)
        self.date_to_return.setDateTime(self.current_datetime)

        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT item_name FROM lnhsis.items WHERE barcode = '{barcode}'")
        except mysql.connector.Error as err:
            print("Error: ", err)

        result = cursor.fetchone()
        
        db.close()

        self.item_name.setText(result[0])

        self.save_button.clicked.connect(self.saveData)

    def saveData(self):

        if not self.borrower.text():
            self.warning.setWarning("Borrower Field is Empty!")
            self.warning.show()
            return
        if not self.address.text():
            self.warning.setWarning("Address Field is Empty!")
            self.warning.show()
            return
        if not self.purpose.toPlainText():
            self.warning.setWarning("Purpose Field is Empty!")
            self.warning.show()
            return
        
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()
        try:
            cursor.execute(f"INSERT INTO lnhsis.borrowers (borrower_name, borrower_address, borrowed_item, barcode, purpose, date_borrowed, date_return_estimate) VALUES ('{self.borrower.text()}','{self.address.text()}', '{self.item_name.text()}', '{self.barcode.text()}', '{self.purpose.toPlainText()}', '{self.date_borrowed.text()}', '{self.date_to_return.text()}');")
        except mysql.connector.Error as err:
            print("Error: ", err)

        connection.commit()

        try:
            cursor.execute(f"SELECT item_id FROM lnhsis.items WHERE barcode = '{self.barcode.text()}'")
            item_id = cursor.fetchone()
            cursor.execute(f"UPDATE lnhsis.items SET status = 1 WHERE item_id = {item_id[0]}")
        except mysql.connector.Error as err:
            print("Error: ", err)
        
        connection.commit()

        try:
            action = f"Item {self.item_name.text()} with the barcode {self.barcode.text()} was borrowed by {self.borrower.text()}"
            cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{self.current_datetime}')")
        except mysql.connector.Error as err:
            print("Error:", err)
        connection.commit()

        db.close()
        self.warning.setWarning("Borrower Data Saved!")
        self.warning.show()
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    window = BorrowerInfo()
    window.show()
    app.exec()