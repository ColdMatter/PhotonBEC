#ipython --matplotlib=qt

import sys, os, random
from PyQt4 import QtGui, QtCore

from pylab import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from socket import gethostname
from time import sleep
from scipy.optimize import curve_fit
import socket


if socket.gethostname() == 'ph-photonbec3':
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\CavityLock")
else:
	raise Exception("Unknown machine")

import hene_utils

#Default values for stabiliser
default_set_ring_rad=0

#Parameters for graph
plot_buffer_length = 1000
label_fontsize=9


########## Plots in the main app window
class EmbeddedUpdatingGraph(FigureCanvas): 
	def __init__(self, stabiliser,parent=None, width=4, height=4.5, dpi=100):
		self.stabiliser = stabiliser
		self.second_fig_y_axis = 'PCA Projections'
		self.cavity_length_plot = False
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes211 = fig.add_subplot(2,1,1)
		self.axes212 = fig.add_subplot(2,1,2)
		fig.subplots_adjust(bottom=0.15,left=0.15,top=0.95,right=0.95)
		# We want the axes cleared every time plot() is called
		self.axes211.hold(False)
		self.axes212.hold(False)
		self.compute_initial_figure()
		#
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		timer = QtCore.QTimer(self)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		timer.start(20) #in ms

	def compute_initial_figure(self):
		#self.axes211.set_xlabel("time (s since midnight)",fontsize=label_fontsize)
		self.axes211.set_ylabel("Control voltage (mV)",fontsize=label_fontsize)
		self.axes211.set_ylim(1000*array(self.stabiliser.control_range))
		#
		self.axes212.set_xlabel("time (s since midnight)",fontsize=label_fontsize)
		self.axes212.set_ylabel("PCA Projection",fontsize=label_fontsize)

	def update_figure(self):
		res = self.stabiliser.results
		if len(res)>plot_buffer_length:
			results = res[-plot_buffer_length:]
		else:
			results = res
			
		time_numbers = [hene_utils.time_number_from_timestamp(r["ts"]) for r in results]
		float_vouts =  [1e3*float(r["Vout"]) for r in results]
		float_ring_rads = [float(r["ring_rad"]) for r in results]
		if self.cavity_length_plot is True:
			phase_shift = np.arccos((float_ring_rads-self.tranfer_parameterA) / self.tranfer_parameterB) - np.pi/2
			cavity_shift = phase_shift * self.stabiliser.led_lambda / (4*np.pi)
			float_ring_rads = 1.0*cavity_shift
			
		if not len(time_numbers) == len(float_vouts) == len(float_ring_rads):
			#race condition with reading the data from stabiliser
			return
		
		#subplot(2,1,1)
		self.axes211.plot(time_numbers, float_vouts, "*", markersize=3)
		self.axes211.set_xlabel("time (s since midnight)")
		self.axes211.set_ylabel("Control voltage (mV)")
		#self.axes211.set_ylim(1000*array(self.stabiliser.control_range)) #should reflect the stabilister control range!!!
		try:
			self.axes211.set_ylim(min(float_vouts),max(float_vouts)) #should reflect the stabilister control range!!!
		except:
			self.axes211.set_ylim(0,1)
		self.axes211.grid(True)
		
		#subplot(2,1,2)
		self.axes212.plot(time_numbers, float_ring_rads, "o", markersize=3)
		self.axes212.set_xlabel("time (s since midnight)")
		self.axes212.set_ylabel(self.second_fig_y_axis)
		self.axes212.grid(True)
		#
		self.draw()


########## Aux canvas displaying camera
class DisplayCameraImageCanvas(FigureCanvas):

	def __init__(self,parent=None,width=5, height=4, dpi=100):
		self.parent=parent
		self.stabiliser = parent.parent.stabiliser
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		FigureCanvas.__init__(self, self.fig)
		self.axes = self.fig.add_subplot(111)
		# We want the axes cleared every time plot() is called
		self.axes.hold(False)
		#
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		#Now, display some data
		self.im_raw = self.stabiliser.im_raw #parent is aw.popup, aw.popup.parent is aw, aw.stabiliser is stabiliser object
		
		self.axesImage = self.axes.axes.imshow(self.im_raw[:,:,self.stabiliser.channel],cmap=cm.gray)#,colorbar()
		cb = self.fig.colorbar(self.axesImage)


