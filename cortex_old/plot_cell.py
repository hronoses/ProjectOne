# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""
#import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np


class PlotWin(pg.GraphicsWindow):
    def __init__(self, cortex, cell, data='voltage'):
        super(PlotWin, self).__init__()
        self.setWindowTitle('Plot cell')
        self.cor = cortex
        self.cell = cell
        self.plot = data
        self.data = np.empty(100)
        self.cor.live()
        self.weights = self.cor.W.reshape((25, 25))
        self.ptr = 0
        self.initPlots()

    def initPlots(self):
        self.p = self.addPlot()

        self.p.setDownsampling(mode='peak')
        self.p.setClipToView(True)
        self.p.setRange(xRange=[-3000, 0], yRange=[-5,60])
        self.p.setLimits(xMax=0)
        self.curve = self.p.plot()


    def start_timer(self):
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0.01)

    def update(self):
        self.cor.live()
        # self.weights = self.cor.W.reshape((25, 25))
        if self.plot == 'voltage':
            self.data[self.ptr] = self.cell.u
        elif self.plot == 'tag':
            self.data[self.ptr] = self.cell.syn_in[5].tag
        else:
            self.data[self.ptr] = self.cell.prp
        self.ptr += 1
        if self.ptr >= self.data.shape[0]:
            tmp = self.data
            self.data = np.empty(self.data.shape[0] * 2)
            self.data[:tmp.shape[0]] = tmp

        self.curve.setData(self.data[:self.ptr])
        self.curve.setPos(-self.ptr, 0)


def show_plot():
    import sys
    from pyqtgraph.Qt import QtCore, QtGui
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
