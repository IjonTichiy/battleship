#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from random import choice
from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg, QtSvg as qsvg)


from gridWidget import Grid
# from .gridWidget import Grid

source_dir = Path(__file__).absolute().parent.parent


class HelpWindow(qtw.QMessageBox):
    """
    displays the rules and shows controls
    """
    def __init__(self, *args, **kwargs):
        super(HelpWindow, self).__init__(*args, **kwargs)


class StatusBar(qtw.QWidget):

    def __init__(self, *args, **kwargs):

        super(StatusBar, self).__init__(*args, **kwargs)

        self.layout = qtw.QGridLayout()
        self.status = qtw.QLabel("Place Your Ships!")
        self.helphint = qtw.QLabel('Press ? for help')
        self.btn_startGame = qtw.QPushButton("Start Game")
        self.layout.addWidget(self.btn_startGame, 0, 0)
        self.layout.addWidget(self.status, 0, 1)
        self.layout.addWidget(self.helphint, 0, 2)

        self.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)

        self.setLayout(self.layout)

    def setStatus(self, text):
        self.status.setText(text)


class GameScreen(qtw.QWidget):

    def __init__(self, *args, parent=None, **kwargs):
        super(GameScreen, self).__init__(*args, **kwargs)

        self.parent = parent

        self.player = qtw.QWidget()
        self.enemy = qtw.QWidget()
        self.statusBar = StatusBar()

        self.layout = qtw.QGridLayout()

        self.layout.addWidget(self.enemy, 0, 0, 1, 2)
        self.layout.addWidget(self.player, 0, 2, 1, 2)
        self.layout.addWidget(self.statusBar, 1, 0, 1, 4)
        self.setLayout(self.layout)

        self.playerView = qtw.QGraphicsView(self.player)
        self.playerScene = Grid(self.playerView, gridType='player')
        self.playerView.setScene(self.playerScene)

        self.enemyView = qtw.QGraphicsView(self.enemy)
        self.enemyScene = Grid(self.enemyView, gridType='enemy')
        self.enemyView.setScene(self.enemyScene)

        self.setGeometry(300, 300, 400, 300)
        self.connect()
        self.show()

    def connect(self):
        self.statusBar.btn_startGame.clicked.connect(self.startGame)

    def startGame(self):

        if not self.playerScene.checkReady():
            self.statusBar.setStatus(
                    'Ships are not placed according to rules!')
            return

        for ship in self.playerScene.ships: ship.disableDrag()

        self.runGameLoop()

    def runGameLoop(self):

        Grid.currentPlayer = choice(('player', 'enemy'))
        gameFinished = False

        self.statusBar.setStatus(f"{Grid.currentPlayer}'s Turn!")

        while (not gameFinished):
            qtw.QApplication.processEvents()
            if Grid.currentPlayer == 'player':
                self.playerTurn()
            elif Grid.currentPlayer == 'enemy':
                self.enemyTurn()

    def playerTurn(self):

        if not self.enemyScene.fieldSelected: return
        field = self.enemyScene.fieldSelected
        self.enemyScene.fieldSelected = None
        print(field)

    def enemyTurn(self):
        pass

    def showHelp(self):

        self.messageBox = qtw.QMessageBox()
        self.messageBox.setIcon(qtw.QMessageBox.Information)
        self.messageBox.setStandardButtons(qtw.QMessageBox.Ok)
        self.messageBox.setDefaultButton(qtw.QMessageBox.Ok)
        with open(source_dir / 'rsc/helptext.txt') as helptext:
            self.messageBox.setText(helptext.read())
        self.messageBox.exec_()

    def keyPressEvent(self, event):
        super(GameScreen, self).keyPressEvent(event)
        print(event.key())
        if event.key() == 63:               # ? press to open help
            self.showHelp()
        elif event.key() == 16777216:       # exit when pressing escape
            sys.exit()



if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    gameScreen = GameScreen()
    sys.exit(app.exec_())
