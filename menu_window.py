from PyQt6.QtWidgets import QPushButton, QApplication,QMainWindow
from PyQt6 import uic
from user_management_window import User_Mngmnt
from item_management_window import Item_Mngmnt
from PyQt6.QtCore import pyqtSignal

class Main_menu(QMainWindow):

    closed_to_login = pyqtSignal()

    def __init__(self):
        super(Main_menu, self).__init__()

        uic.loadUi("Ui/Management_Window.ui", self)

        self.users_button = self.findChild(QPushButton, "user_button")
        self.items_button = self.findChild(QPushButton, "items_button")
        self.barcode_button = self.findChild(QPushButton, "barcode_button")
        self.logs_button = self.findChild(QPushButton, "logs_button")
        self.logout_button = self.findChild(QPushButton, "logout_button")

        self.users_button.clicked.connect(self.manage_users)
        self.items_button.clicked.connect(self.manage_items)
        self.logout_button.clicked.connect(self.logout)

        self.usr_mng_window = User_Mngmnt()
        self.usr_mng_window.return_.connect(self.show)
        self.itm_mng_window = Item_Mngmnt()
        self.itm_mng_window.return_.connect(self.show)

    def closeEvent(self, event):
        self.closed_to_login.emit()
        super().closeEvent(event)

    def manage_users(self):
        self.usr_mng_window.show()
        self.hide()

    def manage_items(self):
        self.itm_mng_window.show()
        self.hide()

    def logout(self):
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    window = Main_menu()
    window.show()
    app.exec()