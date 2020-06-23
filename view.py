#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from PyQt5 import (QtWidgets as qtw, QtCore as qtc)


class LoginDialog(qtw.QInputDialog):
    def __init__(self, *args, **kwargs):
        super(LoginDialog, self).__init__()


class MainWindow(qtw.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(qtw.QMainWindow, self).__init__()

        self.username = None
        ok = False

        while not (self.username and ok):

            username, ok = qtw.QInputDialog().getText(
                    self,
                    "QInputDialog().getText()",
                    "Please enter your name:",
                    qtw.QLineEdit.Normal)

            if username and ok:
                self.username = ok


def start():
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start()
