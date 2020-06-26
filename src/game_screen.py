#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pudb
from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg, QtSvg as qsvg)
import qdarkstyle


Options = {
        'gridSize'
        }


class Ship(qsvg.QGraphicsSvgItem):

    ids = {
            'Carrier': 'rsc/Carrier.svg',
            'Battleship': 'rsc/Battleship.svg',
            'Submarine': 'rsc/Submarine.svg',
            'Cruiser': 'rsc/Cruiser.svg',
            'Destroyer': 'rsc/Destroyer.svg'}

    _scaling = {
            'Carrier': 1.45,
            'Battleship': 1.15,
            'Submarine': .9,
            'Cruiser': .9,
            'Destroyer': .6 }

    _extent = {
            'Carrier': 5,
            'Battleship': 4,
            'Submarine': 3,
            'Cruiser': 3,
            'Destroyer': 2 }

    @property
    def extent(self):
        return self._extent[self.id]

    @property
    def scaling(self):
        return self._scaling[self.id]

    def __init__(self, ship_id, parent):
        """
        This class provides the basic functionality to place ships at the
        beginning of the game.

        ship_id can be one of the following:
            [Carrier, Battleship, Cruiser, Submarine, Destroyer]
        """

        if ship_id not in self.ids.keys():
            raise NotImplementedError(ship_id)

        self.id = ship_id
        self.parent = parent
        self.index = None
        super(Ship, self).__init__(self.ids[ship_id])
        self._orientation = 'h'
        self.setToolTip(ship_id)
        self.setScale(self.scaling*parent.rectSize/30)
        self.enableDrag()

    def enableDrag(self):
        """
        allow to move ships at beginning of game (preparation mode)
        """
        self.setFlag(qtw.QGraphicsItem.ItemIsSelectable)
        self.setFlag(qtw.QGraphicsItem.ItemIsMovable)
        self.setFlag(qtw.QGraphicsItem.ItemIsFocusable)
        self.setFlag(qtw.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(qtw.QGraphicsItem.ItemSendsScenePositionChanges)

    def disableDrag(self):
        """
        disable movement when game starts
        """
        self.setFlag(qtw.QGraphicsItem.ItemIsNotSelectable)
        self.setFlag(qtw.QGraphicsItem.ItemIsNotMovable)
        self.setFlag(qtw.QGraphicsItem.ItemIsNotFocusable)
        self.setFlage(qtw.QGraphicsItem.ItemNotSendGeometryChanges)
        self.setFlag(qtw.QGraphicsItem.ItemNotSendsScenePositionChanges)

    def positionAt(self, i, j):
        self.setPos((1 + j)*self.parent.rectSize, (1 + i)*self.parent.rectSize)

    def mousePressEvent(self, event):
        super(Ship, self).mousePressEvent(event)
        if self.parent.gameMode == 'preparation':
            self.parent.markState(self, False)

    def mouseReleaseEvent(self, event):
        super(Ship, self).mouseReleaseEvent(event)
        if self.parent.gameMode == 'preparation':
            self.parent.markState(self, True)

    def mouseMoveEvent(self, event):
        super(Ship, self).mouseMoveEvent(event)
        if self.parent.gameMode == 'preparation':
            self.snapToGrid()

    def keyPressEvent(self, event):
        print(event.key())
        if self.parent.gameMode == 'preparation':

            if event.key() == 32:  # space
                self.parent.markState(self, False)
                self.rotateShip()

    def snapToGrid(self):
        for i, row in enumerate(self.parent.fields):

            contain_check = [x.contains(self.pos()) for x in row]

            if not any(contain_check):
                continue

            i, j, field = self.getValidField(i, row, contain_check)

            if self._orientation == 'h':
                pos = qtc.QPointF(field.x(), field.y())
            elif self._orientation == 'v':
                pos = qtc.QPointF(field.x(), field.y() + self.parent.rectSize)

            self.setPos(pos)
            self.index = (i, j)
            break

        else:

            self.index = (0, 0)
            if self._orientation == 'h':
                origin = self.parent.fields[0][0]
                self.setPos(origin.x(), origin.y())
            if self._orientation == 'v':
                origin = self.parent.fields[self.extent][0]
                self.setPos(origin.x(), origin.y())

    def getValidField(self, i, row, contain_check):

        j, field = [(j, x) for j, x in enumerate(row)
                    if contain_check[j]][0]

        # check if ship is out of bounds in x-direction
        if (
                self._orientation == 'h' and
                j + self.extent >= self.parent.gridSize[0]):
            j = self.parent.gridSize[0] - self.extent
            field = row[j]

        # check if ship is out of bounds in y-direction
        if (
                self._orientation == 'v' and
                i - self.extent < 0):
            i = self.extent - 1
            field = self.parent.fields[i][j]

        return i, j, field

    def rotateShip(self):

        i, j = self.index
        if self._orientation == 'h':
            if i - self.extent < 0:
                i = self.extent - 1
            self.setRotation(-90)
            self.positionAt(i+1, j)
            self._orientation = 'v'

        elif self._orientation == 'v':
            if j + self.extent > self.parent.gridSize[0]:
                j = self.parent.gridSize[0] - self.extent
                i -= 1
            self.rotateAroundCenter(0)
            self.positionAt(i, j)
            self._orientation = 'h'

        self.index = (i, j)
        self.parent.markState(self, True)

    def rotateAroundCenter(self, angle):
        """
        TODO: rotate around center and not upper left corner
        """
        self.setRotation(angle)


class CenteredTextItem(qtw.QGraphicsTextItem):
    """
    subclass of text item where positioning is done at the center and not the
    upper left corner of the bounding box
    """
    def centerAt(self, pos):
        self.setPos(pos - self.boundingRect().center())


class GridField(qtc.QRectF):

    def __init__(self, *args, **kwargs):

        super(GridField, self).__init__(*args, **kwargs)
        self.occupied = False


class Scene(qtw.QGraphicsScene):
    """
    contains data
    """

    gridSize = (10, 11)
    rectSize = 40
    gameMode = 'preparation'

    def __init__(self, parent):

        super(Scene, self).__init__(parent)
        self.setSceneRect(0, 0, 700, 470)
        self.createGrid(*self.gridSize)
        self.ships = []
        for i, ship_id in enumerate(Ship.ids.keys()):
            self.addShip(i, ship_id)

    def createGrid(self, width, height):

        rectSize = self.rectSize
        self.column_ids = []
        self.row_ids = []
        self.fields = []
        for y in range(height):
            row = []
            for x in range(width):
                rect = GridField(
                        rectSize*(1+x), rectSize*(1+y), rectSize, rectSize)
                self.addRect(rect)
                row.append(rect)
            self.fields.append(row)

        for i in range(width):
            letter = chr(65+i)
            pos = qtc.QPointF(rectSize*(1.5 + i), rectSize*.5)
            item = CenteredTextItem(letter)
            self.addItem(item)
            item.centerAt(pos)
            self.column_ids.append(item)

        for i in range(height):
            pos = qtc.QPointF(rectSize*.5, rectSize*(1.5 + i))
            item = CenteredTextItem(str(1 + i))
            self.addItem(item)
            item.centerAt(pos)
            self.row_ids.append(item)

    def addShip(self, i, ship_id):
        ship = Ship(ship_id, self)
        index = (i, self.gridSize[0] - ship.extent)
        ship.positionAt(*index)
        ship.index = index
        self.markState(ship)
        self.addItem(ship)
        self.ships.append(ship)

    def markState(self, ship, value=True):
        index = ship.index
        for extent in range(ship.extent):
            if ship._orientation == 'h':
                print(index)
                self.fields[index[0]][index[1] + extent].occupied = value
            elif ship._orientation == 'v':
                self.fields[index[0] - extent][index[1]].occupied = value

        self.printOccupied()

    def printOccupied(self):
        for row in self.fields:
            print([field.occupied for field in row])
        print('\n')


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
    style = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(style)
    widget = qtw.QWidget()
    playerView = View(widget)
    widget.setGeometry(300, 300, 400, 300)
    widget.show()

    sys.exit(app.exec_())


