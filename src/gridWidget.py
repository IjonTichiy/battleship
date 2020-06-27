#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg, QtSvg as qsvg)
import qdarkstyle


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

    def enableDrag(self):
        """
        allow to move ships at beginning of game (preparation mode)
        """
        self.setFlag(qtw.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(qtw.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(qtw.QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(qtw.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(qtw.QGraphicsItem.ItemSendsScenePositionChanges, True)

    def disableDrag(self):
        """
        disable movement when game starts
        """
        self.setFlag(qtw.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(qtw.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(qtw.QGraphicsItem.ItemIsFocusable, False)
        self.setFlag(qtw.QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setFlag(qtw.QGraphicsItem.ItemSendsScenePositionChanges, False)

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
        if self.parent.gameMode == 'preparation':
            if event.key() == 32:  # space
                self.parent.markState(self, False)
                self.rotateShip()

    def snapToGrid(self):
        """
        find the grid field which contains the upper left corner of the
        ship and quantize the position to
        """
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
            """
            this will be executed when the current position is not inside one
            of the grid fields. The position is then set to the the upper left
            corner (origin) of the whole grid
            """
            self.index = (0, 0)
            if self._orientation == 'h':
                origin = self.parent.fields[0][0]
                self.setPos(origin.x(), origin.y())
            if self._orientation == 'v':
                origin = self.parent.fields[self.extent][0]
                self.setPos(origin.x(), origin.y())

    def getValidField(self, i, row, contain_check):
        """
        returns the grid field which the ship should be positioned at
        """
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
        """
        Rotate the ship and position it inside the grid if necessary
        """
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
            self.setRotation(0)
            self.positionAt(i, j)
            self._orientation = 'h'
        self.index = (i, j)
        self.parent.markState(self, True)


class CenteredTextItem(qtw.QGraphicsTextItem):
    """
    subclass of text item where positioning is done at the center and not the
    upper left corner of the bounding box
    """
    def centerAt(self, pos):
        self.setPos(pos - self.boundingRect().center())


class GridField(qtc.QRectF):
    """
    single field on the grid. Is needed because we want to mark if the field is
    occupied -> GridField.occupied

    also a simple getter setter implementation is shown examplary
    """

    def __init__(self, index, size, *args, **kwargs):

        super(GridField, self).__init__(
                size*index[0], size*index[1], size, size)
        self._occupied = False
        self._index = index

    @property
    def index(self):
        return self._index

    @property
    def occupied(self):
        return self._occupied

    @occupied.setter
    def occupied(self, value):
        self._occupied = value


class Grid(qtw.QGraphicsScene):
    """
    contains the game data
    """
    gridSize = (10, 11)
    rectSize = 30
    gameMode = 'preparation'

    def __init__(self, parent, *args, player='player', **kwargs):

        super(Grid, self).__init__(parent)
        self.player = player
        self.setSceneRect(0, 0,
                *[self.rectSize*(x + 2) for x in self.gridSize])
        self.createGrid(*self.gridSize)
        self.initPlayer()

    def initPlayer(self):

        if self.player == 'player':

            self.ships = []
            for i, ship_id in enumerate(Ship.ids.keys()):
                index = (i, self.gridSize[0] - Ship._extent[ship_id])
                ship = self.addShip(ship_id, index)
                ship.enableDrag()
                self.ships.append(ship)

    def createGrid(self, width, height):

        rectSize = self.rectSize
        self.column_ids = []
        self.row_ids = []
        self.fields = []
        for y in range(height):
            row = []
            for x in range(width):
                rect = GridField((1 + x, 1 + y), rectSize)
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

    def addShip(self, ship_id, index):
        ship = Ship(ship_id, self)
        ship.positionAt(*index)
        ship.index = index
        self.markState(ship)
        self.addItem(ship)
        return ship

    def markState(self, ship, value=True):
        index = ship.index
        for extent in range(ship.extent):
            if ship._orientation == 'h':
                self.fields[index[0]][index[1] + extent].occupied = value
            elif ship._orientation == 'v':
                self.fields[index[0] - extent][index[1]].occupied = value
        # self.printOccupied()  # for debug

    def printOccupied(self):
        for row in self.fields:
            print([field.occupied for field in row])
        print('\n')

    def getClickedField(self, event):
        for row in self.fields:
            contain_check = [x.contains(event.pos()) for x in row]
            if not any(contain_check): continue
            return [x for j, x in enumerate(row) if contain_check[j]][0]

    def mousePressEvent(self, event):
        super(Grid, self).mousePressEvent(event)
        if self.player == 'enemy':
            field = self.getClickedField(event)
            if not field: return
            print(field.index)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    style = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(style)
    widget = qtw.QWidget()
    playerView = qtw.QGraphicsView(widget)
    playerView.setScene(Grid(playerView, player='enemy'))
    widget.setGeometry(300, 300, 400, 300)
    widget.show()

    sys.exit(app.exec_())