class CheckCentreWindow(QtGui.QWidget):
	#Inteded to pop up when a button is pressed, and house a graph
	def __init__(self,parent=None):
		self.parent=parent
		QtGui.QWidget.__init__(self)
		self.setGeometry(QtCore.QRect(100, 100, 500, 400))
		self.vbox = QtGui.QVBoxLayout(self)
		self.setup()
		
	def setup(self):
		self.setWindowTitle("Cavity Length Stabilisation: check interference fringes")
		self.graph = DisplayCameraImageCanvas(parent = self)
		self.vbox.addWidget(self.graph)
		#Takes most recent data set, currently in the stabiliser thread, and display it



########## Aux canvas displaying fringes
class DisplayFringesImageCanvas(FigureCanvas):

	def __init__(self,parent=None,width=5, height=4, dpi=100):
		self.parent=parent
		self.stabiliser = parent.parent.stabiliser
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		FigureCanvas.__init__(self, self.fig)
		self.axes = self.fig.add_subplot(111)
		# We want the axes cleared every time plot() is called
		self.axes.hold(True)
		#
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		#Now, display some data
		trial_voltages = self.stabiliser.trial_voltages 
		projections = self.stabiliser.projections

		### Fits interference fringes
		def fit_func(x, a, b, c, d):
			return a+b*np.cos(c*x+d)
		p0 = [0, 100, np.pi/(trial_voltages[-1]-trial_voltages[0]), 0]
		pmin = [-20, -150, -np.pi/(trial_voltages[-1]-trial_voltages[0]), 0]
		pmax = [20, 150, np.pi/(trial_voltages[-1]-trial_voltages[0]), 2*np.pi]
		popt, pcov = curve_fit(fit_func, trial_voltages, projections, maxfev=10000, p0=p0, bounds=([pmin, pmax]))
		x_fit = np.linspace(trial_voltages[0], trial_voltages[-1], 100)
		y_fit = fit_func(x_fit, popt[0], popt[1], popt[2], popt[3])
		phase_shift = np.round(np.abs(popt[2])*(trial_voltages[-1]-trial_voltages[0]), 2)

		if parent.parent.dc.cavity_length_plot is True:
			parent.parent.dc.cavity_length_plot = False
			parent.parent.dc.second_fig_y_axis = 'PCA Projections'
		else:
			parent.parent.dc.cavity_length_plot = True
			parent.parent.dc.second_fig_y_axis = 'Cavity length shift (nm)'
			parent.parent.dc.tranfer_parameterA = popt[0]
			parent.parent.dc.tranfer_parameterB = popt[1]

		self.axesImage = self.axes.axes.plot(trial_voltages, projections, label='PCA Projections')
		self.axesImage = self.axes.axes.plot(x_fit, y_fit, label='Cosine fit')
		self.axesImage = self.axes.axes.legend()
		self.axesImage = self.axes.axes.text(trial_voltages[0], 0, 'Spanned phase shift is {0} rad'.format(phase_shift))
		self.axesImage = self.axes.axes.set_xlabel('DAC Piezo Voltage')
		self.axesImage = self.axes.axes.set_ylabel('PCA Projection')

		

class SetCentreWindow(QtGui.QWidget):
	#Inteded to pop up when a button is pressed, and house a graph
	def __init__(self,parent=None):
		self.parent=parent
		QtGui.QWidget.__init__(self)
		self.setGeometry(QtCore.QRect(100, 100, 500, 400))
		self.vbox = QtGui.QVBoxLayout(self)
		self.setup()
		
	def setup(self):
		self.setWindowTitle("Cavity Length Stabilisation: check interference fringes")
		self.graph = DisplayFringesImageCanvas(parent = self)
		self.vbox.addWidget(self.graph)
		#Takes most recent data set, currently in the stabiliser thread, and display it



