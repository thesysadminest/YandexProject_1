import sqlite3
import sys
import datetime
#from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QMainWindow, QDialog
from PyQt5.QtWidgets import *
from PyQt5 import uic


class MainProgram(QMainWindow):
    def __init__(self, login, con, cur):
        super().__init__()
        uic.loadUi('ui.ui', self)
        self.con = con
        self.cur = cur
        self.login = login
        dt = datetime.date.today()
        self.dateChoose.setDate(dt)
        self.pAddBar.hide()
        self.pDelBar.hide()
        self.okButton_bAdd.clicked.connect(self.batchAdd)
        self.okButton_bDel.clicked.connect(self.batchDel)

    def batchAdd(self):  # batch adding students, (teachers) and admins into DB
        from additional import key
        import random
        text = self.bAddField.toPlainText().rstrip('\n').split('\n')
        role = self.selectAAccType.currentText()

        self.pAddBar.setMaximum(len(text))
        self.pAddBar.setValue(0)
        value = 0
        self.pAddBar.show()
        for i in text:
            a = i.split()
            name = ' '.join(a[:3])
            if role == 'Ученик':
                login = 's'
            elif role == 'Учитель':
                login = 't'
            else:
                login = 'a'
            login += a[3][2:] + '_' + key[a[0][0].lower()] + \
                key[a[1][0].lower()] + key[a[2][0].lower()]

            try:
                if role == 'Ученик':
                    classes = a[4].lower()
                elif role == 'Учитель':
                    classes = ' '.join(
                        sorted(list(set([i.lower() for i in a[5:]]))))
            except IndexError:
                if role != 'Администратор':
                    pass  # todo: сообщение об ошибке
            pwd = str(random.randint(100000, 999999))

            if role == 'Ученик':
                n = 0
                while True:
                    try:
                        self.cur.execute(
                            'INSERT INTO student (name, class, login, password) VALUES (?, ?, ?, ?)', (name, classes, login, pwd))
                        flag = True
                    except sqlite3.IntegrityError:
                        flag = False
                        n += 1
                        login = login[:7] + str(n)
                    if flag:
                        break
            # elif role == 'Учитель':
            #     self.cur.execute(
            #         'INSERT INTO teacher (name, classes, lesson, login, password) VALUES (?, ?, ?, ?, ?)', (name, classes, lesson, login, pwd))
            else:
                n = 0
                while True:
                    try:
                        self.cur.execute(
                            'INSERT INTO admin (name, login, password) VALUES (?, ?, ?)', (name, login, pwd))
                        flag = True
                    except sqlite3.IntegrityError:
                        flag = False
                        n += 1
                        login = login[:7] + str(n)
                    if flag:
                        break

            value += 1
            self.pAddBar.setValue(value)
            self.pAddBar.update()

        self.con.commit()
        self.bAddField.setText('')
        self.pAddBar.hide()

    def batchDel(self):
        text = self.bDelField.toPlainText().rstrip('\n').split('\n')
        self.pDelBar.setMaximum(len(text))
        self.pDelBar.setValue(0)
        self.pDelBar.show()
        value = 0

        for i in text:
            if i[0] == "s":
                self.cur.execute("DELETE from student where login = ?", (i,))
            elif i[0] == 't':
                self.cur.execute("DELETE from teacher where login = ?", (i,))
            elif i[0] == "a":
                self.cur.execute("DELETE from admin where login = ?", (i,))
            else:
                pass  # todo: ошибка

            value += 1
            self.pDelBar.setValue(value)

        self.con.commit()
        self.bDelField.setText('')
        self.pDelBar.hide()


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
        result = []
        if role.lower() == 'a':
            result = self.cur.execute(
                """SELECT password FROM admin WHERE login = ?""", (login, )).fetchone()
        elif role.lower() == 't':
            result = self.cur.execute(
                """SELECT password FROM teacher WHERE login = ?""", (login, )).fetchone()
        elif role.lower() == 's':
            result = self.cur.execute(
                """SELECT password FROM student WHERE login = ?""", (login,)).fetchone()

        if result and result[0] == password:
            self.startMainProgram()
        else:
            self.tryAgain()

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
