#ipython --matplotlib=qt

import sys, os, random
from PyQt4 import QtGui, QtCore

from pylab import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from socket import gethostname

#Computer dependent paths
from socket import gethostname
if gethostname()=="ph-rnyman-01":
	sys.path.append("D:\\Control\\PythonPackages\\")
	sys.path.append("D:\\\Control\\Multispec_server")
	semilogy_scale = True
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\\Multispec_server\\")
	semilogy_scale = False
elif gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")
	sys.path.append("D:\\Control\\Multispec_server\\")
	semilogy_scale = False


from pbec_analysis import slice_data
import multi_spectrometers_gui
from spectrometer_reader import Spectrometers

#Parameters for graph
plot_buffer_length = 500
label_fontsize=9
'''
class EmbeddedUpdatingGraph(FigureCanvas):
	def __init__(self, stabiliser,parent=None, width=4, height=4.5, dpi=100):
		self.stabiliser = stabiliser
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes211 = fig.add_subplot(2,1,1)
		self.axes212 = fig.add_subplot(2,1,2)
		fig.subplots_adjust(bottom=0.15,left=0.25,top=0.95,right=0.95)
		# We want the axes cleared every time plot() is called
		self.axes211.hold(False)
		self.axes212.hold(False)
		#
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		timer = QtCore.QTimer(self)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		timer.start(20) #in ms


	def update_figure(self):
		res = self.stabiliser.results
		if len(res)>plot_buffer_length:
			results = res[-plot_buffer_length:]
		else:
			results = res
			
		time_numbers = [mini_utils.time_number_from_timestamp(r["ts"]) for r in results]
		float_vouts =  [1e3*float(r["Vout"]) for r in results]
		float_cutoffs = [float(r["cutoff_wavelength"]) for r in results]
		
		if not len(time_numbers) == len(float_vouts) == len(float_cutoffs):
			#race condition with reading the data from stabiliser
			return
		
		#
		self.draw()
'''

class EmbeddedLatestSpectrumGraph(FigureCanvas):
	#This will be used to show the most recently acquired spectrum
	def __init__(self, spectrometers,parent=None, width=4, height=4.5, dpi=100):
		self.spectrometers = spectrometers
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = self.fig.add_subplot(1,1,1)
		self.fig.subplots_adjust(bottom=0.15,left=0.20,top=0.9,right=0.95)
		self.axes.hold(False)
		
		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.compute_initial_figure()
		
		timer = QtCore.QTimer(self)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		timer.start(20) #in ms

	def compute_initial_figure(self):
		self.axes.plot([1],[1]) #needed to initialised the plot
		if semilogy_scale:
			self.axes.set_yscale("log")
		self.axes.set_ylabel("Spectrum value",fontsize=label_fontsize)
		self.axes.set_ylim(0,)
		self.axes.set_xlim(*self.spectrometers.lamb_range)
		self.axes.set_xlabel("Wavelength (nm)",fontsize=label_fontsize)
		#self.lin = self.axes.lines[0] #I hope

	def update_figure(self):
		if shape(self.spectrometers.spectros[0].lamb)==shape(self.spectrometers.spectros[0].spectrum) and self.spectrometers.spectros[0].lamb!=[] and self.spectrometers.spectros[0].spectrum!=[]:
			try:
				for spec in self.spectrometers.spectros:
					cut = slice_data(spec.lamb, spec.spectrum,self.spectrometers.lamb_range)
					cutlamb, cutspec = cut[0], cut[1]
					#cutlamb, cutspec = self.stabiliser.lamb, self.stabiliser.spectrum
					#self.axes.plot(cutlamb,cutspec)
					self.lin = self.axes.lines[0]
					self.lin.set_xdata(cutlamb)
					self.lin.set_ydata(cutspec)
					#Now manually set xlim and ylim
					self.axes.set_ylim(min(cutspec),max(cutspec)) #better to round things a bit...
			except:
				print "plotting failure"
		self.axes.set_title(self.spectrometers.ts)
		self.axes.set_ylabel("Spectrum value",fontsize=label_fontsize)
		self.axes.set_xlim(*self.spectrometers.lamb_range)
		self.axes.set_xlabel("Wavelength (nm)",fontsize=label_fontsize)
		#########self.axes.set_xlim(*self.stabiliser.lamb_range)
		self.axes.grid(1)
		try:
			self.draw()
		except:
			print "plotting data failed for some reason"

