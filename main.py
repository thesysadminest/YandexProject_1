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
        self.timetable, self.teachersIds, self.lessonsIds = {}, {}, {}
        self.teachersLoaded, self.studentsLoaded, self.adminsLoaded = [], [], []

        self.loadLessonsTeachersIds()
        self.setLoginInfo()

        if datetime.date.today().weekday() == 6:
            self.dateChoose.setDate(
                datetime.date.today() + datetime.timedelta(1))
        else:
            self.dateChoose.setDate(datetime.date.today())
        self.dateChoose.dateChanged.connect(self.currentDateTimetable_changed)
        self.dayChoose.setCurrentIndex(datetime.date.today().weekday())
        self.dayChoose.currentChanged.connect(self.currentDayTimetable_changed)
        self.classChoose.currentTextChanged.connect(self.loadTimetable)

        self.changePasswordButton.clicked.connect(
            self.changePassword)  # password change
        self.oldPassword.textChanged.connect(
            self.control_changePassword_button)
        self.newPassword1.textChanged.connect(
            self.control_changePassword_button)
        self.newPassword2.textChanged.connect(
            self.control_changePassword_button)

        self.handle()
        self.loadTimetable()

        # a = QComboBox(self)
        # a.

    def handle(self):
        if self.login[0] == 's':
            self.classChoose.setDisabled(True)
            temp = self.cur.execute(
                "SELECT class, class_letter FROM student WHERE login = ?", (self.login,)).fetchone()
            self.classChoose.addItem(''.join(str(i) for i in temp))

        elif self.login[0] == 't':
            classes = self.cur.execute(
                "SELECT classes FROM teacher WHERE login = ?", (self.login, )).fetchone()
            classes = classes[0].split('; ')
            self.classChoose.addItems(classes)
            self.okTableButton.clicked.connect(self.teacher_commitTableChanges)
            self.teacher_loadsubjects()
            self.teacher_loadMarks()
            self.teacherSubject.currentTextChanged.connect(
                self.teacher_loadMarks)

            def temp():
                self.loadTimetable()
                self.teacher_loadsubjects()
                self.teacher_loadMarks()
            self.classChoose.currentTextChanged.connect(temp)

        else:
            classes1 = self.cur.execute(
                "SELECT DISTINCT class, class_letter FROM student").fetchall()
            classes2 = self.cur.execute(
                "SELECT DISTINCT class FROM timetable").fetchall()
            classes2 = [(int(i[0][:-1]), i[0][-1]) for i in classes2]
            classes = sorted(classes1 + classes2)
            classes = [str(i[0]) + str(i[1]) for i in classes]
            self.classChoose.addItems(classes)

            self.addLesson.clicked.connect(self.addTimetableLesson)
            self.okTableButton.clicked.connect(self.admin_commitTableChanges)
            self.sacTable.itemChanged.connect(
                self.enable_changeAccsInfo_buttons)  # table with accounts
            self.tacTable.itemChanged.connect(
                self.enable_changeAccsInfo_buttons)
            self.aacTable.itemChanged.connect(
                self.enable_changeAccsInfo_buttons)

            self.okAccsBtn.clicked.connect(
                self.changeAccsInfo)  # accs info change
            self.deAccsBtn.clicked.connect(self.loadAccs)

            self.okButton_bAdd.clicked.connect(self.batchAdd)  # batchAdd
            self.pAddBar.hide()
            self.bAddField.textChanged.connect(self.control_batchAdd_buttons)

            self.okButton_bDel.clicked.connect(self.batchDel)  # batchDel
            self.pDelBar.hide()
            self.bDelField.textChanged.connect(self.control_batchDel_buttons)

            self.loadAccs()

    def setLoginInfo(self):  # sets login information
        def make_call(table):
            call = f"SELECT name FROM {table} WHERE login = '{self.login}'"
            name = self.cur.execute(call).fetchall()[0][0]
            return name
        role = self.login[0]
        fullRole = ''
        if role == 's':
            name = make_call('student')
            fullRole = 'Ученик'
        elif role == 't':
            name = make_call('teacher')
            fullRole = 'Учитель'
        else:
            name = make_call('admin')
            fullRole = 'Администратор'

        self.loginInformation.setText(f"{fullRole}: {name} ({self.login})")

    def loadLessonsTeachersIds(self):  # loading lessons and teachers ids
        temp_teachers = self.cur.execute("SELECT * FROM teacher").fetchall()
        temp_lessons = self.cur.execute("SELECT * FROM lesson").fetchall()
        for i in temp_lessons:
            self.lessonsIds[i[0]] = i[1]
        for i in temp_teachers:
            self.teachersIds[i[0]] = i[1]

    def teacher_loadsubjects(self):
        currentName = self.cur.execute(
            "SELECT name FROM teacher WHERE login = ?", (self.login,)).fetchone()[0]
        currentClass = self.classChoose.currentText()
        for i in self.teachersIds:
            if self.teachersIds[i] == currentName:
                currentName = i
                break

        subjects = self.cur.execute("""SELECT DISTINCT lesson FROM timetable \
            WHERE class = ? AND teacher = ? ORDER BY lesson""",
                                    (currentClass, currentName)).fetchall()

        try:
            subjects = [self.lessonsIds[i[0]] for i in subjects]
        except Exception:
            return

        self.teacherSubject.clear()
        self.teacherSubject.addItems(subjects)

    def teacher_loadMarks(self):
        date = self.dateChoose.text().split('.')
        dateEnd = datetime.date(int(date[2]), int(date[1]), int(date[0]))
        dateBegin = dateEnd - datetime.timedelta(30)
        currentName = self.cur.execute(
            "SELECT name FROM teacher WHERE login = ?", (self.login,)).fetchone()[0]
        currentClass = self.classChoose.currentText()
        for i in self.teachersIds.keys():
            if self.teachersIds[i] == currentName:
                currentName = i
                break
        currentLesson = self.teacherSubject.currentText()
        for i in self.lessonsIds.keys():
            if self.lessonsIds[i] == currentLesson:
                currentLesson = i
                break

        temp_timetable = self.cur.execute(
            """SELECT id, day FROM timetable WHERE teacher = ? AND class = ? AND lesson = ?\
                 AND day BETWEEN ? AND ? ORDER BY day""",
            (currentName, currentClass, currentLesson, dateBegin, dateEnd)).fetchall()

        self.marks = []
        for i in temp_timetable:
            result = self.cur.execute(
                "SELECT * FROM marks WHERE id_timetable = ?", (i[0],)).fetchall()
            self.marks.append([i[1], result])

        self.marksStudents = self.cur.execute(
            "SELECT id, name FROM student WHERE class = ? AND class_letter = ? ORDER BY name",
            (int(currentClass[:-1]), currentClass[-1])).fetchall()
        self.marksStudents = {(self.marksStudents[i][0], self.marksStudents[i][1]): i for i in range(
            len(self.marksStudents))}

        temp1 = [i[0] for i in self.marks]
        temp2 = [i[1] for i in self.marksStudents.keys()]
        self.marksTable.clear()
        self.marksTable.setRowCount(len(temp2))
        self.marksTable.setColumnCount(len(temp1))
        self.marksTable.setHorizontalHeaderLabels(temp1)
        self.marksTable.setVerticalHeaderLabels(temp2)
        self.marksTable.resizeColumnsToContents()
        self.marksTable.resizeRowsToContents()
        for i in range(len(self.marks)):
            for j in self.marks[i][1]:
                if len(j) > 1:
                    for r in self.marksStudents:
                        if r[0] == j[1]:
                            self.marksTable.setItem(
                                self.marksStudents[r], i, QTableWidgetItem(str(j[2])))
                            break

    # # def teacher_commitMarksChanges(self):
    #     self.students = {i[0]: self.students[i] for i in self.students.keys()}
    #     for i in self.marks:
    #         self.marks[i].append(self.students[self.marks[i][1]])

    #     for i in range(self.marksTable.columnCount()):
    #         for j in range(self.marksTable.rowCount()):
    #             pass

    def currentDayTimetable_changed(self):  # when day is changed
        date = self.dateChoose.text().split('.')
        dateFormatted = datetime.date(int(date[2]), int(date[1]), int(date[0]))
        dateFormatted -= datetime.timedelta(dateFormatted.weekday())
        dateFormatted += datetime.timedelta(self.dayChoose.currentIndex())
        self.dateChoose.setDate(dateFormatted)

    def currentDateTimetable_changed(self):  # when timetable weekday changed
        date = self.dateChoose.text().split('.')
        dateFormatted = datetime.date(int(date[2]), int(date[1]), int(date[0]))
        if dateFormatted.weekday() == 6:
            if self.dayChoose.currentIndex() <= 3:
                dateFormatted -= datetime.timedelta(1)
            else:
                dateFormatted += datetime.timedelta(1)

        self.dayChoose.disconnect()
        self.dayChoose.setCurrentIndex(dateFormatted.weekday())
        self.dayChoose.currentChanged.connect(self.currentDayTimetable_changed)
        self.dateChoose.setDate(dateFormatted)
        self.loadTimetable()

    def addTimetableLesson(self):  # adds lesson into timetable
        def addRow(table):
            table.setRowCount(table.rowCount() + 1)

        index = self.dayChoose.currentIndex()

        if index == 0:
            addRow(self.mon_table)
        elif index == 1:
            addRow(self.tue_table)
        elif index == 2:
            addRow(self.wed_table)
        elif index == 3:
            addRow(self.thi_table)
        elif index == 4:
            addRow(self.fri_table)
        elif index == 5:
            addRow(self.sat_table)

    def admin_commitTableChanges(self):  # admin: applies timetable changes
        date = self.dateChoose.text().split('.')
        currentClass = self.classChoose.currentText()
        dateFormatted = datetime.date(int(date[2]), int(date[1]), int(date[0]))
        dateFormatted -= datetime.timedelta(dateFormatted.weekday() + 1)

        table = [self.mon_table, self.tue_table, self.wed_table,
                 self.thu_table, self.fri_table, self.sat_table]
        for r in range(6):
            dateFormatted += datetime.timedelta(1)
            try:
                temp_day = self.timetable[(
                    currentClass, dateFormatted.isoformat())]
            except KeyError:
                continue

            for i in range(table[r].rowCount()):
                try:
                    lesson_name = table[r].item(
                        i, 0).text().rstrip(' ').lstrip(' ').lower()
                    teacher_name = table[r].item(
                        i, 2).text().rstrip(' ').lstrip(' ').lower()
                except AttributeError:
                    continue
                try:
                    homework_name = table[r].item(
                        i, 1).text().rstrip(' ').lstrip(' ')
                except AttributeError:
                    homework_name = ''

                if lesson_name == '' or teacher_name == '':
                    try:
                        self.cur.execute(
                            'DELETE FROM timetable WHERE id = ?', (temp_day[i][0], ))
                        self.con.commit()
                    except Exception:
                        pass
                    continue

                lesson_id = teacher_id = -1
                for j in self.lessonsIds.keys():
                    if self.lessonsIds[j].lower() == lesson_name:
                        lesson_id = j
                        break
                for j in self.teachersIds.keys():
                    if self.teachersIds[j].lower() == teacher_name:
                        teacher_id = j
                        break
                if teacher_id == -1 or lesson_id == -1:
                    continue  # todo: error message

                try:
                    if lesson_name == temp_day[i][2] and \
                        homework_name == temp_day[i][4] and \
                            teacher_name == temp_day[i][3]:
                        continue
                except IndexError:
                    call = f"""INSERT INTO timetable (day, class, number, lesson, teacher, homework)
                             VALUES ('{dateFormatted.isoformat()}', '{currentClass}', {len(temp_day) + 1},
                                 {lesson_id}, {teacher_id}, '{homework_name}')"""
                    temp_day.append(tuple())
                    self.cur.execute(call)
                    self.con.commit()
                    continue
                call = f"UPDATE timetable SET lesson = {lesson_id}, teacher = {teacher_id}, \
                    homework = '{homework_name}' WHERE id = {temp_day[i][0]}"
                self.cur.execute(call)
                self.con.commit()

            try:
                del self.timetable[(currentClass, dateFormatted.isoformat())]
            except Exception:
                pass

        self.loadTimetable()
        QMessageBox.information(
            self, "Успеx!", "Данные успешно внесены в таблицу!")

    def teacher_commitTableChanges(self):  # teacher: applies timetable changes
        date = self.dateChoose.text().split('.')
        currentClass = self.classChoose.currentText()
        dateFormatted = datetime.date(int(date[2]), int(date[1]), int(date[0]))
        dateFormatted -= datetime.timedelta(dateFormatted.weekday() + 1)

        table = [self.mon_table, self.tue_table, self.wed_table,
                 self.thu_table, self.fri_table, self.sat_table]
        current_name = self.cur.execute(
            "SELECT name FROM teacher WHERE login = ?", (self.login,)).fetchone()[0].lower()

        for r in range(6):
            dateFormatted += datetime.timedelta(1)
            try:
                temp_day = self.timetable[(
                    currentClass, dateFormatted.isoformat())]
            except KeyError:
                continue

            for i in range(table[r].rowCount()):
                homework_name = table[r].item(
                    i, 1).text().rstrip(' ').lstrip(' ')
                teacher_name = temp_day[i][3]

                if teacher_name.lower() != current_name:
                    continue

                if homework_name != temp_day[i][4]:
                    self.cur.execute(
                        "UPDATE timetable SET homework = ? WHERE id = ?", (homework_name, temp_day[i][0]))
                    self.con.commit()

            del self.timetable[(currentClass, dateFormatted.isoformat())]

        self.loadTimetable()
        QMessageBox.information(
            self, "Успеx!", "Данные успешно внесены в таблицу!")

    def loadTimetable(self):  # loads timetable
        isEmpty = False
        currentClass = self.classChoose.currentText()
        currentDate = self.dateChoose.text().split('.')
        currentDate = '-'.join([currentDate[2],
                                currentDate[1], currentDate[0]])
        try:
            if not self.timetable[(currentClass, currentDate)]:
                raise KeyError
        except KeyError:
            currentDay = self.cur.execute(
                "SELECT id, class, lesson, teacher, homework FROM timetable WHERE day = ? AND class = ? ORDER BY number", (currentDate, currentClass)).fetchall()
            if not currentDay:
                isEmpty = True
            currentDay = [(i[0], i[1], self.lessonsIds[i[2]],
                           self.teachersIds[i[3]], i[4]) for i in currentDay]
            self.timetable[(currentClass, currentDate)] = currentDay
        temp = self.dayChoose.currentIndex()

        def fillTable(table):
            if isEmpty:
                table.setRowCount(0)
                return  # todo: error

            table.setRowCount(
                len(self.timetable[(currentClass, currentDate)]))
            table.setColumnCount(3)
            for i in range(len(self.timetable[(currentClass, currentDate)])):
                table.setItem(i, 0, QTableWidgetItem(str(
                    self.timetable[(currentClass, currentDate)][i][2])))
                table.setItem(i, 1, QTableWidgetItem(str(
                    self.timetable[(currentClass, currentDate)][i][4])))
                table.setItem(i, 2, QTableWidgetItem(str(
                    self.timetable[(currentClass, currentDate)][i][3])))
            table.resizeColumnsToContents()

        if temp == 0:
            fillTable(self.mon_table)
        elif temp == 1:
            fillTable(self.tue_table)
        elif temp == 2:
            fillTable(self.wed_table)
        elif temp == 3:
            fillTable(self.thu_table)
        elif temp == 4:
            fillTable(self.fri_table)
        elif temp == 5:
            fillTable(self.sat_table)

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
                call = f'''UPDATE admin\n SET name = "{temp[1]}", login = "{temp[2]}", password = "{temp[3]}"\n WHERE id = {temp[0]}'''
                self.cur.execute(call)
                self.adminsLoaded[i] = temp

        self.con.commit()
        self.okAccsBtn.setDisabled(True)
        self.deAccsBtn.setDisabled(True)

    # controls buttons for batch accounts add
    def control_batchAdd_buttons(self):
        text = self.bAddField.toPlainText()
        if text == '':
            self.selectAAccType.setDisabled(True)
            self.okButton_bAdd.setDisabled(True)
        else:
            self.selectAAccType.setEnabled(True)
            self.okButton_bAdd.setEnabled(True)

    # controls buttons for batch accounts delete
    def control_batchDel_buttons(self):
        text = self.bDelField.toPlainText()
        if text == '':
            self.okButton_bDel.setDisabled(True)
        else:
            self.okButton_bDel.setEnabled(True)

    def batchAdd(self):  # batch adding students, teachers and admins into DB
        from additional import key
        import random
        text = self.bAddField.toPlainText().rstrip('\n').split('\n')
        role = self.selectAAccType.currentText()

        if role == '---':
            QMessageBox.critical(
                self, "Ошибка ", "Выберите тип аккаунта")
            return

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
                        QMessageBox.critical(
                            self, "Ошибка ", "Задайте классы, в которых преподаёт учитель \nили поставьте прочерк")
                        return

            except IndexError:
                if role != 'Администратор':
                    QMessageBox.critical(
                        self, "Ошибка ", "Проверьте введённые данные")
                    return

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
                QMessageBox.critical(
                    self, "Ошибка ", "Проверьте ведённые данные")

            progressBar_value += 1
            self.pDelBar.setValue(progressBar_value)

        self.con.commit()
        self.bDelField.setText('')
        self.pDelBar.hide()

    # controls buttons for changing password
    def control_changePassword_button(self):
        if self.oldPassword.text() == '' or self.newPassword1.text() == '' or self.newPassword2.text() == '':
            self.changePasswordButton.setDisabled(True)
        else:
            self.changePasswordButton.setEnabled(True)

    def changePassword(self):
        oldPassword = self.oldPassword.text()
        newPassword1 = self.newPassword1.text()
        newPassword2 = self.newPassword2.text()
        role = self.login[0]
        if role == 's':
            checkPassword = self.cur.execute(
                "SELECT password FROM student WHERE login = ?", (self.login, )).fetchone()[0]
        elif role == 't':
            checkPassword = self.cur.execute(
                "SELECT password FROM teacher WHERE login = ?", (self.login, )).fetchone()[0]
        elif role == 'a':
            checkPassword = self.cur.execute(
                "SELECT password FROM admin WHERE login = ?", (self.login,)).fetchone()[0]

        if oldPassword != checkPassword:
            QMessageBox.critical(
                self, "Ошибка ", "Неверно введён старый пароль")
            self.oldPassword.setText("")
            return

        if newPassword1 != newPassword2:
            QMessageBox.critical(
                self, "Ошибка ", "Новые пароли не совпадают")
            self.newPassword1.setText("")
            self.newPassword2.setText("")
            return

        if role == 's':
            call = f'UPDATE student\nSET password = "{newPassword2}"\n WHERE login = "{self.login}"'
        elif role == 't':
            call = f'UPDATE teacher\nSET password = "{newPassword2}"\n WHERE login = "{self.login}"'
        elif role == 'a':
            call = f'UPDATE admin\nSET password = "{newPassword2}"\n WHERE login = "{self.login}"'

        self.cur.execute(call)
        self.con.commit()
        QMessageBox.information(
            self, "Успешно изменено!", f"Новый пароль: {newPassword1}")

        self.oldPassword.setText("")
        self.newPassword1.setText("")
        self.newPassword2.setText("")


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
