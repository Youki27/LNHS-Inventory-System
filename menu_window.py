from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QPushButton, QApplication,QMainWindow
from PyQt6 import uic
from user_management_window import User_Mngmnt
from item_management_window import Item_Mngmnt
from borrower_management_window import Borrower_Mngmnt
from log_window import ViewLogs
from scan_barcode import Scanbarcode
from PyQt6.QtCore import pyqtSignal
from database import Database
from warning_dialog import Warning
import mysql.connector, datetime

class Main_menu(QMainWindow):

    closed_to_login = pyqtSignal()

    def __init__(self):
        super(Main_menu, self).__init__()

        uic.loadUi("Ui/Management_Window.ui", self)

        self.warning = Warning()

        self.users_button = self.findChild(QPushButton, "user_button")
        self.items_button = self.findChild(QPushButton, "items_button")
        self.barcode_button = self.findChild(QPushButton, "barcode_button")
        self.logs_button = self.findChild(QPushButton, "logs_button")
        self.logout_button = self.findChild(QPushButton, "logout_button")
        self.borrower_button = self.findChild(QPushButton, "borrow_history")

        self.users_button.clicked.connect(self.manage_users)
        self.items_button.clicked.connect(self.manage_items)
        self.logout_button.clicked.connect(self.logout)
        self.barcode_button.clicked.connect(self.scan_barcode)
        self.borrower_button.clicked.connect(self.manage_borrowers)
        self.logs_button.clicked.connect(self.view_logs)

        self.usr_mng_window = User_Mngmnt()
        self.usr_mng_window.return_.connect(self.show)
        self.itm_mng_window = Item_Mngmnt()
        self.itm_mng_window.return_.connect(self.show)
        self.scan_window = Scanbarcode()
        self.scan_window.return_.connect(self.show)
        self.borrower_window = Borrower_Mngmnt()
        self.borrower_window.return_.connect(self.show)
        self.log_window = ViewLogs()
        self.log_window.return_.connect(self.show)

    def closeEvent(self, event):
        self.closed_to_login.emit()
        self.logout()
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT user FROM lnhsis.logs ORDER BY log_id DESC LIMIT 1")
        except mysql.connector.Error as err:
            print("Error:", err)

        self.current_user = cursor.fetchone()
        db.close()

    def manage_borrowers(self):
        self.borrower_window.show()
        self.hide()

    def view_logs(self):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT * FROM lnhsis.permissions WHERE perm_user = '{self.current_user[0]}' AND (perm_val LIKE '%logs%' OR perm_val LIKE '%admin%')")
        except mysql.connector.Error as err:
            print("Error:", err)
        
        result = cursor.fetchone()
        db.close()

        if not result:
            self.warning.setWarning("You have no permission to access this feature.")
            self.warning.exec()
            return
        self.log_window.show()
        self.hide()

    def manage_users(self):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT * FROM lnhsis.permissions WHERE perm_user = '{self.current_user[0]}' AND (perm_val LIKE '%users%' OR perm_val LIKE '%admin%')")
        except mysql.connector.Error as err:
            print("Error:", err)
        
        result = cursor.fetchone()
        db.close()

        if not result:
            self.warning.setWarning("You have no permission to access this feature.")
            self.warning.exec()
            return
        self.usr_mng_window.show()
        self.hide()

    def manage_items(self):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT * FROM lnhsis.permissions WHERE perm_user = '{self.current_user[0]}' AND (perm_val LIKE '%items%' OR perm_val LIKE '%admin%')")
        except mysql.connector.Error as err:
            print("Error:", err)
        
        result = cursor.fetchone()
        db.close()
        if not result:
            self.warning.setWarning("You have no permission to access this feature.")
            self.warning.exec()
            return
        self.itm_mng_window.show()
        self.hide()

    def scan_barcode(self):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT * FROM lnhsis.permissions WHERE perm_user = '{self.current_user[0]}' AND (perm_val LIKE '%barcode%' OR perm_val LIKE '%admin%')")
        except mysql.connector.Error as err:
            print("Error:", err)
        
        result = cursor.fetchone()
        db.close()
        if not result:
            self.warning.setWarning("You have no permission to access this feature.")
            self.warning.exec()
            return
        self.scan_window.show()
        self.hide()

    def logout(self):
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()
        action = "Logged Out"
        current_datetime = datetime.datetime.now()

        try:
            cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{current_datetime}')")
        except mysql.connector.Error as err:
            print("Error: ", err)
        connection.commit()
        db.close()
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    window = Main_menu()
    window.show()
    app.exec()