import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt6.QtGui import QImage, QPainter,QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtSvg import QSvgRenderer
from database import Database
import sys, mysql.connector, datetime

class PrintBarcode(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        

    def print_document(self, filepaths):

        self.filepaths = filepaths

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.paintRequested.connect(self.print_request)
        preview_dialog.exec()

    def print_request(self, printer):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT user FROM lnhsis.logs ORDER BY log_date DESC LIMIT 1;")
        except mysql.connector.Error as err:
            print("Error:", err)

        current_user = cursor.fetchone()

        for filepath in self.filepaths:
            try:
                action = f"Printed the ff: {filepath}"
                current_datetime = datetime.datetime.now()
                cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{current_user[0]}', '{action}', '{current_datetime}')")
            except mysql.connector.Error as err:
                print("Error:", err)
        connection.commit()
        db.close()

        painter = QPainter(printer)

        images_per_page = 14
        margin = 50
        img_size = (printer.pageRect(QPrinter.Unit.DevicePixel).width() - 2 * margin) // 2  # Max two images per row
        img_height = (printer.pageRect(QPrinter.Unit.DevicePixel).height() - 2 * margin) // round(images_per_page/2)
        y_offset = margin
        
        for i, filepath in enumerate(self.filepaths):
            if i > 0 and i % images_per_page == 0:
                printer.newPage()  # Start a new page after 5 images
                y_offset = margin  # Reset the vertical position

            # Load the image
            pixmap = QPixmap(filepath)
            pixmap = pixmap.scaled(img_size, img_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            # Determine the position for the image
            x = margin if i % 2 == 0 else (printer.pageRect(QPrinter.Unit.DevicePixel).width() // 2) + margin // 2
            painter.drawPixmap(x, y_offset, pixmap)

            # Move down the vertical offset every 2 images
            if i % 2 == 1:
                y_offset += img_height + margin

        painter.end()

def main():
    app = QApplication(sys.argv)
    window = PrintBarcode()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()