# -*- coding: utf-8 -*-
"""
Created on Thu Nov 06 16:49:28 2014

@author: Hronos
"""
import sys

import numpy as np
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from PyQt4 import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree

import cortex_memory
from plot_cell import PlotWin

t_step = 0.001
max_time = 100
time = np.arange(0., max_time, t_step)

class Cell():
    
    def __init__(self, params = (0,0,0,0,0), koef = (0,0,0), init = (0,0)):
        self.a = params[0]
        self.b = params[1]
        self.c = params[2]
        self.d = params[3]
        self.Vthr = params[4]
        
        self.k1 = koef[0]
        self.k2 = koef[1]
        self.k3 = koef[2]
        
        self.V0 = init[0]
        self.U0 = init[1]
        self.V = np.zeros(time.size)
        self.V[0] = init[0]
        self.U = np.zeros(time.size)
        self.U[0] = init[1]
        
        self.I = 0


class ComplexParameter(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)
        
        self.addChild({'name': 'a', 'type': 'float', 'value': 0.02, 'step': 0.001})
        self.addChild({'name': 'b', 'type': 'float', 'value':-0.1, 'step': 0.001})
        self.addChild({'name': 'c', 'type': 'float', 'value': -55, 'step': 1})        
        self.addChild({'name': 'd', 'type': 'float', 'value': 6, 'step': 0.5})        
        self.addChild({'name': 'k1', 'type': 'float', 'value': 0.04, 'step': 0.001})        
        self.addChild({'name': 'k2', 'type': 'float', 'value': 5, 'step': 0.5})        
        self.addChild({'name': 'k3', 'type': 'float', 'value': 140, 'step': 5})  
        self.addChild({'name': 'Vthr', 'type': 'float', 'value': 30, 'step': 5})  
        self.addChild({'name': 'V0', 'type': 'float', 'value': -70, 'step': 5})  
        self.addChild({'name': 'U0', 'type': 'float', 'value': -20, 'step': 5})  
        self.addChild({'name': 'Icr', 'type': 'float', 'value': 0,'readonly': True})   
        self.a = self.param('a')
        self.b = self.param('b')
        self.c = self.param('c')
        self.d = self.param('d')
        self.k1 = self.param('k1')
        self.k2 = self.param('k2')
        self.k3 = self.param('k3')
        self.Vthr = self.param('Vthr')
        self.V0 = self.param('V0')
        self.U0 = self.param('U0')
        self.Icr = self.param('Icr')
        self.k2.sigValueChanged.connect(self.findIcr)
        self.b.sigValueChanged.connect(self.findIcr)
        self.k3.sigValueChanged.connect(self.findIcr)
        self.k1.sigValueChanged.connect(self.findIcr)
        
        self.Vthr.sigValueChanged.connect(self.exchangeParams)
        self.a.sigValueChanged.connect(self.exchangeParams)
        self.b.sigValueChanged.connect(self.exchangeParams)
        self.c.sigValueChanged.connect(self.exchangeParams)
        self.d.sigValueChanged.connect(self.exchangeParams)
        self.k1.sigValueChanged.connect(self.exchangeParams)
        self.k2.sigValueChanged.connect(self.exchangeParams)
        self.k3.sigValueChanged.connect(self.exchangeParams)
        self.V0.sigValueChanged.connect(self.exchangeParams)
        self.U0.sigValueChanged.connect(self.exchangeParams)
        
        self.findIcr()
        
    def findIcr(self):
        self.Icr.setValue((self.b.value()-self.k2.value())**2/4/self.k1.value()-self.k3.value())
   
    def setParams(self, obj):
        self.a.setValue(obj.a)
        self.b.setValue(obj.b)
        self.c.setValue(obj.c)
        self.d.setValue(obj.d)
        self.k1.setValue(obj.k1)
        self.k2.setValue(obj.k2)
        self.k3.setValue(obj.k3)
        self.Vthr.setValue(obj.Vthr)
        self.V0.setValue(obj.V0)
        self.U0.setValue(obj.U0)
    
    ## BAD place becuase i need to run this one before self.exchangeParams() !!!!!!
    def setObj(self, obj):
        self.myobj = obj
        
        
    def exchangeParams(self):
        self.myobj.a = self.a.value()
        self.myobj.b = self.b.value()
        self.myobj.c = self.c.value()
        self.myobj.d = self.d.value()
        self.myobj.k1 = self.k1.value()
        self.myobj.k2 = self.k2.value()
        self.myobj.k3 = self.k3.value()
        self.myobj.V[0] = self.V0.value()
        self.myobj.U[0] = self.U0.value()
        self.myobj.Vthr = self.Vthr.value()
        
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
       super(MainWindow, self).__init__()
       self.initUI()

    def initUI(self):
        self.resize(1000, 650)
        self.setWindowTitle('ProjectOne')
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)


        comPar =  ComplexParameter(name='Parameters')
        params = [
            comPar,
            {'name': 'Main', 'type': 'group', 'children': [
                {'name': 'Current', 'type': 'float', 'value': 10},
                {'name': 'Time', 'type': 'int', 'value': max_time},
                {'name': 'Time_step', 'type': 'float', 'value': t_step, 'step': 0.001},
                {'name': 'Edit', 'type': 'action'},
            ]},

        ]

        self.p = Parameter.create(name='params', type='group', children=params)
        self.p.param('Main', 'Edit').sigActivated.connect(self.func)
        ## Create two ParameterTree widgets, both accessing the same data
        t = ParameterTree()

        t.setParameters(self.p, showTop=False)
        t.setWindowTitle('pyqtgraph example: Parameter Tree')

        c = cortex_memory.Cortex(dimension=(1, 1, 625))
        self.plot = PlotWin(cortex=c, cell=c.cell)
        self.plot2 = pg.ImageView()
        self.plot2.setImage(self.plot.weights)

        layout = QtGui.QGridLayout()
        layout.setSpacing(10)


        layout.addWidget(t, 0, 0,2,1)   # button goes in upper-left
        layout.addWidget(self.plot, 0, 1)  # plot goes on right side, spanning 3 rows
        layout.addWidget(self.plot2, 1, 1)

        self.widget.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

    def update(self):
        self.plot.update()
        if np.random.randint(10) == 5:
            self.plot2.setImage(self.plot.weights,autoRange=False, autoLevels=False, levels=(-5, 5))

    def func(self):
        global max_time, t_step, time
        # mycell.I = p.param('Main','Current').value()
        # max_time = p.param('Main','Time').value()
        # t_step = p.param('Main','Time_step').value()
        # mycell.evolve()
        # plot.clear()
        # plot2.clear()
        # mycell.pgplot()

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
