# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.Vector import Vector
import pyqtgraph.opengl as gl
# import time
# import numpy as np
# import random

class MyView(gl.GLViewWidget):

    def __init__(self):
        super(MyView, self).__init__()
        self.opts = {
            'center': Vector(0,0,20),  ## will always appear at the center of the widget
            'distance': 100.0,         ## distance of camera from center
            'fov':  60,               ## horizontal field of view in degrees
            'elevation':  0,         ## camera's angle of elevation in degrees
            'azimuth': 0,            ## camera's azimuthal angle in degrees
                                      ## (rotation around z-axis 0 points along x-axis)
            'viewport': None,         ## glViewport params; None == whole widget
        }

    def setup(self, data, env_data=None, pred_data=None):
        self.data = data
        self.env_data = env_data
        self.pred_data = pred_data
        self.speed = 50
        self.step = 0
        self.vox = gl.GLVolumeItem(self.data[self.step], 5, False)
        # self.zgrid = gl.GLGridItem(color = (0,0,0,1))
        # self.zgrid.scale(10, 20, 1)
        self.addItem(self.vox)
        self.setCameraPosition(None,100,0,0)
        self.setBackgroundColor('w')
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.process)
        self.showSteps()

    def process(self):
        if self.step >= len(self.data):
            self.step = 1
        self.vox.setData(self.data[self.step])
        self.showSteps()
        self.step += 1



    def showSteps(self):
        win.lblSteps.setText('Step: ' + str(self.step))
        win.lblSpeed.setText('World data:' + str(self.env_data[self.step:self.step+20]))
        win.lblPrediction.setText('Prediction:' + str(self.pred_data[self.step]))

    def stopTimer(self):
        self.timer.stop()
        
    def startTimer(self):
        self.timer.start(self.speed)
        
    def sloverVis(self):
        self.speed *= 1.1
        self.startTimer()
        win.lblSpeed.setText('Speed:' + str(self.speed))
    
    def stepVis(self):
        self.process()
        
    def removeCell(self):
        self.cor.remove_active_cell()
        
    def enhanceCell(self):
        self.cor.enhanceInput()
        
    def fasterVis(self):
        self.speed *= 0.9
        self.startTimer()
        win.lblSpeed.setText('Speed:' + str(self.speed))
        
    def reset(self):
        self.cor.reset()
    
    def startRecordDataFile(self):
        self.startRecordData = 1
    
    def stopRecordData(self):
        self.stopTimer()
        self.startRecordData = 0    
        self.data = [] 
        
    def selectCell(self, ind):
        self.cor.selectedCell = ind

    def save(self):
        self.ncortex.save_cortex(self.data_file)
        print 'Saved to ' + self.data_file

    def keyPressEvent(self, e):
       
        if e.key() == QtCore.Qt.Key_R:
            self.cor.reset()
        if e.key() == QtCore.Qt.Key_W:
            self.speed *= 0.9 
            self.timer.start(self.speed)
        if e.key() == QtCore.Qt.Key_S:
            self.speed *= 1.1 
            self.timer.start(self.speed)

