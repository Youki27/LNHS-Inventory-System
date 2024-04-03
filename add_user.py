from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QCheckBox, QMainWindow, QWidget, QApplication
from PyQt6 import uic
from database import Database
import mysql.connector, datetime
from warning_dialog import Warning

class AddUser(QMainWindow):

    def __init__(self):

        
        self.warning = Warning()

        super(AddUser, self).__init__()

        uic.loadUi("Ui/add_user_window.ui", self)

        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT user FROM lnhsis.logs ORDER BY log_date LIMIT 1")
        except mysql.connector.Error as err:
            print("Error:", err)

        self.current_user = cursor.fetchone()
        db.close()

        self.username = self.findChild(QLineEdit,"username")
        self.password = self.findChild(QLineEdit, "password")
        self.password_confirm = self.findChild(QLineEdit, "password_confirm")
        admin_checkbox = self.findChild(QCheckBox, "admin_checkbox")
        users_checkbox = self.findChild(QCheckBox, "users_checkbox")
        items_checkbox = self.findChild(QCheckBox, "items_checkbox")
        barcode_checkbox = self.findChild(QCheckBox, "barcode_checkbox")
        logs_checkbox = self.findChild(QCheckBox, "logs_checkbox")
        save_button = self.findChild(QPushButton, "save_button")

        self.permissions = [admin_checkbox, users_checkbox, items_checkbox, barcode_checkbox, logs_checkbox, save_button]

        save_button.clicked.connect(self.saveData)

    def saveData(self):
        if not self.verifyUsername():
            return
        if not self.verifyPassword():
            return
        if not self.verifyPermissions():
            return
        
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"INSERT INTO lnhsis.users (username,password) VALUES ('{self.username.text()}','{self.password.text()}');")
            connection.commit()
        except mysql.connector.Error as err:
            print("Error in Insert 1:", err)
       

        for items in self.permissions:
            if items.isChecked():
                try:
                    cursor.execute(f"INSERT INTO lnhsis.permissions (perm_val, perm_user) VALUES ('{items.text()}','{self.username.text()}');")
                    connection.commit()
                except mysql.connector.Error as err:
                    print("Error ins Insert 2:", err)

        try:
            action = f"Added the user {self.username.text()}"
            current_datetime = datetime.datetime.now()
            cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{current_datetime}')")
        except mysql.connector.Error as err:
            print("Error:", err)
        connection.commit()

        db.close()
        self.warning.setWarning(f"User {self.username.text()}, saved!")
        self.warning.show()
                    

    def verifyUsername(self):
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM lnhsis.users WHERE username = '{self.username.text()}'")
        except mysql.connector.Error as err:
            print("Error: ",err)

        result = cursor.fetchall()
        
        connection.close()

        if not self.username.text():
            self.warning.setWarning("Username field is Empty!")
            self.warning.show()
            return
        if not self.username.text().isalnum():
            self.warning.setWarning("Username must contain Alphanumeric characters only!")
            self.warning.show()
            return
        if result:
            self.warning.setWarning("Username is already taken!")
            self.warning.show()
            return

        return True
    
    def verifyPassword(self):

        if not self.password.text():
            self.warning.setWarning("Password field is Empty!")
            self.warning.show()
            return
        if not self.password.text().isalnum():
            self.warning.setWarning("Password must contain Alphanumeric Characters Only!")
            self.warning.show()
        if len(self.password.text()) < 6:
            self.warning.setWarning("Password must be atleast 6 characters long!")
            self.warning.show()
            return
        if not self.password_confirm.text():
            self.warning.setWarning("Confirm Password field is Empty!")
            self.warning.show()
            return
        if self.password.text() != self.password_confirm.text():
            self.warning.setWarning("Passwords Does not Match!")
            self.warning.show()
            return
        
        return True
    
    def verifyPermissions(self):
        
        permissions_checked = any(permissions.isChecked() for permissions in self.permissions)
        checked = [checkbox.text() for checkbox in self.permissions if checkbox.isChecked()]
        admin_checked = any('Admin' in check_data for check_data in checked )

        if not permissions_checked:
            self.warning.setWarning("Check atleast one of the Permission!")
            self.warning.show()
            return
        if admin_checked and len(checked) > 1:
            self.warning.setWarning("Admin permission is already granted, uncheck the others.")
            self.warning.show()
            return
        return True

if __name__ == "__main__":
    app = QApplication([])
    window = AddUser()
    window.show()
    app.exec()