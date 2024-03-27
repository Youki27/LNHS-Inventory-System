from PyQt6.QtGui import QCloseEvent, QKeyEvent
from PyQt6.QtWidgets import QPushButton, QApplication,QMainWindow, QLineEdit
from PyQt6 import uic
from PyQt6.QtCore import QEvent, QObject, pyqtSignal, Qt

class Scanbarcode(QMainWindow):

    return_ = pyqtSignal()

    def __init__(self):
        super(Scanbarcode, self).__init__()

        uic.loadUi("Ui/scan_window.ui", self)

        self.barcode_box = self.findChild(QLineEdit, "barcode")
        
        self.barcode_box.keyPressEvent = self.keypress

    def closeEvent(self,event):
        self.return_.emit()
        super().closeEvent(event)

    def keypress(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            print("Enter pressed")
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = Scanbarcode()
    window.show()
    app.exec()
    
