from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6 import uic
import mysql.connector, datetime
from warning_dialog import Warning
from database import Database

class CustomLineEdit(QLineEdit):
    enter_pressed = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enter_pressed.emit()
        else:
            super().keyPressEvent(event)

class Scanbarcode(QMainWindow):
    return_ = pyqtSignal()

    def __init__(self):
        super(Scanbarcode, self).__init__()

        uic.loadUi("Ui/scan_window.ui", self)

        self.warning = Warning()

        self.vBox = self.findChild(QVBoxLayout, "verticalLayout")
        self.barcode_box = CustomLineEdit(self)
        self.vBox.addWidget(self.barcode_box)
        self.barcode_box.setObjectName("barcode")
        self.barcode_box.enter_pressed.connect(self.verifyBarcode)

        self.barcode_box.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.barcode_box.setPlaceholderText("Barcode ...")
        self.barcode_box.setStyleSheet("Background-color:white;color:#333333;")

    def closeEvent(self, event):
        self.return_.emit()
        super().closeEvent(event)

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

    def verifyBarcode(self):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT status,item_id FROM lnhsis.items WHERE barcode = %s", (self.barcode_box.text(),))
        except mysql.connector.Error as err:
            print("Error:", err)

        results = cursor.fetchone()
        db.close()

        if results:

            if results[0]:
                connection = db.connect()
                cursor = connection.cursor()
                try:
                    cursor.execute(f"UPDATE lnhsis.items SET status = 0 WHERE item_id = {results[1]};")
                    connection.commit()
                    cursor.execute(f"SELECT bid FROM lnhsis.borrowers WHERE barcode = '{self.barcode_box.text()}' AND date_returned IS NULL;")
                except mysql.connector.Error as err:
                    print("Error: ", err)

                bid = cursor.fetchone()

                current_datetime = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                try:
                    cursor.execute(f"UPDATE lnhsis.borrowers SET date_returned = '{current_datetime}' WHERE bid = {bid[0]};")
                    connection.commit()
                except mysql.connector.Error as err:
                    print("Error 2:", err)

                try:
                    action = f"Item with the barcode {self.barcode_box.text()} returned."
                    cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{current_datetime}')")
                except mysql.connector.Error as err:
                    print("Error:", err)
                connection.commit()

                db.close()

                self.warning.setWarning("Item Returned!")
                self.warning.show()
                self.barcode_box.setText('')
                return
            try:
                from termcond import TermsAndCondition
                self.terms_condition = TermsAndCondition()
                self.terms_condition.show()
            finally:
                self.terms_condition.action.connect(self.addBorrower)
                    
        else:
            self.warning.setWarning("No Items Found!")
            self.warning.show()

    def addBorrower(self):
        from input_borrower import BorrowerInfo
        self.borrower_info_window = BorrowerInfo()
        self.borrower_info_window.addBorrowerInfo(self.barcode_box.text())
        self.barcode_box.setText("")
        self.borrower_info_window.show()

if __name__ == "__main__":
    app = QApplication([])
    window = Scanbarcode()
    window.show()
    app.exec()

