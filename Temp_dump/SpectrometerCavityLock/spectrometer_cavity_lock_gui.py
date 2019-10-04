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
	sys.path.append("D:\\\Control\\SpectrometerCavityLock")
	semilogy_scale = True
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\\SpectrometerCavityLock\\")
	semilogy_scale = False
elif gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")
	sys.path.append("D:\\Control\\SpectrometerCavityLock\\")
	semilogy_scale = False


from pbec_analysis import slice_data
import spectrometer_cavity_lock_gui
from spectrometerStabiliser import SpectrometerStabiliser
import mini_utils #replaces "hene_utils"


#Default values for stabiliser
default_set_cutoff_wavelength=569

#Parameters for graph
plot_buffer_length = 500
label_fontsize=9

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
		self.axes211.plot([0],[0],"*", markersize=3) #needed to initialised the plot
		self.axes211.set_ylabel("Control voltage (mV)",fontsize=label_fontsize)
		self.axes211.set_ylim(1000*array(self.stabiliser.control_range))
		#
		self.axes212.plot([0],[0],"o", markersize=3) #needed to initialised the plot
		self.axes212.set_xlabel("time \n(s since midnight)",fontsize=label_fontsize)
		self.axes212.set_ylabel("Cutoff wavelength (nm)",fontsize=label_fontsize)

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
		
		#subplot(2,1,1)
		###self.axes211.plot(time_numbers, float_vouts, "*", markersize=3)
		self.lin211 = self.axes211.lines[0]
		self.lin211.set_xdata(time_numbers)
		self.lin211.set_ydata(float_vouts)

		self.axes211.set_xlabel("time \n(s since midnight)")
		self.axes211.set_ylabel("Control voltage (mV)")
		self.axes211.set_ylim(1000*array(self.stabiliser.control_range)) #should reflect the stabilister control range!!!
		self.axes211.set_xlim(min(time_numbers),max(time_numbers))
		self.axes211.grid(True)
		
		#subplot(2,1,2)
		#self.axes212.plot(time_numbers, float_cutoffs, "o", markersize=3)
		self.lin212 = self.axes212.lines[0]
		self.lin212.set_xdata(time_numbers)
		self.lin212.set_ydata(float_cutoffs)
		self.axes212.set_xlabel("time \n(s since midnight)")
		self.axes212.set_ylabel("Cutoff wavelength (nm)")
		self.axes212.set_xlim(min(time_numbers),max(time_numbers))
		self.axes212.set_ylim(min(float_cutoffs),max(float_cutoffs))
		self.axes212.grid(True)
		#
		self.draw()


class EmbeddedLatestSpectrumGraph(FigureCanvas):
	#This will be used to show the most recently acquired spectrum
	def __init__(self, stabiliser,parent=None, width=4, height=4.5, dpi=100):
		self.stabiliser = stabiliser
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
		self.axes.set_xlim(*self.stabiliser.lamb_range)
		self.axes.set_xlabel("Wavelength (nm)",fontsize=label_fontsize)
		#self.lin = self.axes.lines[0] #I hope

	def update_figure(self):
		if shape(self.stabiliser.lamb)==shape(self.stabiliser.spectrum) and self.stabiliser.lamb!=[] and self.stabiliser.spectrum!=[]:
			try:
				cut = slice_data(self.stabiliser.lamb, self.stabiliser.spectrum,self.stabiliser.lamb_range)
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
		self.axes.set_title(self.stabiliser.ts)
		self.axes.set_ylabel("Spectrum value",fontsize=label_fontsize)
		self.axes.set_xlim(*self.stabiliser.lamb_range)
		self.axes.set_xlabel("Wavelength (nm)",fontsize=label_fontsize)
		#########self.axes.set_xlim(*self.stabiliser.lamb_range)
		self.axes.grid(1)
		try:
			self.draw()
		except:
			print "plotting data failed for some reason"

class ApplicationWindow(QtGui.QMainWindow):
	#This is the main window
	def __init__(self,stabiliser):
		self.stabiliser = stabiliser
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

		self.set_cutoff_wavelength=default_set_cutoff_wavelength
		self.stabiliser.set_point = default_set_cutoff_wavelength
		self.stabiliser.pic.set_point = default_set_cutoff_wavelength
		
		#Add the updating graph
		self.dc = EmbeddedUpdatingGraph(self.stabiliser, parent=self.main_widget,width=5, height=4, dpi=100)
		self.graph_hbox.addWidget(self.dc)
		
		#Add the spectrum display graph
		self.sg= EmbeddedLatestSpectrumGraph(self.stabiliser,parent=self.main_widget,width=5, height=4, dpi=100)
		self.all_graph_box.addWidget(self.sg)
		
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
		
		#---------------
		#-----Start and stop the lock, etc.---------
		#The labels on these buttons should change once they've been pushed
		self.start_stop_acquisition_button=QtGui.QPushButton("Start\nAcquisition")
		self.start_stop_lock_button=QtGui.QPushButton("Start\nLock")
		self.reset_button=QtGui.QPushButton("Reset lock;\nOutput to "+str(mean(stabiliser.control_range))+" V")
		self.save_buffer_button=QtGui.QPushButton("Save displayed\ndata") #TODO: more informative text
		self.stop_go_hbox.addWidget(self.start_stop_acquisition_button)
		self.stop_go_hbox.addWidget(self.start_stop_lock_button)
		self.stop_go_hbox.addWidget(self.reset_button)
		self.stop_go_hbox.addWidget(self.save_buffer_button)
		
		
		#----------Gain entry and display zone-------------
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
		#invoke a callback function whenever it gets a new cutoff_wavelength and set_point
		def update_cutoff_wavelength_display():
			self.currentCutoffText.display(self.stabiliser.cutoff_wavelength)
			self.setLCD.display(self.stabiliser.pic.set_point)

		timer = QtCore.QTimer(self)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), update_cutoff_wavelength_display)
		timer.start(10) #in ms. Updates once per second
		
		self.setCentralWidget(self.main_widget)

	def message(self,message="No message"):
		QtGui.QMessageBox.about(self, "MessageBox",message)
