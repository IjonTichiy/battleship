#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg, QtSvg as qsvg)
import qdarkstyle
style = qdarkstyle.load_stylesheet_pyqt5()


class Ship(qsvg.QGraphicsSvgItem):

    ids = {
            'Carrier': 'rsc/Carrier.svg',
            'Battleship': 'rsc/Battleship.svg',
            'Submarine': 'rsc/Submarine.svg',
            'Cruiser': 'rsc/Cruiser.svg',
            'Destroyer': 'rsc/Destroyer.svg'}

    scalings = {
            'Battleship': 1.2,
            'Carrier': 1.5,
            'Submarine': 0.9
            }

    def __init__(self, ship_id, parent=None):

        if ship_id not in self.ids.keys():
            raise NotImplementedError(ship_id)

        super(Ship, self).__init__(self.ids[ship_id])
        self.setScale(self.scalings[ship_id])



class Scene(qtw.QGraphicsScene):
    """
    contains data
    """

    gridSize = (10, 10)
    rectSize = 30

    def __init__(self, parent, ):

        super(Scene, self).__init__(parent)
        self.setSceneRect(0, 0, 600, 400)
        self.createGrid(*self.gridSize)
        ship1 = self.addShip('Carrier')
        ship1.setPos(30,10)
        print(ship1.boundingRegion())
        ship2 = self.addShip('Battleship')
        ship2.setPos(30, 90)
        ship3 = self.addShip('Submarine')
        ship3.setPos(30, 190)

    def createGrid(self, height, width):
        rectSize = self.rectSize

        self.fields = [
                [self.addRect(
                    rectSize*(1+x), rectSize*(1+y), rectSize, rectSize)
                 for x in range(width)]
                for y in range(height)]

        self.column_ids = [
                self.addText(letter) for letter in
                [chr(65 + i) for i in range(self.gridSize[1])]]
        [x.setPos(rectSize*(1.5 + i), rectSize*.5)
         for i, x in enumerate(self.column_ids)]

        self.row_ids = [
                self.addText(letter) for letter in
                [str(i) for i in range(1, self.gridSize[0])]]
        [x.setPos(rectSize*.5, rectSize*(1.5+i))
         for i, x in enumerate(self.row_ids)]

    def addShip(self, ship_id):
        ship = Ship(ship_id, self)
        self.addItem(ship)
        return ship


class View(qtw.QGraphicsView):
    """
    displays data
    """

    def __init__(self, parent=None, scene=None):

        super(View, self).__init__(parent)

        self.setScene(Scene(self))
        self.setMouseTracking(True)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    app.setStyleSheet(style)
    widget = qtw.QWidget()
    playerView = View(widget)
    widget.setGeometry(300, 300, 400, 300)
    widget.show()

    sys.exit(app.exec_())


