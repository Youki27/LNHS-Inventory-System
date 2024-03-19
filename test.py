from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import Qt
import sys

# Initialize the application
app = QApplication(sys.argv)

# Load the image
image = QImage('Barcodes/lmao.png')
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
    painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
    painter.setWindow(image.rect())
    painter.drawImage(0, 0, image)
    painter.end()