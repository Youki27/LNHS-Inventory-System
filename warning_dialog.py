from PyQt6.QtWidgets import QDialog, QLabel, QApplication
from PyQt6 import uic

class Warning(QDialog):
    def __init__(self):
        super(Warning, self).__init__()

        uic.loadUi("Ui/warning_dialog.ui", self)

        self.warning = self.findChild(QLabel,"warning_field")

    def setWarning(self,warning):
        self.warning.setText(warning)

if __name__ == "__main__":
    app = QApplication([])
    window = Warning()
    window.show()
    app.exec()