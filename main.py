import sqlite3
import sys
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLCDNumber, QLabel, QMainWindow, QDialog
from PyQt5 import uic


class MainProgram(QMainWindow):
    def __init__(self, login, password):
        super().__init__()
        uic.loadUi('ui.ui', self)

    def checkPassword(self, login, password):
        pass


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('dui.ui', self)
        self.buttonBox.accepted.connect(self.runMainProgram)

    def runMainProgram(self):
        login = self.login.text()
        password = self.password.text()
        main_prog = MainProgram(login, password)
        main_prog.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_dial = LoginDialog()
    login_dial.show()
    sys.exit(app.exec_())

    # cur.execute(
    #     """insert into teacher(name, login, password) values('ddfjdfgj', 'fjfgjfg', 'fjfjfjf')""")
    # con.commit()

    # def login():
    #     pass

    # login = input()

    # a = cur.execute(
    #     """select * from teacher  where login = ?""", (login, )).fetchall()
    # print(a)

    # con.close()
