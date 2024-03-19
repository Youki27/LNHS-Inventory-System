
from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_incUNPW_warning(object):
    def setupUi(self, incUNPW_warning):
        incUNPW_warning.setObjectName("incUNPW_warning")
        incUNPW_warning.resize(443, 128)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=incUNPW_warning)
        self.buttonBox.setGeometry(QtCore.QRect(0, 80, 411, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(parent=incUNPW_warning)
        self.label.setGeometry(QtCore.QRect(20, 20, 431, 51))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setStyleSheet("color:#F47174;")
        self.label.setObjectName("label")

        self.retranslateUi(incUNPW_warning)
        self.buttonBox.accepted.connect(incUNPW_warning.accept) # type: ignore
        self.buttonBox.rejected.connect(incUNPW_warning.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(incUNPW_warning)

    def retranslateUi(self, incUNPW_warning):
        _translate = QtCore.QCoreApplication.translate
        incUNPW_warning.setWindowTitle(_translate("incUNPW_warning", "Dialog"))
        self.label.setText(_translate("incUNPW_warning", "Incorrect Username or Password."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    incUNPW_warning = QtWidgets.QDialog()
    ui = Ui_incUNPW_warning()
    ui.setupUi(incUNPW_warning)
    incUNPW_warning.show()
    sys.exit(app.exec())