class ApplicationWindow(QtGui.QMainWindow):
	#This is the main window
	def __init__(self,stabiliser):
		self.stabiliser = stabiliser
		QtGui.QMainWindow.__init__(self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setWindowTitle("Cavity Length Stabilisation")
		self.setGeometry(QtCore.QRect(500, 300, 600, 500))
		#Set some useful parameters
		self.acquisition_running = False
		self.lock_on = False

		#Layout of the main window
		self.main_widget = QtGui.QWidget(self)
		self.vbox = QtGui.QVBoxLayout(self.main_widget)
		self.graph_hbox = QtGui.QHBoxLayout()
		self.controls_hbox = QtGui.QHBoxLayout()
		self.vbox.addLayout(self.graph_hbox)
		self.vbox.addLayout(self.controls_hbox)
		#
		self.misc_controls_vbox = QtGui.QVBoxLayout()
		self.pi_controls_vbox=QtGui.QVBoxLayout()
		self.controls_hbox.addLayout(self.misc_controls_vbox)
		self.controls_hbox.addLayout(self.pi_controls_vbox)
		#
		self.set_point_hbox = QtGui.QHBoxLayout()
		self.stop_go_hbox = QtGui.QHBoxLayout()
		self.centre_check_hbox = QtGui.QHBoxLayout()
		
		self.misc_controls_vbox.addLayout(self.set_point_hbox)
		self.misc_controls_vbox.addLayout(self.stop_go_hbox)
		self.misc_controls_vbox.addLayout(self.centre_check_hbox)

		self.set_ring_rad=default_set_ring_rad
		self.stabiliser.set_point = default_set_ring_rad
		self.stabiliser.pic.set_point = default_set_ring_rad
		
		#Add the updating graph
		self.dc = EmbeddedUpdatingGraph(self.stabiliser, parent=self.main_widget,width=5, height=4, dpi=100)
		self.graph_hbox.addWidget(self.dc)
		
		#-----Set point entry, display and current value display---------
		self.setLCD = QtGui.QLCDNumber()
		self.setLCD.display(default_set_ring_rad)
		self.setText = QtGui.QLineEdit() #JM: such a bad name
		self.currentRadiusText=QtGui.QLCDNumber()
		self.set_point_hbox.addWidget(QtGui.QLabel("Projection\nset point: "))
		self.set_point_hbox.addWidget(self.setText)
		self.set_point_hbox.addWidget(QtGui.QLabel("Set value: "))
		self.set_point_hbox.addWidget(self.setLCD)
		self.set_point_hbox.addWidget(QtGui.QLabel("Current projection value"))
		self.set_point_hbox.addWidget(self.currentRadiusText)
		
		#---------------
		#-----Start and stop the lock, etc.---------
		#The labels on these buttons should change once they've been pushed
		self.start_stop_acquisition_button=QtGui.QPushButton("Start\nAcquisition")
		self.start_stop_lock_button=QtGui.QPushButton("Start\nLock")
		self.reset_button=QtGui.QPushButton("Reset lock;\nOutput to "+str(mean(stabiliser.control_range))+" V")
		self.stop_go_hbox.addWidget(self.start_stop_acquisition_button)
		self.stop_go_hbox.addWidget(self.start_stop_lock_button)
		self.stop_go_hbox.addWidget(self.reset_button)
		
		#Check if centre is well placed
		self.save_buffer_button=QtGui.QPushButton("Save displayed\ndata") #TODO: more informative text
		self.centre_check_hbox.addWidget(self.save_buffer_button, stretch=2)
		self.check_centre_button=QtGui.QPushButton("Check fringes")
		self.check_centre_button.setEnabled(False)
		self.centre_check_hbox.addWidget(self.check_centre_button, stretch=2)
		self.set_centre_button=QtGui.QPushButton("Check projections")
		self.set_centre_button.setEnabled(False)
		self.centre_check_hbox.addWidget(self.set_centre_button, stretch=2)
		#self.currentCentreText=QtGui.QLabel("Centre: ")
		#self.centre_check_hbox.addWidget(self.currentCentreText, stretch=1)
		
		#----------Gain entry and display zone-------------
		#self.gains_hbox = QtGui.QHBoxLayout()
		#self.const_hbox = QtGui.QHBoxLayout()
		#self.pi_controls_vbox.addLayout(self.gains_hbox)
		#self.pi_controls_vbox.addLayout(self.const_hbox)

		self.set_Pgain = QtGui.QLineEdit()
		self.Pgain_text = QtGui.QLabel()
		self.Pgain_text.setText(str(self.stabiliser.pic.P_gain)) #initialise to value in stabiliser.pic.P_gain
		self.set_Igain = QtGui.QLineEdit()
		self.Igain_text = QtGui.QLabel()
		self.Igain_text.setText(str(self.stabiliser.pic.I_gain)) #initialise to value in stabiliser.pic.P_gain
		self.set_IIgain = QtGui.QLineEdit()
		self.IIgain_text = QtGui.QLabel()
		self.IIgain_text.setText(str(self.stabiliser.pic.II_gain)) #initialise to value in stabiliser.pic.P_gain
		
		self.set_Iconst = QtGui.QLineEdit()
		self.Iconst_text = QtGui.QLabel()
		self.Iconst_text.setText(str(self.stabiliser.pic.I_const)) #initialise to value in stabiliser.pic.P_gain
		self.set_IIconst = QtGui.QLineEdit()
		self.IIconst_text = QtGui.QLabel()
		self.IIconst_text.setText(str(self.stabiliser.pic.II_const)) #initialise to value in stabiliser.pic.P_gain

		lab = QtGui.QLabel("Feedback Gains")
		lab.setFont(QtGui.QFont("MS Sans Serif",12,QtGui.QFont.Bold))
		self.pi_controls_vbox.addWidget(lab)
		
		self.pi_controls_label_hbox  = QtGui.QHBoxLayout()
		self.pi_controls_vbox.addLayout(self.pi_controls_label_hbox)
		self.pi_controls_label_titles_hbox  = QtGui.QHBoxLayout()
		self.pi_controls_vbox.addLayout(self.pi_controls_label_titles_hbox)
		self.pi_controls_label_hbox.addWidget(QtGui.QLabel("Parameter"),stretch=1)
		self.pi_controls_label_hbox.addWidget(QtGui.QLabel("Set"),stretch=1)
		self.pi_controls_label_hbox.addWidget(QtGui.QLabel("Current"),stretch=1)
		
		self.Pgain_hbox  = QtGui.QHBoxLayout()
		self.pi_controls_vbox.addLayout(self.Pgain_hbox)
		self.Pgain_hbox.addWidget(QtGui.QLabel("P: "),stretch=1)
		self.Pgain_hbox.addWidget(self.set_Pgain,stretch=1)
		self.Pgain_hbox.addWidget(self.Pgain_text,stretch=1)
		
		self.Igain_hbox  = QtGui.QHBoxLayout()
		self.pi_controls_vbox.addLayout(self.Igain_hbox,stretch=1)
		self.Igain_hbox.addWidget(QtGui.QLabel("I: "),stretch=1)
		self.Igain_hbox.addWidget(self.set_Igain,stretch=1)
		self.Igain_hbox.addWidget(self.Igain_text,stretch=1)
		
		self.IIgain_hbox  = QtGui.QHBoxLayout()
		self.pi_controls_vbox.addLayout(self.IIgain_hbox)
		self.IIgain_hbox.addWidget(QtGui.QLabel("II: "),stretch=1)
		self.IIgain_hbox.addWidget(self.set_IIgain,stretch=1)
		self.IIgain_hbox.addWidget(self.IIgain_text,stretch=1)
		
		self.Iconst_hbox  = QtGui.QHBoxLayout()
		self.pi_controls_vbox.addLayout(self.Iconst_hbox)
		self.Iconst_hbox.addWidget(QtGui.QLabel("I time: "),stretch=1)
		self.Iconst_hbox.addWidget(self.set_Iconst,stretch=1)
		self.Iconst_hbox.addWidget(self.Iconst_text,stretch=1)
		
		self.IIconst_hbox  = QtGui.QHBoxLayout()
		self.pi_controls_vbox.addLayout(self.IIconst_hbox)
		self.IIconst_hbox.addWidget(QtGui.QLabel("II time: "),stretch=1)
		self.IIconst_hbox.addWidget(self.set_IIconst,stretch=1)
		self.IIconst_hbox.addWidget(self.IIconst_text,stretch=1)
		
		#TODO jakov: probably a much better way would be to have the thread in stabiliser_class
		# invoke a callback function whenever it gets a new ring_rad and set_point
		def update_ring_radius_display():
			self.currentRadiusText.display(self.stabiliser.ring_rad)
			self.setLCD.display(self.stabiliser.pic.set_point)
		#def update_centre_display():
		#	#centre = (self.stabiliser.x0_est,self.stabiliser.y0_est)
		#	self.currentCentreText.setText("Centre: (Nan)")

		timer = QtCore.QTimer(self)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), update_ring_radius_display)
		#QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), update_centre_display)
		timer.start(0.2) #in ms. Updates once per second
		
		self.setCentralWidget(self.main_widget)

		#self.statusBar().showMessage("Initial status message", 2000)
		#self.check_centre_window = CheckCentreWindow(parent=self)

	def message(self,message="No message"):
		QtGui.QMessageBox.about(self, "MessageBox",message)
	
	def popup_check_centre_window(self):
		self.check_centre_window = CheckCentreWindow(parent=self)
		self.check_centre_window.show()
		
	def popup_set_centre_window(self):
		self.set_centre_window = SetCentreWindow(parent=self)
		self.set_centre_window.show()

