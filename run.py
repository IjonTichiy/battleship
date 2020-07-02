#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import qdarkstyle
from PyQt5 import (QtWidgets as qtw, QtCore as qtc, QtGui as qtg)
from src import MainWindow

app = qtw.QApplication(sys.argv)
style = qdarkstyle.load_stylesheet_pyqt5()
app.setStyleSheet(style)
window = MainWindow()
sys.exit(app.exec_())
