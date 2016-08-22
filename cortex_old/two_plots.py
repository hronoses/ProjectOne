# -*- coding: utf-8 -*-
"""
Created on Thu Nov 06 16:49:28 2014

@author: Hronos
"""
import sys

import numpy as np
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore

import cortex_memory
from plot_cell import PlotWin

t_step = 0.001
max_time = 100
time = np.arange(0., max_time, t_step)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
       super(MainWindow, self).__init__()
       self.initUI()

    def initUI(self):
        self.resize(1000, 650)
        self.setWindowTitle('ProjectOne')
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)

        c = cortex_memory.Cortex(dimension=(1, 1, 625))
        self.plot = PlotWin(cortex=c, cell=c.cell, data='voltage')
        self.plot2 = PlotWin(cortex=c, cell=c.cell, data='tag')

        layout = QtGui.QGridLayout()
        layout.setSpacing(10)


        layout.addWidget(self.plot, 0, 1)  # plot goes on right side, spanning 3 rows
        layout.addWidget(self.plot2, 1, 1)

        self.widget.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0.01)

    def update(self):
        self.plot.update()
        self.plot2.update()
        # if np.random.randint(10) == 5:
        #     self.plot2.setImage(self.plot.weights,autoRange=False, autoLevels=False, levels=(-5, 5))


if __name__ == "__main__":
    pg.setConfigOption('background', (255,255,255))
    pg.setConfigOption('foreground', (0,0,0))
    app = QtGui.QApplication([])
    win = MainWindow()
    # mycell = Cell(params=(0.02, -0.1, -55, 6, 30), koef=(0.04, 5, 140), init=(-70, -20) )
    # comPar.setParams(mycell)
    # comPar.setObj(mycell)
    win.show()
    sys.exit(app.exec_())     
