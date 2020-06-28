#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg, QtSvg as qsvg)
import pudb
from random import choice, randint
from pathlib import Path

rsc = Path(__file__).absolute().parent.parent / 'rsc'


class HitIcon(qsvg.QGraphicsSvgItem):

    ids = {
            'hit': rsc / 'HitShot.svg',
            'miss': rsc / 'MissedShot.svg'}

    def __init__(self, field, shot):
        super(HitIcon, self).__init__(self.ids[shot])
        self.setPos(field.pos())


class Ship(qsvg.QGraphicsSvgItem):

    ids = {
            'Carrier':      rsc / 'Carrier.svg',
            'Battleship':   rsc /'Battleship.svg',
            'Submarine':    rsc / 'Submarine.svg',
            'Cruiser':      rsc / 'Cruiser.svg',
            'Destroyer':    rsc / 'Destroyer.svg'}

    _scaling = {
            'Carrier':      1.45,
            'Battleship':   1.15,
            'Submarine':    .9,
            'Cruiser':      .9,
            'Destroyer':    .6 }

    _extent = {
            'Carrier':      5,
            'Battleship':   4,
            'Submarine':    3,
            'Cruiser':      3,
            'Destroyer':    2 }

    _orientation_angle = {
            'h':            0,
            'v':            -90}

    @property
    def extent(self):
        return self._extent[self.id]

    @property
    def scaling(self):
        return self._scaling[self.id]

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = value

    def __init__(self, ship_id, parent, orientation='h'):
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
        self._index = None
        super(Ship, self).__init__(self.ids[ship_id])
        self.orientation = orientation
        self.setRotation(self._orientation_angle[orientation])
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

    def mouseReleaseEvent(self, event):
        super(Ship, self).mouseReleaseEvent(event)
        self.parent.markState()

    def mouseMoveEvent(self, event):
        super(Ship, self).mouseMoveEvent(event)
        self.snapToGrid()

    def keyPressEvent(self, event):
        if event.key() == 32:  # space
            self.rotateShip()
            self.parent.markState()

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
            if self.orientation == 'h':
                pos = qtc.QPointF(field.x(), field.y())
            elif self.orientation == 'v':
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
            if self.orientation == 'h':
                origin = self.parent.fields[0][0]
                self.setPos(origin.x(), origin.y())
            if self.orientation == 'v':
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
                self.orientation == 'h' and
                j + self.extent >= self.parent.gridSize[0]):
            j = self.parent.gridSize[0] - self.extent
            field = row[j]
        # check if ship is out of bounds in y-direction
        if (
                self.orientation == 'v' and
                i - self.extent < 0):
            i = self.extent - 1
            field = self.parent.fields[i][j]
        return i, j, field

    def rotateShip(self):
        """
        Rotate the ship and position it inside the grid if necessary
        """
        i, j = self.index
        if self.orientation == 'h':
            self.orientation = 'v'
            if i - self.extent < 0:
                i = self.extent - 1
            self.setRotation(-90)
            self.positionAt(i+1, j)
        elif self.orientation == 'v':
            self.orientation = 'h'
            if j + self.extent > self.parent.gridSize[0]:
                j = self.parent.gridSize[0] - self.extent
                i -= 1
            self.setRotation(0)
            self.positionAt(i, j)
        self.index = (i, j)


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
        self._index = (index[0] - 1, index[1] - 1)
        self._hit = False

    @property
    def index(self):
        return self._index

    @property
    def occupied(self):
        return self._occupied

    @occupied.setter
    def occupied(self, value):
        self._occupied = value

    def setOccupied(self, val):
        if val not in [True, False]:
            raise ValueError
        self._occupied = val

    def hit(self):
        self._hit = True
        self.status = HitIcon()


