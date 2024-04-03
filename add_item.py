from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QCheckBox, QMainWindow, QDialog, QApplication, QComboBox, QDateTimeEdit, QFileDialog
from PyQt6 import uic
from database import Database
import mysql.connector
import uuid, datetime
from warning_dialog import Warning

class AddItem(QMainWindow):

    def __init__(self):
        super(AddItem, self).__init__()

        self.warning = Warning()

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

        self.barcode = self.findChild(QLineEdit, "barcode")
        self.item_name = self.findChild(QLineEdit, "item_name")
        self.quality = self.findChild(QComboBox, "quality_box")
        self.datetime = self.findChild(QDateTimeEdit, "datetime_added")
        self.save_button = self.findChild(QPushButton, "save_button")

        self.unique_code = str(uuid.uuid4())
        current_datetime = datetime.datetime.now()

        self.barcode.setText(self.unique_code)
        self.datetime.setDateTime(current_datetime)
        self.quality.addItem("Good")
        self.quality.addItem("Bad")
        self.quality.addItem("Broken")
        self.save_button.clicked.connect(self.saveData)

    def saveData(self):

        if not self.item_name.text:
            self.warning.setWarning("Item Name Field is Empty!")
            self.warning.show()
            return

        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"INSERT INTO lnhsis.items (item_name, quality, barcode, date_added, status) VALUES ('{self.item_name.text()}', '{self.quality.currentText()}', '{self.barcode.text()}', '{self.datetime.text()}', 0)")
        except mysql.connector.Error as err:
            print("Error: ", err)

        try:
            action = f"Added the item {self.item_name.text()}"
            cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{self.datetime.text()}')")
        except mysql.connector.Error as err:
            print("Error:", err)
        connection.commit()
        db.close()
        

        self.warning.setWarning(f"{self.item_name.text()} saved! Print Barcode?")
        confirmation = self.warning.exec()

        if confirmation == QDialog.DialogCode.Accepted:
            connection = db.connect()
            cursor = connection.cursor()

            try:
                action = f"Printed the barcode for {self.item_name.text()}"
                cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{self.datetime.text()}')")
            except mysql.connector.Error as err:
                print("Error:", err)
            connection.commit()
            db.close()

            import barcode
            from barcode.writer import ImageWriter

            Code128 = barcode.get_barcode_class('code128')
            code128 = Code128(self.unique_code, writer = ImageWriter())

            filepath = f'Barcodes/{self.item_name.text()}_{self.barcode.text()}'

            code128.save(filepath, options={'write_text' : False})

            from printbarcode import PrintBarcode

            PrintBarcode.printCode(self,filepath)
            

        self.close()



    




if __name__ == "__main__":
    app = QApplication([])
    window = AddItem()
    window.show()
    app.exec()