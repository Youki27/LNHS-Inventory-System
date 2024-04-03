from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QPushButton, QMainWindow, QApplication, QLineEdit,QTableView, QHeaderView, QDialog
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, QItemSelection, QModelIndex
from add_user import AddUser
from database import Database
import mysql.connector, datetime


class User_Mngmnt(QMainWindow):

    return_ =pyqtSignal()
    
    
    def __init__(self):
        super(User_Mngmnt,self).__init__()

        uic.loadUi("Ui/users_window.ui", self)

        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT user FROM lnhsis.logs ORDER BY log_date DESC LIMIT 1")
        except mysql.connector.Error as err:
            print("Error:", err)

        self.current_user = cursor.fetchone()
        db.close()

        self.return_button = self.findChild(QPushButton, "return_button")
        self.add_user_button = self.findChild(QPushButton, "add_user_button")
        self.search_bar = self.findChild(QLineEdit, "search_bar")
        self.main_table = self.findChild(QTableView, "main_table")
        self.refresh_button = self.findChild(QPushButton, "refresh_button")
        self.search_button = self.findChild(QPushButton, "search_button")

        self.return_button.clicked.connect(self.Return_)
        self.add_user_button.clicked.connect(self.addUser)
        self.refresh_button.clicked.connect(self.loadUsers)
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.search_button.clicked.connect(self.loadSearchedItem)

        self.loadUsers()

    def Return_(self):
        self.close()
        self.return_.emit()

    def closeEvent(self, event):
        self.return_.emit()
        super().closeEvent(event)

    def addUser(self):
        self.AddUser_window = AddUser()
        self.AddUser_window.show()
        
    def loadUsers(self):

        db =  Database()

        connection = db.connect()
        cursor = connection.cursor()
        
        try:
            cursor.execute(f"SELECT username, password FROM lnhsis.users")
        except mysql.connector.Error as err:
            print("Error:", err)

        results = cursor.fetchall()

        try:
            cursor.execute(f"SELECT perm_val, perm_user FROM lnhsis.permissions")
        except mysql.connector.Error as err:
            print("Error: ", err)

        permm_res = cursor.fetchall()
        connection.close()
        
        self.model = QStandardItemModel(0,3)
        self.model.setHorizontalHeaderLabels(['Username','Password','Permissions','',''])

        items = []
        for row in results:
            items = [
                QStandardItem(row[0]),
                QStandardItem(row[1])
            ]
            perm_items = []
            for perm_row in permm_res:
                if row[0] == perm_row[1]:
                    perm_items.append(perm_row[0])
            items.append(QStandardItem(', '.join(str(item) for item in perm_items)))
            items.append(QStandardItem("Edit"))
            items.append(QStandardItem("Delete"))
            self.model.appendRow(items)

        self.view = self.main_table
        self.view.setModel(self.model)
        self.view.setColumnWidth(2, 650)
        self.main_table.selectionModel().selectionChanged.connect(self.tableItemClicked)

    def tableItemClicked(self, item:QModelIndex):

        selected_item = ""

        for index in item.indexes():
            selected_item = index

        if isinstance(selected_item, str):
            return

        selected_item_data = selected_item.data()

        username_index = self.model.index(selected_item.row(),0)
        password_index = self.model.index(selected_item.row(),1)
        permission_index = self.model.index(selected_item.row(),2)

        selected_username = self.model.data(username_index)
        selected_password = self.model.data(password_index)
        selected_permission = self.model.data(permission_index)

        if selected_item_data == "Edit":

            creds = [selected_username, selected_password, selected_permission]

            from edit_users import EditUsers

            self.edit_user_window = EditUsers()
            self.edit_user_window.editUser(creds)
            self.edit_user_window.show()
            
        if selected_item_data == "Delete":
            
            from warning_dialog import Warning

            self.warning = Warning()

            self.warning.setWarning(f"Delete {selected_username} and their data?")

            res = self.warning.exec()

            if res == QDialog.DialogCode.Accepted:
                db = Database()

                connection = db.connect()
                cursor = connection.cursor()

                try:
                    cursor.execute(f"SELECT uid FROM lnhsis.users WHERE username = '{selected_username}'")
                except mysql.connector.Error as err:
                    print("Error 1: ", err)

                result = cursor.fetchall()


                for item in result:
                    try:
                        cursor.execute(f"DELETE FROM lnhsis.users WHERE uid = {item[0]}")
                    except mysql.connector.Error as err:
                        print("Error 2: ", err)
                        connection.rollback()
                    connection.commit()

                try:
                    cursor.execute(f"SELECT perm_id FROM lnhsis.permissions WHERE perm_user = '{selected_item}'")
                except mysql.connector.Error as err:
                    print("Error 3: ", err)

                perm_res = cursor.fetchall()

                for item in perm_res:
                    try:
                        cursor.execute(f"DELETE FROM lnhsis.permissions WHERE perm_id = '{item[0]}'")
                        connection.commit()
                    except mysql.connector.Error as err:
                        print("Error 4: ", err)

                try:
                    action = f"Deleted the item {selected_username}"
                    current_datetime = datetime.datetime.now()
                    cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{self.current_user[0]}', '{action}', '{current_datetime}')")
                except mysql.connector.Error as err:
                    print("Error:", err)
                connection.commit()

                db.close()
                self.warning.setWarning(f"{selected_username} was Deleted Successfully")
                self.warning.show()
                self.loadUsers()

            else:
                self.warning.setWarning("Deletion Cancelled!")
                self.warning.show()

    def showEvent(self, event):
        super().showEvent(event)
        self.loadUsers()

    def loadSearchedItem(self):
        db = Database()

        connection = db.connect()
        cursor = connection.cursor()

        tbsearched = self.search_bar.text()

        try:
            cursor.execute(f"SELECT * FROM lnhsis.users WHERE username LIKE '%{tbsearched}%' OR password LIKE '%{tbsearched}%'")
        except mysql.connector.Error as err:
            print("Error:", err)
            connection.rollback()

        results = cursor.fetchall()

        found = []

        for items in results:
            item = [items[0], items[1], items[2]]
            found.append(item)
        counter = 0
        for items in found:
            try:
                cursor.execute(f"SELECT perm_val FROM lnhsis.permissions WHERE perm_user = '{items[1]}'")
            except mysql.connector.Error as err:
                print("Error: ", err)
                connection.rollback()
            perm_res = cursor.fetchall()

            found_perms = ', '.join(str(item[0]) for item in perm_res)
            found[counter].append(found_perms)
            counter += 1
            
        db.close()

        self.model.removeRows(0, self.model.rowCount())


        for items in found:
            Searched_item = [
                QStandardItem(items[1]),
                QStandardItem(items[2]),
                QStandardItem(items[3]),
                QStandardItem("Edit"),
                QStandardItem("Delete"),
            ]
            self.model.appendRow(Searched_item)

        self.view.setModel(self.model)
        self.main_table.selectionModel().selectionChanged.connect(self.tableItemClicked)



if __name__ == "__main__":
    app = QApplication([])
    window = User_Mngmnt()
    window.show()
    app.exec()