class Grid(qtw.QGraphicsScene):
    """
    contains the game data
    """
    gridSize = (10, 10)
    rectSize = 30
    gridTypes = ('player', 'enemy')
    currentPlayer = None
    gameFinished = False

    def __init__(self, parent, *args, gridType='player', **kwargs):

        if gridType not in self.gridTypes: raise NotImplementedError
        super(Grid, self).__init__(parent)
        self.ships = []
        self.gridType = gridType
        self.fieldSelected = None
        self.setSceneRect(0, 0,
                *[self.rectSize*(x + 2) for x in self.gridSize])
        self.createGrid(*self.gridSize)

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

    def randomizePlacement(self):

        if self.ships:
            [self.removeShip(ship) for ship in self.ships]

        no = 0
        finished = False
        pu.db
        shipIds = [x for x in Ship.ids.keys()]
        while not finished:
            shipId = shipIds[no]
            extent = Ship._extent[shipId]
            orientation = choice(('v', 'h'))
            if orientation == 'h':
                index = (randint(0, self.gridSize[0] - 1),
                         randint(0, self.gridSize[1] - 1 - extent))
            elif orientation == 'v':
                index = (randint(extent - 1, self.gridSize[0] - 1),
                         randint(0, self.gridSize[1] - 1))
            ship = Ship(shipId, self, orientation)
            try:
                self.addShip(ship, index)
            except Exception:
                pu.db
            ship.enableDrag()
            self.ships.append(ship)
            if not self.checkReady():
                self.removeShip(ship)
            else:
                no += 1
                if no == len(shipIds):
                    finished = True

    def addShip(self, ship, index, visible=True):
        if ship.orientation == 'h':
            ship.positionAt(*index)
        elif ship.orientation == 'v':
            ship.positionAt(index[0] + 1, index[1])
        ship.index = index
        self.addItem(ship)

    def enableDrag(self):
        [ship.enableDrag() for ship in self.ships]

    def disableDrag(self):
        [ship.disableDrag() for ship in self.ships]

    def setShipVisibility(self, val):
        [ship.setVisible(val) for ship in self.ships]

    def removeShip(self, shipToRemove):
        self.ships = [ship for ship in self.ships if not ship == shipToRemove]
        self.removeItem(shipToRemove)

    def markState(self):

        self.resetState()

        for ship in self.ships:
            index = ship.index
            for offset in range(ship.extent):
                if ship.orientation == 'h':
                    self.fields[index[0]][index[1] + offset].occupied = True
                elif ship.orientation == 'v':
                    self.fields[index[0] - offset][index[1]].occupied = True
        self.printOccupied()  # for debug

    def resetState(self):
        for row in self.fields:
            [field.setOccupied(False) for field in row]

    def finalizePlacement(self):
        self.markState()
        for ship in self.ships: ship.disableDrag()

    def checkReady(self):
        """
        check if the ships are placed according to the rules before game start
        """
        check = [[0 for _1 in range(self.gridSize[0])]
                 for _2 in range(self.gridSize[1])]

        for ship in self.ships:
            j, i = ship.index
            extent = ship.extent
            orientation = ship.orientation

            if orientation == 'h':
                indices = [
                        (i - 1, j, 1), (i - 1, j - 1, 1), (i - 1, j + 1, 1),
                        (i + extent, j - 1, 1), (i + extent, j + 1, 1),
                        (i + extent, j, 1)]

                for offset in range(extent):
                    indices.extend([
                        (i+offset, j, 2),
                        (i + offset, j - 1, 1),
                        (i + offset, j + 1, 1)])

            elif orientation == 'v':
                indices = [
                        (i, j + 1, 1), (i - 1, j + 1, 1), (i + 1, j + 1, 1),
                        (i, j - extent, 1), (i - 1, j - extent, 1),
                        (i + 1, j - extent, 1)]

                for offset in range(extent):
                    indices.extend([
                            (i, j - offset, 2),
                            (i - 1, j - offset, 1),
                            (i + 1, j - offset, 1)])

            for i_, j_, val in indices:
                if (i_ < 0 or i_ >= self.gridSize[0] or
                        j_ < 0 or j_ >= self.gridSize[1]): continue
                check[j_][i_] += val

        print('check:')
        for row in check:
            print([i for i in row])
        print('\n')

        for row in check:
            if any([x > 2 for x in row]):
                return False
        else:
            return True

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
        if self.gridType == 'enemy':
            field = self.getClickedField(event)
            if not field or Grid.currentPlayer == 'enemy': return
            self.fieldSelected = field


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    widget = qtw.QWidget()
    player = qtw.QWidget()
    enemy = qtw.QWidget()
    layout = qtw.QGridLayout()
    layout.addWidget(enemy, 0, 0, 5, 1)
    layout.addWidget(player, 5, 0, 5, 1)
    widget.setLayout(layout)

    playerView = qtw.QGraphicsView(player)
    playerView.setScene(Grid(playerView, gridType='player'))

    enemyView = qtw.QGraphicsView(enemy)
    enemyView.setScene(Grid(enemyView, gridType='enemy'))

    widget.setGeometry(300, 300, 400, 300)
    widget.show()

    sys.exit(app.exec_())


