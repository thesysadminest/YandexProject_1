import sqlite3
import sy
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLCDNumber, QLabel, QMainWindow, QDialog
from PyQt5 import uic
con = sqlite3.connect('14. Защита проекта QT/db.sqlite')
cur = con.cursor()


class MainProgram(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui.ui', self)

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
