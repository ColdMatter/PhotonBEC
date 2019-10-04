#ipython --matplotlib=qt

import sys, os, random
from PyQt4 import QtGui, QtCore

from pylab import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from socket import gethostname
from time import sleep

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
from multispec_runner import MultiSpectrometers

#Parameters for graph
plot_buffer_length = 500
label_fontsize=9
j=0

class EmbeddedLatestSpectrumGraph(FigureCanvas):
	#This will be used to show the most recently acquired spectrum
	def __init__(self, spectrometers,parent=None, width=4, height=4.5, dpi=100):
		self.counter = 0
		self.spectrometers = spectrometers
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		self.plots = []
		self.xmins, self.xmaxs, self.ymins, self.ymaxs = [], [], [], []
		self.update_paused = True
		self.thread_paused_override = self.spectrometers.thread.paused
		self.logscale = [semilogy_scale, semilogy_scale, semilogy_scale]
		for i in range(self.spectrometers.num_spectrometers):
			print i
			self.plots.append(self.fig.add_subplot(self.spectrometers.num_spectrometers,1,i+1))
			self.xmins.append(560)
			self.xmaxs.append(600)
			self.ymins.append(0.1)
			self.ymaxs.append(500)
		self.fig.subplots_adjust(bottom=0.15,left=0.20,top=0.9,right=0.95)
		for	axes in self.plots:
			axes.hold(False)
		
		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.compute_initial_figure()
		
		self.timer = QtCore.QTimer(self)
		QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		self.timer.start(1) #in ms

	def compute_initial_figure(self):
		for i,axes in enumerate(self.plots):
			axes.plot([1,2],[1,2])
			if self.logscale[i]:
				axes.set_yscale("log")
			axes.set_ylabel("Spectrum value",fontsize=label_fontsize)
			axes.set_ylim(self.ymins[i],self.ymaxs[i])
			axes.set_xlim(self.xmins[i],self.xmaxs[i])
			axes.set_ylabel("Spectrum value",fontsize=label_fontsize)
			axes.grid(1)
		self.plots[0].set_title("Timestamp will go here")
		self.plots[-1].set_xlabel("Wavelength (nm)",fontsize=label_fontsize)
		self.draw()
			
		#self.lin = self.axes.lines[0] #I hope

	def update_figure(self):
		#print "Updating figure: ", self.counter
		self.counter+=1
		if shape(self.spectrometers.spectros[0].lamb)==shape(self.spectrometers.spectros[0].spectrum) and self.spectrometers.spectros[0].lamb!=[] and self.spectrometers.spectros[0].spectrum!=[]:
			try:
				self.thread_paused_override = self.spectrometers.thread.paused
				if self.update_paused == False:
					#Python's threading is an issue here: pause acquisition during display update
					self.spectrometers.thread.paused=True
					for i,axes in enumerate(self.plots):
						spectro = self.spectrometers.spectros[i]
						cut = slice_data(spectro.lamb, spectro.spectrum, (self.xmins[i],self.xmaxs[i]))
						cutlamb, cutspec = cut[0], cut[1]
						self.lin = axes.lines[0]
						self.lin.set_xdata(cutlamb)
						self.lin.set_ydata(cutspec)
						if i==0:
							axes.set_title(self.spectrometers.ts)
						
						axes.draw_artist(axes.patch)
						axes.draw_artist(self.lin)
						self.update()
						self.flush_events()
					self.spectrometers.thread.paused=self.thread_paused_override
				else:
					print "Have skipped updating"
					sleep(1e-1)
					
			except:
				print "plotting failure"
				#self.spectrometers.thread.paused = is_thread_paused
		self.plots[0].set_title(self.spectrometers.ts)
		self.plots[-1].set_xlabel("Wavelength (nm)",fontsize=label_fontsize)

		
