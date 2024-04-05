import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QPageLayout
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

class PrintTable(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        

    def print_document(self, table):

        self.table = table
        printer = QPrinter()
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.paintRequested.connect(self.print_preview)
        preview_dialog.exec()

    def print_preview(self, printer):
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        self.table.render(printer)

def main():
    app = QApplication(sys.argv)
    window = PrintTable()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
