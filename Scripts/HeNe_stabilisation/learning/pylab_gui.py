#ipython --matplotlib=qt

import sys, os, random
from PyQt4 import QtGui, QtCore

from pylab import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

default_parameter=17

class Stabiliser():
	def __init__(self):
		pass

class EmbeddedUpdatingGraph(FigureCanvas):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
		# We want the axes cleared every time plot() is called
		self.axes.hold(False)
		self.compute_initial_figure()
		#
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		timer = QtCore.QTimer(self)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		timer.start(1000) #in ms
		self.parameter=default_parameter

	def update_parameter(self,parameter):
		self.parameter = parameter

	def compute_initial_figure(self):
		self.axes.plot(rand(default_parameter), 'r')

	def update_figure(self):
		self.axes.plot(rand(self.parameter), 'r')
		self.draw()


class ApplicationWindow(QtGui.QMainWindow):
	#This is the main window
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setWindowTitle("Cavity Length Stabilisation")

		#Set some useful parameters
		self.acquisition_running = False
		self.lock_on = False

		#Layout of the main window
		self.main_widget = QtGui.QWidget(self)
		self.vbox = QtGui.QVBoxLayout(self.main_widget)
		self.graph_hbox = QtGui.QHBoxLayout()
		self.set_point_hbox = QtGui.QHBoxLayout()
		self.stop_go_hbox = QtGui.QHBoxLayout()
		self.vbox.addLayout(self.graph_hbox)
		self.vbox.addLayout(self.set_point_hbox)
		self.vbox.addLayout(self.stop_go_hbox)
		
		#Add the updating graph
		self.dc = EmbeddedUpdatingGraph(self.main_widget, width=5, height=4, dpi=100)
		self.graph_hbox.addWidget(self.dc)
		
		#-----Set point entry and display---------
		self.setLCD = QtGui.QLCDNumber()
		self.setLCD.display(default_parameter)
		self.setText = QtGui.QLineEdit()
		self.set_point_hbox.addWidget(QtGui.QLabel("Ring radius set point: "))
		self.set_point_hbox.addWidget(self.setText)
		self.set_point_hbox.addWidget(QtGui.QLabel("Current set value: "))
		self.set_point_hbox.addWidget(self.setLCD)
		#---------------
		#-----Start and stop the lock, etc.---------
		#The labels on these buttons should change once they've been pushed
		self.start_stop_acquisition_button=QtGui.QPushButton("Start\nAcquisition")
		self.start_stop_lock_button=QtGui.QPushButton("Start\nLock")
		self.stop_go_hbox.addWidget(self.start_stop_acquisition_button)
		self.stop_go_hbox.addWidget(self.start_stop_lock_button)
		
		#self.main_widget.setFocus()
		self.setCentralWidget(self.main_widget)

		#self.statusBar().showMessage("Initial status message", 2000)

	def fileQuit(self):
		self.close()

	def closeEvent(self, ce):
		self.fileQuit()

	def message(self,message="No message"):
		QtGui.QMessageBox.about(self, "MessageBox",message)

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()

def setValueChangedByText():
    try:
		newValue = int(aw.setText.text())
    except:
		pass
    else:
		aw.setLCD.display(newValue)
		aw.dc.update_parameter(newValue)
		#Now also update the "parameter" of the MyDynamicMplCanvas
	#
aw.setText.returnPressed.connect(setValueChangedByText)

def start_stop_acquisition_button_pushed():
	aw.acquisition_running=not(aw.acquisition_running)
	if aw.acquisition_running:
		aw.start_stop_acquisition_button.setText("Stop\nAcquisition")
		#Now do the things you need to do
	else:
		aw.start_stop_acquisition_button.setText("Start\nAcquisition")
		#Now do the things you need to do
	aw.start_stop_acquisition_button.update()

aw.start_stop_acquisition_button.pressed.connect(start_stop_acquisition_button_pushed)

def start_stop_lock_button_pushed():
	aw.lock_on=not(aw.lock_on)
	if aw.lock_on:
		aw.start_stop_lock_button.setText("Stop\nLock")
		#Now do the things you need to do
	else:
		aw.start_stop_lock_button.setText("Start\nLock")
		#Now do the things you need to do
	aw.start_stop_lock_button.update()

aw.start_stop_lock_button.pressed.connect(start_stop_lock_button_pushed)


aw.show()
sys.exit(qApp.exec_())