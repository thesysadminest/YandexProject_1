import sqlite3
import sys
import datetime
# from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QMainWindow, QDialog
from PyQt5.QtWidgets import *
from PyQt5 import uic


class MainProgram(QMainWindow):
    def __init__(self, login, con, cur):
        super().__init__()
        uic.loadUi('ui.ui', self)
        self.con = con
        self.cur = cur
        self.login = login

        self.accsLoaded = False
        self.teachersLoaded, self.studentsLoaded, self.adminsLoaded = [], [], []
        self.dateChoose.setDate(datetime.date.today())
        self.sacTable.itemChanged.connect(self.enable_changeAccsInfo_buttons)
        self.tacTable.itemChanged.connect(self.enable_changeAccsInfo_buttons)
        self.aacTable.itemChanged.connect(self.enable_changeAccsInfo_buttons)

        self.okAccsBtn.clicked.connect(self.changeAccsInfo)  # accs info work
        self.deAccsBtn.clicked.connect(self.loadAccs)
        self.okButton_bAdd.clicked.connect(self.batchAdd)  # batchAdd
        self.pAddBar.hide()
        self.bAddField.textChanged.connect(self.enable_batchAdd_buttons)
        self.okButton_bDel.clicked.connect(self.batchDel)  # batchDel
        self.pDelBar.hide()
        def temp_func(): return self.okButton_bDel.setEnabled(True)
        self.bDelField.textChanged.connect(temp_func)

        self.loadAccs()  # todo: потом убрать эту строчку
        # a = QTextEdit(self)
        # a.

    def loadAccs(self):  # loading accounts into tables (for admin)
        if not self.accsLoaded:
            self.studentsLoaded = self.cur.execute(
                "SELECT * FROM student ORDER BY class, class_letter, name").fetchall()
            self.teachersLoaded = self.cur.execute(
                "SELECT * FROM teacher ORDER BY name").fetchall()
            self.adminsLoaded = self.cur.execute(
                "SELECT * FROM admin ORDER BY name").fetchall()

        self.sacTable.setRowCount(len(self.studentsLoaded))
        self.tacTable.setRowCount(len(self.teachersLoaded))
        self.aacTable.setRowCount(len(self.adminsLoaded))

        for i in range(len(self.studentsLoaded)):
            for j in range(6):
                self.sacTable.setItem(
                    i, j, QTableWidgetItem(str(self.studentsLoaded[i][j])))
        self.sacTable.resizeColumnsToContents()

        for i in range(len(self.teachersLoaded)):
            for j in range(5):
                self.tacTable.setItem(
                    i, j, QTableWidgetItem(str(self.teachersLoaded[i][j])))
        self.tacTable.resizeColumnsToContents()

        for i in range(len(self.adminsLoaded)):
            for j in range(4):
                self.aacTable.setItem(
                    i, j, QTableWidgetItem(str(self.adminsLoaded[i][j])))
        self.aacTable.resizeColumnsToContents()

        self.okAccsBtn.setDisabled(True)
        self.deAccsBtn.setDisabled(True)
        self.accsLoaded = True

    # enables buttons for change accs information
    def enable_changeAccsInfo_buttons(self):

        self.okAccsBtn.setEnabled(True)
        self.deAccsBtn.setEnabled(True)

    def changeAccsInfo(self):  # changing accounts information
        for i in range(self.sacTable.rowCount()):
            temp = tuple()
            for j in range(6):
                if j == 0 or j == 2:
                    temp += (int(self.sacTable.item(i, j).text()),)
                else:
                    temp += (self.sacTable.item(i, j).text(),)

            if (temp != self.studentsLoaded[i]):
                print(temp)
                call = f'''UPDATE student\n SET name = "{temp[1]}", class = {temp[2]}, class_letter = "{temp[3]}", login = "{temp[4]}", password = "{temp[5]}"\n WHERE id = {temp[0]}'''
                self.cur.execute(call)
                self.studentsLoaded[i] = temp

        for i in range(self.tacTable.rowCount()):
            temp = tuple()
            for j in range(5):
                if j == 0:
                    temp += (int(self.tacTable.item(i, j).text()),)
                else:
                    temp += (self.tacTable.item(i, j).text(),)

            if (temp != self.teachersLoaded[i]):
                print(temp)
                call = f'''UPDATE teacher\n SET name = "{temp[1]}", classes = "{temp[2]}", login = "{temp[3]}", password = "{temp[4]}"\n WHERE id = {temp[0]}'''
                self.cur.execute(call)
                self.teachersLoaded[i] = temp

        for i in range(self.aacTable.rowCount()):
            temp = tuple()
            for j in range(4):
                if j == 0:
                    temp += (int(self.aacTable.item(i, j).text()),)
                else:
                    temp += (self.aacTable.item(i, j).text(),)

            if (temp != self.adminsLoaded[i]):
                print(temp)
                call = f'''UPDATE admin\n SET name = "{temp[1]}", login = "{temp[2]}", password = "{temp[3]}"\n WHERE id = {temp[0]}'''
                self.cur.execute(call)
                self.adminsLoaded[i] = temp

        self.con.commit()
        self.okAccsBtn.setDisabled(True)
        self.deAccsBtn.setDisabled(True)

    # enables buttons for batch accounts add
    def enable_batchAdd_buttons(self):
        self.selectAAccType.setEnabled(True)
        self.okButton_bAdd.setEnabled(True)

    def batchAdd(self):  # batch adding students, teachers and admins into DB
        from additional import key
        import random
        text = self.bAddField.toPlainText().rstrip('\n').split('\n')
        role = self.selectAAccType.currentText()

        if role == '---':
            return 0  # todo: ошибка

        self.pAddBar.setMaximum(len(text))
        self.pAddBar.setValue(0)
        progressBar_value = 0
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
                    classes = int(a[4][:-1])
                    class_letter = a[4][-1]
                elif role == 'Учитель':
                    classes = set()
                    for temp in a[4:]:
                        classes.add(temp)

                    classes = [[int(i[:-1]), i[-1]] for i in classes]
                    classes.sort()
                    classes = [str(i[0]) + i[1] for i in classes]
                    classes = '; '.join(classes)

                    if classes == '':
                        break  # todo: ошибка

            except IndexError:
                if role != 'Администратор':
                    break
                    pass  # todo: сообщение об ошибке
            pwd = str(random.randint(100000, 999999))

            if role == 'Ученик':
                n = 0
                while True:
                    try:
                        self.cur.execute(
                            'INSERT INTO student (name, class, class_letter, login, password) VALUES (?, ?, ?, ?, ?)', (name, classes, class_letter, login, pwd))
                        flag = True
                    except sqlite3.IntegrityError:
                        flag = False
                        n += 1
                        login = login[:7] + str(n)
                    if flag:
                        break

            elif role == 'Учитель':
                n = 0
                while True:
                    try:
                        self.cur.execute(
                            'INSERT INTO teacher (name, classes, login, password) VALUES (?, ?, ?, ?)', (name, classes, login, pwd))
                        flag = True
                    except sqlite3.IntegrityError:
                        flag = False
                        n += 1
                        login = login[:7] + str(n)
                    if flag:
                        break

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

            progressBar_value += 1
            self.pAddBar.setValue(progressBar_value)
            self.pAddBar.update()

        self.con.commit()
        self.bAddField.setText('')
        self.pAddBar.hide()
        self.selectAAccType.setDisabled(True)
        self.okButton_bAdd.setDisabled(True)

    def batchDel(self):  # batch deleting students, teachers and admins from DB
        text = self.bDelField.toPlainText().rstrip('\n').split('\n')
        self.pDelBar.setMaximum(len(text))
        self.pDelBar.setValue(0)
        self.pDelBar.show()
        progressBar_value = 0

        for i in text:
            if i[0] == "s":
                self.cur.execute("DELETE from student where login = ?", (i,))
            elif i[0] == 't':
                self.cur.execute("DELETE from teacher where login = ?", (i,))
            elif i[0] == "a":
                self.cur.execute("DELETE from admin where login = ?", (i,))
            else:
                pass  # todo: ошибка

            progressBar_value += 1
            self.pDelBar.setValue(progressBar_value)

        self.con.commit()
        self.bDelField.setText('')
        self.pDelBar.hide()
        self.okButton_bDel.setDisabled(True)


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
        main_prog.loadAccs()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_prog = None
    login_dial = LoginDialog()
    login_dial.show()
    sys.exit(app.exec_())
