from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import Qt
from database import Database
import sys, mysql.connector, datetime

class PrintBarcode(QPrintDialog):

    def __init__(self):
        super(PrintBarcode, self).__init__()

    def printCode(self, filepath):
        image = QImage(filepath)

        if image.isNull():
            QMessageBox.information(None, "Image Viewer", "Cannot load the image.")
            sys.exit(1)

        # Prepare the printer
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer)

        # Show the print dialog
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:

            db = Database()
            connection = db.connect()
            cursor = connection.cursor()

            try:
                cursor.execute("SELECT user FROM lnhsis.logs ORDER BY log_date DESC LIMIT 1;")
            except mysql.connector.Error as err:
                print("Error:", err)

            current_user = cursor.fetchone()

            try:
                action = f"Printed {filepath}"
                current_datetime = datetime.datetime.now()
                cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{current_user[0]}', '{action}', '{current_datetime}')")
            except mysql.connector.Error as err:
                print("Error:", err)
            connection.commit()
            db.close()

            painter = QPainter(printer)
            rect = painter.viewport()
            size = image.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
            painter.setViewport(int(rect.x()/3), int(rect.y()/3), int(size.width()/3), int(size.height()/3))
            painter.setWindow(image.rect())
            painter.drawImage(0, 0, image)
            painter.end()

