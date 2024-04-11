from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QCheckBox, QMainWindow, QDialog, QApplication, QComboBox, QDateTimeEdit, QFileDialog
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from database import Database
import mysql.connector
import uuid, datetime, os, sys
from warning_dialog import Warning

class AddItem(QMainWindow):

    update_ = pyqtSignal()

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
        self.donor_input = self.findChild(QLineEdit, "donor_input")
        self.owner = self.findChild(QComboBox, "owner")

        self.unique_code = str(uuid.uuid4())
        current_datetime = datetime.datetime.now()

        self.barcode.setText(self.unique_code)
        self.datetime.setDateTime(current_datetime)
        self.quality.addItem("Good")
        self.quality.addItem("Bad")
        self.quality.addItem("Broken")
        self.owner.addItem("BPP")
        self.owner.addItem("COOKERY")
        self.owner.addItem("CSS")
        self.owner.addItem("EIM")
        self.owner.addItem("EPASS")
        self.owner.addItem("FBC")
        self.save_button.clicked.connect(self.saveData)

    def saveData(self):

        if not self.item_name.text():
            self.warning.setWarning("Item Name Field is Empty!")
            self.warning.show()
            return
        donor = self.donor_input.text()
        if not self.donor_input.text():
            donor = "None"

        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"INSERT INTO lnhsis.items (item_name, quality, barcode, date_added, status, donor, owner) VALUES ('{self.item_name.text()}', '{self.quality.currentText()}', '{self.barcode.text()}', '{self.datetime.text()}', 0, '{donor}', '{self.owner.currentText()}')")
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

            import os
            from barcode import codex
            from barcode.writer import ImageWriter
            from PIL import Image, ImageFont, ImageDraw

            if not os.path.exists('Barcodes'):
                os.makedirs('Barcodes')

            Code128 = codex.Code128(self.unique_code, writer = ImageWriter())

            filepath = f'Barcodes\{self.item_name.text()}_{self.barcode.text()}'

            Code128.save(filepath, options={'write_text':False})

            from printbarcode import PrintBarcode
            try:
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
                draw.text((150, 250), self.barcode.text() ,(0,0,0), font=font)
                draw.text((150, 0), self.item_name.text() ,(0,0,0), font=font)
                new_img.save(filepath+".png")

                self.print_barcode = PrintBarcode()

                self.print_barcode.print_document(filepath)
            finally:
                os.remove(f"{filepath}.png")
        
        self.update_.emit()
            

        self.close()

    def resource_path(self,relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)


    




if __name__ == "__main__":
    app = QApplication([])
    window = AddItem()
    window.show()
    app.exec()