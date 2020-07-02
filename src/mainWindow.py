#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)

from .gameScreen import GameScreen


class MainWindow(qtw.QMainWindow):

    style = """
    #mainButtons{
    border-image: url(rsc/MainWindow.jpg) 0 0 0 0 stretch stretch;
    }
    #gameWindow{
    border-image: url(rsc/GameWindow.jpg) 0 0 0 0 stretch stretch;
    }
    """

    username = None

    def __init__(self, parent=None, *args, **kwargs):

        super(MainWindow, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle('battleship V0.1')
        self.setObjectName("mainwindow")
        self.getUserName()
        self.createButtons()
        self.initUI()
        self.showFullScreen()
        self.setMinimumSize(800, 400)

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
            if ok and not self.username: self.username = 'user'
            if username: self.username = username

    def initUI(self):

        self.stackWidget = qtw.QStackedWidget(objectName='centralWidget')
        self.stackWidget.setStyleSheet(self.style)
        self.stackWidget.addWidget(self.mainMenu)
        self.setCentralWidget(self.stackWidget)
        self.connect()

    def createButtons(self):

        self.mainMenu = qtw.QWidget(objectName='mainButtons')
        self.mainButtons = qtw.QWidget()
        buttonBox = qtw.QGridLayout()
        buttonBox.addWidget(self.mainButtons, 1, 1)
        self.mainMenu.setLayout(buttonBox)

        sizePolicy = qtw.QSizePolicy.Maximum

        self.mainButtons.setSizePolicy(sizePolicy, sizePolicy)

        self.btn_newGame = qtw.QPushButton(
                "New Game", objectName='button:new game')
        self.btn_options = qtw.QPushButton(
                "Options", objectName='button:options')
        self.btn_exit = qtw.QPushButton(
                "Exit", objectName='button:exit')

        self.btn_newGame.setSizePolicy(sizePolicy, sizePolicy)
        self.btn_options.setSizePolicy(sizePolicy, sizePolicy)
        self.btn_exit.setSizePolicy(sizePolicy, sizePolicy)

        buttonLayout = qtw.QVBoxLayout()
        buttonLayout.addWidget(self.btn_newGame)
        buttonLayout.addWidget(self.btn_options)
        buttonLayout.addWidget(self.btn_exit)
        self.mainButtons.setLayout(buttonLayout)

    def showGameScreen(self):
        self.gameScreen = GameScreen(parent=self)
        self.stackWidget.addWidget(self.gameScreen)
        self.stackWidget.setCurrentWidget(self.gameScreen)

    def connect(self):
        self.btn_newGame.clicked.connect(self.showGameScreen)

    def exitGame(self):
        self.stackWidget.removeWidget(self.gameScreen)
        self.gameScreen.deleteLater()
        self.gameScreen = None
        self.stackWidget.setCurrentWidget(self.mainMenu)


def start():
    app = qtw.QApplication(sys.argv)
    style = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(style)
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start()
