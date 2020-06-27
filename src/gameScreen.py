#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg, QtSvg as qsvg)

from gridWidget import Grid


class GameScreen(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super(GameScreen, self).__init__(*args, **kwargs)

        self.playerGrid = self.createGridWidget()
        self.layout = qtw.QGridLayout()
        self.layout.addWidget(self.playerGrid)
        self.show()


    def createGridWidget(self):
        widget = qtw.QWidget()
        playerView = qtw.QGraphicsView(widget)
        grid = Grid(playerView)
        playerView.setScene(grid)
        return widget


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    GameScreen()
    sys.exit(app.exec_())