class ApplicationWindow(QtGui.QMainWindow):
	#This is the main window
	def __init__(self,spectrometers):
		print "Starting App window"
		self.spectrometers = spectrometers
		QtGui.QMainWindow.__init__(self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setWindowTitle("Multi Spectrometer Server interface")
		self.setGeometry(QtCore.QRect(950, 540, 600, 500))
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
		print "Checkpoint"
		self.set_point_hbox = QtGui.QHBoxLayout()
		self.stop_go_hbox = QtGui.QHBoxLayout()
		
		self.vbox.addLayout(self.stop_go_hbox)
		
		self.spec_controls_hbox = QtGui.QHBoxLayout()
		self.graph_hbox.addLayout(self.spec_controls_hbox)
		
		
		
		#Add the updating graph
		#self.dc = EmbeddedUpdatingGraph(self.stabiliser, parent=self.main_widget,width=5, height=4, dpi=100)
		#self.graph_hbox.addWidget(self.dc)
		
		#Add the spectrum display graph
		print "Starting graph bit"
		self.sg= EmbeddedLatestSpectrumGraph(self.spectrometers,parent=self.main_widget,width=5, height=4, dpi=100)
		self.all_graph_box.addWidget(self.sg)
		print "hello"
		
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
		#-----Change integration times---------
		self.spec_settings_vbox = QtGui.QVBoxLayout()
		self.spec_controls_hbox.addLayout(self.spec_settings_vbox)
		self.int_times = []
		self.n_averages = []
		for i in range(self.spectrometers.num_spectrometers):
			print i
			self.int_times.append(QtGui.QLineEdit())
			self.spec_settings_vbox.addWidget(QtGui.QLabel("Int time: "))
			self.spec_settings_vbox.addWidget(self.int_times[i])
			self.n_averages.append(QtGui.QLineEdit())
			self.spec_settings_vbox.addWidget(QtGui.QLabel("n averages: "))
			self.spec_settings_vbox.addWidget(self.n_averages[i])
			
		#-----Change graph limits---------
		self.spec_lims_hbox = QtGui.QHBoxLayout()
		self.spec_controls_hbox.addLayout(self.spec_lims_hbox)
		self.spec_xlims_vbox = QtGui.QVBoxLayout()
		self.spec_ylims_vbox = QtGui.QVBoxLayout()
		self.spec_log_vbox = QtGui.QVBoxLayout()
		self.spec_lims_hbox.addLayout(self.spec_xlims_vbox)
		self.spec_lims_hbox.addLayout(self.spec_ylims_vbox)
		self.spec_lims_hbox.addLayout(self.spec_log_vbox)
		self.xmins, self.xmaxs, self.ymins, self.ymaxs, self.logs = [], [], [], [], []
		for i in range(self.spectrometers.num_spectrometers):
			self.xmins.append(QtGui.QLineEdit())
			self.xmaxs.append(QtGui.QLineEdit())
			self.ymins.append(QtGui.QLineEdit())
			self.ymaxs.append(QtGui.QLineEdit())
			self.logs.append(QtGui.QCheckBox())
			self.spec_xlims_vbox.addWidget(QtGui.QLabel("xmin: "))
			self.spec_xlims_vbox.addWidget(self.xmins[i])
			self.spec_xlims_vbox.addWidget(QtGui.QLabel("xmax: "))
			self.spec_xlims_vbox.addWidget(self.xmaxs[i])
			self.spec_ylims_vbox.addWidget(QtGui.QLabel("ymin: "))
			self.spec_ylims_vbox.addWidget(self.ymins[i])
			self.spec_ylims_vbox.addWidget(QtGui.QLabel("ymax: "))
			self.spec_ylims_vbox.addWidget(self.ymaxs[i])
			self.spec_log_vbox.addWidget(QtGui.QLabel("log scale: "))
			self.spec_log_vbox.addWidget(self.logs[i])
			
			
		
		#-----Start and stop acquisition, etc.---------
		#The labels on these buttons should change once they've been pushed
		self.start_stop_acquisition_button=QtGui.QPushButton("Start\nAcquisition")
		self.save_buffer_button=QtGui.QPushButton("Save displayed\ndata") #TODO: more informative text
		self.stop_go_hbox.addWidget(self.start_stop_acquisition_button)
		self.stop_go_hbox.addWidget(self.save_buffer_button)
		
		#TODO jakov: probably a much better way would be to have the thread in stabiliser_class
		#invoke a callback function whenever it gets a new cutoff_wavelength and set_point

		timer = QtCore.QTimer(self)
		timer.start(1) #in ms. Updates once per second
		
		self.setCentralWidget(self.main_widget)

	def message(self,message="No message"):
		QtGui.QMessageBox.about(self, "MessageBox",message)
