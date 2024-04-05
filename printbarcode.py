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

        

    def print_document(self, filepath):
        self.image = QImage(filepath)
        printer = QPrinter()
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

        try:
            action = f"Printed "
            current_datetime = datetime.datetime.now()
            cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{current_user[0]}', '{action}', '{current_datetime}')")
        except mysql.connector.Error as err:
            print("Error:", err)
        connection.commit()
        db.close()

        painter = QPainter(printer)
        rect = painter.viewport()
        size = self.image.size()
        size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
        painter.setViewport(int(rect.x()/3), int(rect.y()/3), int(size.width()/3), int(size.height()/3))
        painter.setWindow(self.image.rect())
        painter.drawImage(0, 0, self.image)
        painter.end()

def main():
    app = QApplication(sys.argv)
    window = PrintBarcode()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()