class ApplicationWindow(QtGui.QMainWindow):
	#This is the main window
	def __init__(self,spectrometers):
		self.spectrometers = spectrometers
		QtGui.QMainWindow.__init__(self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setWindowTitle("Spectrometer Cavity Length Stabilisation")
		self.setGeometry(QtCore.QRect(920, 40, 600, 500))
		#Set some useful parameters
		self.acquisition_running = False
		self.lock_on = False
		#Layout of the main window
		self.main_widget = QtGui.QWidget(self)
		self.vbox = QtGui.QVBoxLayout(self.main_widget)
		self.graph_hbox = QtGui.QHBoxLayout()
		self.controls_hbox = QtGui.QHBoxLayout()
		self.all_graph_box = QtGui.QHBoxLayout()
		self.vbox.addLayout(self.graph_hbox)
		self.graph_hbox.addLayout(self.all_graph_box)
		self.vbox.addLayout(self.controls_hbox)
		#
		self.misc_controls_vbox = QtGui.QVBoxLayout()
		self.pi_controls_vbox=QtGui.QVBoxLayout()
		self.controls_hbox.addLayout(self.misc_controls_vbox)
		self.controls_hbox.addLayout(self.pi_controls_vbox)
		#
		self.set_point_hbox = QtGui.QHBoxLayout()
		self.stop_go_hbox = QtGui.QHBoxLayout()
		
		self.misc_controls_vbox.addLayout(self.set_point_hbox)
		self.misc_controls_vbox.addLayout(self.stop_go_hbox)

		
		#Add the updating graph
		#self.dc = EmbeddedUpdatingGraph(self.stabiliser, parent=self.main_widget,width=5, height=4, dpi=100)
		#self.graph_hbox.addWidget(self.dc)
		
		#Add the spectrum display graph
		self.sg= EmbeddedLatestSpectrumGraph(self.spectrometers,parent=self.main_widget,width=5, height=4, dpi=100)
		self.all_graph_box.addWidget(self.sg)
		
		'''
		#-----Set point entry, display and current value display---------
		self.setLCD = QtGui.QLCDNumber()
		self.setLCD.display(default_set_cutoff_wavelength)
		self.setText = QtGui.QLineEdit() #JM: such a bad name
		self.currentCutoffText=QtGui.QLCDNumber()
		self.set_point_hbox.addWidget(QtGui.QLabel("Cutoff wavelength (nm)\nset point: "))
		self.set_point_hbox.addWidget(self.setText)
		self.set_point_hbox.addWidget(QtGui.QLabel("Set value: "))
		self.set_point_hbox.addWidget(self.setLCD)
		self.set_point_hbox.addWidget(QtGui.QLabel("Current cutoff wavelength (nm)"))
		self.set_point_hbox.addWidget(self.currentCutoffText)
		'''
		#---------------
		#-----Start and stop the lock, etc.---------
		#The labels on these buttons should change once they've been pushed
		self.start_stop_acquisition_button=QtGui.QPushButton("Start\nAcquisition")
		self.start_stop_lock_button=QtGui.QPushButton("Start\nLock")
		self.save_buffer_button=QtGui.QPushButton("Save displayed\ndata") #TODO: more informative text
		self.stop_go_hbox.addWidget(self.start_stop_acquisition_button)
		self.stop_go_hbox.addWidget(self.start_stop_lock_button)
		self.stop_go_hbox.addWidget(self.save_buffer_button)
		
		
		#TODO jakov: probably a much better way would be to have the thread in stabiliser_class
		#invoke a callback function whenever it gets a new cutoff_wavelength and set_point

		timer = QtCore.QTimer(self)
		timer.start(10) #in ms. Updates once per second
		
		self.setCentralWidget(self.main_widget)

	def message(self,message="No message"):
		QtGui.QMessageBox.about(self, "MessageBox",message)