class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        layout = QtGui.QVBoxLayout()
        self.widget.setLayout(layout)
        layout.setSpacing(10)

        self.lblSteps = QtGui.QLabel('Lifespan:    ....Today:', self)
        self.lblSpeed = QtGui.QLabel('Speed:', self)
        self.lblPrediction = QtGui.QLabel('Prediction:', self)
        #OpenGl
        self.view = MyView()
        self.view.setCameraPosition(0,150,80,0)
        layout.addWidget(self.view,20)
        layout.addWidget(self.lblSteps,1)
        layout.addWidget(self.lblSpeed,1)
        layout.addWidget(self.lblPrediction,1)

        self.createActions()
        self.createMenus()
        self.createToolbars()
        
        self.setGeometry(200, 200, 800, 400)
        self.setWindowTitle('visualization')    
        self.show()

    def createActions(self):
        self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl+X",
                statusTip="Quit Scenediagram example", triggered=self.close)
        
        self.saveAction = QtGui.QAction('&Save', self, triggered=self.view.save)
        self.runAction = QtGui.QAction('&RUN', self, triggered=self.view.startTimer)
        self.stopAction = QtGui.QAction('&STOP', self, triggered=self.view.stopTimer)
        self.fasterAction = QtGui.QAction('&Faster', self, triggered=self.view.fasterVis)
        self.sloverAction = QtGui.QAction('&Slover', self, triggered=self.view.sloverVis)
        self.stepAction = QtGui.QAction('&Step', self, triggered=self.view.stepVis)
        self.removeAction = QtGui.QAction('&RemoveCell', self, triggered=self.view.removeCell)
        self.enhanceAction = QtGui.QAction('&EnhanceCell', self, triggered=self.view.enhanceCell)
        self.resetAction = QtGui.QAction('&Reset', self, triggered=self.view.reset)
        self.startRecordDataAction = QtGui.QAction('&Start', self, triggered=self.view.startRecordDataFile)
        self.stopRecordDataAction = QtGui.QAction('&Stop', self, triggered=self.stopRecordData)
        
        self.selectCellAction = QtGui.QAction('&Select Cell', self, triggered=self.selectCell)        
        self.cellInfoAction = QtGui.QAction('&Cell info', self, triggered=self.cellInfo)        
        self.plotAction = QtGui.QAction('&Plot', self, triggered=self.plotInfo)        

        # self.SaveAction = QtGui.QAction('&Plot', self, triggered=self.view.save)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.exitAction)
    
    def createToolbars(self):
        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.runAction)
        self.editToolBar.addAction(self.stopAction)
        self.editToolBar.addAction(self.stepAction)
        self.editToolBar.addAction(self.sloverAction)
        self.editToolBar.addAction(self.fasterAction)
        self.editToolBar.addAction(self.removeAction)
        self.editToolBar.addAction(self.enhanceAction)
        
        self.optionsToolBar = self.addToolBar("Options")
        self.optionsToolBar.addAction(self.resetAction)        
        self.optionsToolBar.addWidget(QtGui.QLabel('Record data:', self))
        self.optionsToolBar.addAction(self.startRecordDataAction)
        self.optionsToolBar.addAction(self.stopRecordDataAction)
        
        self.cellsToolBar = self.addToolBar("CellInfo")
        self.cellsToolBar.addAction(self.selectCellAction)
        self.cell_lbl = QtGui.QLabel('Selected Cell: None' , self) 
        self.cellsToolBar.addWidget(self.cell_lbl)

        self.cellsToolBar = self.addToolBar("Save")
        self.cellsToolBar.addAction(self.saveAction)

    def stopRecordData(self):
        self.view.stopTimer()
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                "QFileDialog.getSaveFileName()",
                'data',
                "All Files (*)")
        if fileName:        
            np.save(str(fileName), self.view.data)
            self.view.stopRecordData()
            
    def selectCell(self):
        text, ok = QtGui.QInputDialog.getText(self, "QInputDialog.getText()",
                "Select Cell:", QtGui.QLineEdit.Normal,
                QtCore.QDir.home().dirName())
        if ok and text != '':
            self.view.selectCell(self.getIndices(text))
            self.cell_lbl.setText('Selected Cell:' + str(self.getIndices(text)))
            
            
            self.cellsToolBar.addAction(self.cellInfoAction)
            self.cellsToolBar.addAction(self.plotAction)
            
    def getIndices(self, text):
        indices = ()
        for i in list(text.split(' ')):
            indices += (int(str(i)),)
        self.selectedCell = self.view.cor.cortex[indices[0],indices[1],indices[2]]
        return indices
        
    def cellInfo(self):
        message = self.view.cor.info(self.selectedCell)
        info = QtGui.QMessageBox.information(self,
                "Cell information", message)

    def plotInfo(self):
        pass


def visualize3d(data, env_data=None, pred_data=None):
    global win
    import sys
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.view.setup(data, env_data, pred_data)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    w = World()
    for i in range(30):
        w.evolve()
    win.view.setup(w.data)
    win.show()
    sys.exit(app.exec_())