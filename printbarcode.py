from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import Qt
import sys

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
            painter = QPainter(printer)
            rect = painter.viewport()
            size = image.size()
            size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
            painter.setViewport(int(rect.x()/3), int(rect.y()/3), int(size.width()/3), int(size.height()/3))
            painter.setWindow(image.rect())
            painter.drawImage(0, 0, image)
            painter.end()

