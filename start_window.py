import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
    from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QFrame, QPushButton, QDialog
    from PyQt6 import uic
    import mysql.connector, datetime, ctypes, sys
    from menu_window import Main_menu
    from user_management_window import User_Mngmnt
    from UNPW_pop import Ui_incUNPW_warning
    from database import Database

    class Login_Window(QMainWindow):
        def __init__(self):
            super(Login_Window,self).__init__()

            uic.loadUi("Ui/Log_in-window.ui", self)

            self.username_input = self.findChild(QLineEdit, "username_input")
            self.pass_input = self.findChild(QLineEdit, "pass_input")
            self.login_button = self.findChild(QPushButton, "log_in_button")

            self.login_button.clicked.connect(self.login)

            self.main_menu_window = Main_menu()
            self.usr_mngmt_win = User_Mngmnt()
            self.main_menu_window.closed_to_login.connect(self.show)
            
        def login(self):
            db = Database()

            connection = db.connect()
            cursor = connection.cursor()
            
            given_cred = [self.username_input.text(), self.pass_input.text()]

            if db.verify_login(given_cred):

                action = "Logged in"
                current_datetime = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                
                try:
                    cursor.execute(f"INSERT INTO lnhsis.logs (user, action, log_date) VALUES ('{given_cred[0]}', '{action}', '{current_datetime}' )")
                except mysql.connector.Error as err:
                    print("Error: ", err)
                connection.commit()
                
                db.close()

                self.username_input.setText("")
                self.pass_input.setText("")
                self.main_menu_window.show()
                self.hide()
            else:
                db.close()
            
                self.username_input.setText("")
                self.pass_input.setText("")
                self.window = QDialog()
                self.ui = Ui_incUNPW_warning()
                self.ui.setupUi(self.window)
                self.window.show()
            
            
    if __name__ == "__main__":
        app = QApplication([])
        Ui_Login_window = Login_Window()
        Ui_Login_window.show()
        app.exec()

else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)