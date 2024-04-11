from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QCheckBox, QPushButton
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from warning_dialog import Warning

class TermsAndCondition(QMainWindow):
    action = pyqtSignal()

    def __init__(self):
        super(TermsAndCondition, self).__init__()

        self.warning = Warning()

        uic.loadUi("Ui/terms_and_condition.ui", self)

        self.accept = self.findChild(QCheckBox, "checkBox")
        self.cont = self.findChild(QPushButton, "pushButton")
        self.terms = self.findChild(QTextEdit, "textEdit")

        self.cont.clicked.connect(self.cont_to_borrow)

    def cont_to_borrow(self):

        if not self.accept.isChecked():
            self.warning.setWarning("You must Accept the Terms and Conditions to Continue.")
            self.warning.show()
            return
        
        self.close()
        self.action.emit()

if __name__ == "__main__":
    app = QApplication([])
    window = TermsAndCondition()
    window.show()
    app.exec()