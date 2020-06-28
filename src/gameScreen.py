#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from random import choice, randrange
from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg, QtSvg as qsvg)
from time import sleep


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
        self.btn_startGame = qtw.QPushButton('Start Game')
        self.btn_randomize = qtw.QPushButton('Randomize')
        self.btn_exitGame = qtw.QPushButton('Exit')
        self.layout.addWidget(self.btn_startGame, 0, 0)
        self.layout.addWidget(self.btn_randomize, 0, 1)
        self.layout.addWidget(self.status, 0, 2)
        self.layout.addWidget(self.helphint, 0, 3)

        self.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)

        self.setLayout(self.layout)

    def setStatus(self, text):
        self.status.setText(text)

    def enterGameMode(self):
        self.btn_randomize.setEnabled(False)
        self.btn_randomize.disconnect()
        self.layout.removeWidget(self.btn_randomize)
        self.btn_randomize.deleteLater()
        self.btn_startGame.setEnabled(False)
        self.btn_startGame.disconnect()
        self.layout.removeWidget(self.btn_startGame)
        self.btn_startGame.deleteLater()
        self.layout.addWidget(self.btn_exitGame, 0, 0)


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
        self.playerScene.randomizePlacement()
        self.playerScene.enableDrag()
        self.playerView.setScene(self.playerScene)

        self.enemyView = qtw.QGraphicsView(self.enemy)
        self.enemyScene = Grid(self.enemyView, gridType='enemy')
        # self.enemyScene.randomizePlacement()
        # self.enemyScene.setShipVisibility(False)
        self.enemyView.setScene(self.enemyScene)

        self.setGeometry(300, 300, 400, 300)
        self.connect()
        self.show()

    def connect(self):
        self.statusBar.btn_startGame.clicked.connect(
                self.startGame)
        self.statusBar.btn_randomize.clicked.connect(
                self.playerScene.randomizePlacement)
        self.statusBar.btn_exitGame.clicked.connect(
                self.exitGame)

    def startGame(self):

        if not self.playerScene.checkReady():
            self.statusBar.setStatus(
                    'Ships are not placed according to rules!')
            return

        self.playerScene.finalizePlacement()
        self.statusBar.enterGameMode()
        self.runGameLoop()

    def exitGame(self):
        self.parent.exitGame()

    def runGameLoop(self):

        Grid.currentPlayer = choice(('player', 'enemy'))

        while (not Grid.gameFinished):
            self.statusBar.setStatus(f"{Grid.currentPlayer}'s Turn!")
            qtw.QApplication.processEvents()
            if not self.isAlive():
                sys.exit()

            if Grid.currentPlayer == 'player':
                self.playerTurn()
            elif Grid.currentPlayer == 'enemy':
                self.enemyTurn()

    def isAlive(self):
        if self.parent:
            if not self.parent.isVisible(): return False
            else: return True
        else:
            if not self.isVisble(): return False
            else: return True

    def playerTurn(self):

        if not self.enemyScene.fieldSelected: return
        field = self.enemyScene.fieldSelected
        self.enemyScene.fieldSelected = None
        field.hit()
        Grid.currentPlayer = 'enemy'

    def enemyTurn(self):
        sleep(0.2)
        target = (randrange(0, Grid.gridSize[1]),
                  randrange(0, Grid.gridSize[0]))

        self.playerScene.fields(*target).hit()
        Grid.currentPlayer = 'player'

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
