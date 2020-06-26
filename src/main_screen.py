#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
import qdarkstyle


class MainWindow(qtw.QMainWindow):

    style = """
    #centralWidget{
    border-image: url(rsc/MainWindow.jpg) 0 0 0 0 stretch stretch;
    }
    """

    username = None

    def __init__(self, *args, **kwargs):

        super(MainWindow, self).__init__()

        self.setWindowTitle('battleship V0.1')
        self.setObjectName("mainwindow")
        self.getUserName()
        self.initUI()
        self.showMaximized()
        self.setFixedSize(self.startMenu.size())

    def getUserName(self):
        """
        open a QDialog to get the username and save it as self.username. Close
        the application if the user presses cancel at QDialog
        """
        while not (self.username):
            username, ok = qtw.QInputDialog().getText(
                    self, "QInputDialog().getText()",
                    "Welcome to battleship!\nPlease enter your name:",
                    qtw.QLineEdit.Normal)
            if not ok: sys.exit()
            if username: self.username = ok

    def initUI(self):

        self.startMenu = qtw.QWidget(objectName='centralWidget')
        self.startMenu.setStyleSheet(self.style)
        self.setCentralWidget(self.startMenu)

        self.mainButtons = qtw.QWidget()
        self.mainButtons.setSizePolicy(
                qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)

        self.btn_newGame = qtw.QPushButton(
                "New Game", objectName='button:new game')
        self.btn_newGame.setSizePolicy(
                qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)

        self.btn_options = qtw.QPushButton(
                "Options", objectName='button:options')
        self.btn_options.setSizePolicy(
                qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)

        self.btn_exit = qtw.QPushButton(
                "Exit", objectName='button:exit')
        self.btn_exit.setSizePolicy(
                qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)


        buttonLayout = qtw.QVBoxLayout()
        buttonLayout.addWidget(self.btn_newGame)
        buttonLayout.addWidget(self.btn_options)
        buttonLayout.addWidget(self.btn_exit)
        self.mainButtons.setLayout(buttonLayout)

        layout = qtw.QGridLayout()
        layout.addWidget(self.mainButtons, 1, 1)

        self.startMenu.setLayout(layout)


class GameWindow(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super(GameWindow, self).__init__()

        self.show()

    def createCanvas(self):
        self.playerScreen = qtc.QLabel()


def start():
    app = qtw.QApplication(sys.argv)
    style = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(style)
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start()
