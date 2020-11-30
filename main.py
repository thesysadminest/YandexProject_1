import sqlite3
import sys
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLCDNumber, QLabel, QMainWindow, QDialog
from PyQt5 import uic


class MainProgram(QMainWindow):
    def __init__(self, login, con, cur):
        super().__init__()
        uic.loadUi('ui.ui', self)
        self.con = con
        self.cur = cur
        self.login = login

        print("dfdfadfg")


class LoginDialog(QDialog):
    def __init__(self, pwdState=True):
        super().__init__()
        uic.loadUi('dui.ui', self)
        if pwdState:
            self.wrongPasswordLabel.hide()
        self.buttonBox.accepted.connect(self.checkPwd)

    def checkPwd(self):
        self.con = sqlite3.connect("db.sqlite")
        self.cur = self.con.cursor()
        login = self.login.text()
        password = self.password.text()
        try:
            role = login[0]
        except IndexError:
            return self.tryAgain()

        if role.lower() == 'a':
            result = self.cur.execute(
                """SELECT password FROM admin WHERE login = ?""", (login, )).fetchall()
        elif role.lower() == 't':
            result = self.cur.execute(
                """SELECT password FROM teacher WHERE login = ?""", (login, )).fetchall()
        elif role.lower() == 's':
            result = self.cur.execute(
                """SELECT password FROM student WHERE login = ?""", (login, )).fetchall()
        else:
            self.tryAgain()

        print(result)

    def tryAgain(self):
        global login_dial
        login_dial = LoginDialog(False)
        login_dial.show()

    def startMainProgram(self):
        global main_prog
        main_prog = MainProgram(self.login.text(), self.con, self.cur)
        main_prog.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_prog = None
    login_dial = LoginDialog()
    login_dial.show()
    sys.exit(app.exec_())
