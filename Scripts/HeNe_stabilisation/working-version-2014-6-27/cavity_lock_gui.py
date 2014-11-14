#ipython --matplotlib=qt

import sys, os, random
from PyQt4 import QtGui, QtCore

from pylab import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from hene_utils import time_number_from_timestamp

default_parameter=170 #ring_radius!!! to be renamed

class EmbeddedUpdatingGraph(FigureCanvas):
	def __init__(self, stabiliser,parent=None, width=5, height=4, dpi=100):
		self.stabiliser = stabiliser
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
		self.parameter=default_parameter #stolen from main.py: to be corrected!!!

	def update_parameter(self,parameter):
		self.parameter = parameter

	def compute_initial_figure(self):
		self.axes.plot(rand(default_parameter), 'r')
		self.axes.set_xlabel("time (s since midnight)")
		self.axes.set_ylabel("Control voltage (mV)")
		self.axes.set_ylim(1000*array(self.stabiliser.control_range)) #should reflect the stabilister control range!!!

	def update_figure(self):
		res = self.stabiliser.results
		if len(res)>500:
			results = res[-500:]
		else:
			results = res
		#self.axes.plot(rand(self.parameter), 'r')
		#subplot(2,1,1)
		self.axes.plot([time_number_from_timestamp(r["ts"]) for r in results],[1e3*float(r["Vout"]) for r in results],"*")
		self.axes.set_xlabel("time (s since midnight)")
		self.axes.set_ylabel("Control voltage (mV)")
		self.axes.set_ylim(1000*array(self.stabiliser.control_range)) #should reflect the stabilister control range!!!
		self.axes.grid(True)
		#subplot(2,1,2)
		#plot([time_number_from_timestamp(r["ts"]) for r in res],[int(r["ring_rad"]) for r in res])
		#xlabel("time (s since midnight)")
		#ylabel("Ring radius (px)")
		self.draw()


class ApplicationWindow(QtGui.QMainWindow):
	#This is the main window
	def __init__(self,stabiliser):
		self.stabiliser = stabiliser
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
		self.dc = EmbeddedUpdatingGraph(self.stabiliser, parent=self.main_widget,width=5, height=4, dpi=100)
		self.graph_hbox.addWidget(self.dc)
		
		#-----Set point entry, display and current value display---------
		self.setLCD = QtGui.QLCDNumber()
		self.setLCD.display(default_parameter)
		self.setText = QtGui.QLineEdit()
		self.currentRadiusText=QtGui.QLCDNumber()
		self.set_point_hbox.addWidget(QtGui.QLabel("Ring radius set point: "))
		self.set_point_hbox.addWidget(self.setText)
		self.set_point_hbox.addWidget(QtGui.QLabel("Current set value: "))
		self.set_point_hbox.addWidget(self.setLCD)
		self.set_point_hbox.addWidget(QtGui.QLabel("Current ring radius"))
		self.set_point_hbox.addWidget(self.currentRadiusText)
		#--
		def update_ring_radius_display():
			self.currentRadiusText.display(self.stabiliser.ring_rad)#not really available!!
		#
		timer = QtCore.QTimer(self)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), update_ring_radius_display)
		timer.start(1000) #in ms. Updates once per second
		self.parameter=default_parameter
		#--
		
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

