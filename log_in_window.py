from PyQt6 import QtCore, QtGui, QtWidgets
from management_window import Ui_management_window
from UNPW_pop import Ui_incUNPW_warning
from database import Database

db = Database(host='127.0.0.1',user='root',password='youkifubuki27*',database='LNHSIS')

db.connect()
#db.delete_database()
db.close()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(438, 600)
        MainWindow.setStyleSheet("background-color: white")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.log_in_box = QtWidgets.QFrame(parent=self.centralwidget)
        self.log_in_box.setGeometry(QtCore.QRect(50, 250, 351, 281))
        self.log_in_box.setAutoFillBackground(False)
        self.log_in_box.setStyleSheet("background-color: #6EC6FF;\n"
"border-radius: 5px;\n"
"border-color: #4A90E2;\n"
"")
        self.log_in_box.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.log_in_box.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.log_in_box.setObjectName("log_in_box")
        self.label = QtWidgets.QLabel(parent=self.log_in_box)
        self.label.setGeometry(QtCore.QRect(140, 30, 61, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.username_input = QtWidgets.QLineEdit(parent=self.log_in_box)
        self.username_input.setGeometry(QtCore.QRect(30, 100, 291, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.username_input.setFont(font)
        self.username_input.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeVerCursor))
        self.username_input.setStyleSheet("background-color: white; \n"
"border-radius: 5px;\n"
"color:#333333")
        self.username_input.setObjectName("username_input")
        self.pass_input = QtWidgets.QLineEdit(parent=self.log_in_box)
        self.pass_input.setGeometry(QtCore.QRect(30, 150, 291, 41))
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.pass_input.setFont(font)
        self.pass_input.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeVerCursor))
        self.pass_input.setStyleSheet("background-color: white; \n"
"border-radius: 5px;\n"
"color:#333333")
        self.pass_input.setObjectName("pass_input")
        self.log_in_button = QtWidgets.QPushButton(parent=self.log_in_box, clicked=lambda: Ui_MainWindow.logged_in(self))
        self.log_in_button.setGeometry(QtCore.QRect(30, 210, 291, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.log_in_button.setFont(font)
        self.log_in_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.log_in_button.setStyleSheet("background-color: #8BC34A;\n"
"color:white;\n"
"border-radius: 5px;\n"
"border: #4A90E2;")
        self.log_in_button.setObjectName("log_in_button")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(130, 60, 181, 171))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("../pyqt6/imgs/10367120_1535392513362694_7783233140674644301_n.jpg"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 438, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Log In"))
        self.log_in_button.setText(_translate("MainWindow", "Log In"))

    def logged_in(self):

        givem_cred = [self.username_input.text(), self.pass_input.text()]

        if not db.verify_login(givem_cred):
            self.username_input.setText("")
            self.pass_input.setText("")
            self.window = QtWidgets.QDialog()
            self.ui = Ui_incUNPW_warning()
            self.ui.setupUi(self.window)
            self.window.show()
            return
        
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_management_window()
        self.ui.setupUi(self.window)
        self.window.show()
        MainWindow.hide()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.setWindowTitle("LNHS Inventory System")
    MainWindow.show()
    sys.exit(app.exec())
