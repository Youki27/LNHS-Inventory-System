from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QCheckBox, QMainWindow, QWidget, QApplication
from PyQt6 import uic
from database import Database
import mysql.connector
from warning_dialog import Warning

class EditUsers(QMainWindow):
    
    def __init__(self):
        super(EditUsers, self).__init__()

        uic.loadUi("Ui/add_user_window.ui", self)

        self.warning = Warning()

        self.label = self.findChild(QLabel,"label")
        self.username = self.findChild(QLineEdit, "username")
        self.password = self.findChild(QLineEdit, "password")
        self.password_confirm = self.findChild(QLineEdit, "password_confirm")
        self.admin_checkbox = self.findChild(QCheckBox, "admin_checkbox")
        self.users_checkbox = self.findChild(QCheckBox, "users_checkbox")
        self.items_checkbox = self.findChild(QCheckBox, "items_checkbox")
        self.logs_checkbox = self.findChild(QCheckBox, "logs_checkbox")
        self.barcode_checkbox = self.findChild(QCheckBox, "barcode_checkbox")
        self.save_button = self.findChild(QPushButton, "save_button")

        self.permissions = [self.admin_checkbox, self.users_checkbox, self.items_checkbox, self.logs_checkbox, self.barcode_checkbox]

        self.label.setText("Edit User")

        self.save_button.clicked.connect(self.saveEdit)

    def editUser(self, creds):

        self.uname = creds[0]
        self.pword = creds[1]
        self.perms = creds[2].split(',')

        self.username.setText(self.uname)
        self.password.setText(self.pword)
        self.password_confirm.setText(self.pword)

        for perm in self.perms:
            if 'admin' in perm or 'Admin' in perm:
                self.admin_checkbox.setChecked(True)
            if 'Users' in perm:
                self.users_checkbox.setChecked(True)
            if 'Items' in perm:
                self.items_checkbox.setChecked(True)
            if 'Logs' in perm:
                self.logs_checkbox.setChecked(True)
            if 'Barcode' in perm:
                self.barcode_checkbox.setChecked(True)

    def saveEdit(self):

        if not self.verifyUsername():
            return
        if not self.verifyPassword():
            return
        if not self.verifyPerms():
            return
        
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        if self.username.text() != self.uname or self.password.text() != self.pword:
            try:
                cursor.execute(f"SELECT uid FROM lnhsis.users WHERE username = '{self.uname}'")
            except mysql.connector.Error as err:
                print("Error: ", err)

            uid = cursor.fetchall()

            try:
                cursor.execute(f"UPDATE lnhsis.users SET username = '{self.username.text()}', password = '{self.password.text()}' WHERE uid = {uid[0][0]}")
            except mysql.connector.Error as err:
                print("Error:", err)

            connection.commit()

        try:
            cursor.execute(f"SELECT perm_id FROM lnhsis.permissions WHERE perm_user = '{self.uname}'")
        except mysql.connector.Error as err:
            print("Error:", err)

        perm_res = cursor.fetchall()

        for item in perm_res:
            try:
                cursor.execute(f"DELETE FROM lnhsis.permissions WHERE perm_id = {item[0]}")
            except mysql.connector.Error as err:
               print("Error", err)
            connection.commit()

        for item in self.permissions:
            if item.isChecked():
                try:
                    cursor.execute(f"INSERT INTO lnhsis.permissions (perm_val, perm_user) VALUES ('{item.text()}','{self.username.text()}')")
                    connection.commit()
                except mysql.connector.Error as err:
                    print("Error:", err)

        db.close()
        self.close()
        self.warning.setWarning("Edit Saved!")
        self.warning.show()




        
    def verifyUsername(self):
        
        db = Database()
        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(f"SELECT * FROM lnhsis.users WHERE username = '{self.username.text()}'")
        except mysql.connector.Error as err:
            print("Error: ", err)

        results = cursor.fetchall()
        connection.close()

        if not self.username.text():
            self.warning.setWarning("Username Fields are empty!")
            self.warning.show()
            return
        if self.username.text() != self.uname and results:
            self.warning.setWarning("Username Already Taken!")
            self.warning.show()
            return
        if not self.username.text().isalnum():
            self.warning.setWarning("Username Must only contain Alphanumeric characters!")
            self.warning.show()
            return
        
        return True
    
    def verifyPassword(self):

        if not self.password.text():
            self.warning.setWarning("Password Field is Empty!")
            self.warning.show()
            return
        if not self.password_confirm.text():
            self.warning.setWarning("Password Confimation Field is Empty!")
            self.warning.show()
            return
        if not self.password.text().isalnum():
            self.warning.setWarning("Password  must be Alphanumeric!")
            self.warning.show()
            return
        if len(self.password.text())<6:
            self.warning.setWarning("Password must be 6 characters long!")
            self.warning.show()
            return
        if self.password.text() != self.password_confirm.text():
            self.warning.setWarning("Passwords do not Match!")
            self.warning.show()
            return
        
        return True
    
    def verifyPerms(self):

        permissions_checked = any(perms.isChecked() for perms in self.permissions)
        checked = [checkbox.text() for checkbox in self.permissions if checkbox.isChecked()]
        admin_checked = any('Admin' in check_data for check_data in checked)

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
    window = EditUsers()
    window.show()
    app.exec()