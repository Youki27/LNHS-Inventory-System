from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6 import uic
import mysql.connector
from warning_dialog import Warning
# Assuming database.py and its Database class are correctly implemented
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

    def verifyBarcode(self):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM lnhsis.items WHERE barcode = %s", (self.barcode_box.text(),))
        except mysql.connector.Error as err:
            print("Error:", err)

        results = cursor.fetchall()
        db.close()

        if results:
            from input_borrower import BorrowerInfo
            self.borrower_info_window = BorrowerInfo()
            self.borrower_info_window.addBorrowerInfo(self.barcode_box.text())
            self.barcode_box.setText("")
            self.borrower_info_window.show()
        else:
            self.warning.setWarning("No Items Found!")
            self.warning.show()

if __name__ == "__main__":
    app = QApplication([])
    window = Scanbarcode()
    window.show()
    app.exec()

