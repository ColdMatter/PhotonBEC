#ipython --matplotlib=qt

import sys, os, random
from PyQt5 import QtCore, QtWidgets

from pylab import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from socket import gethostname
from time import sleep

#Computer dependent paths
from socket import gethostname
if gethostname()=="ph-rnyman-01":
	sys.path.append("D:\\Control\\PythonPackages\\")
	sys.path.append("D:\\\Control\\Multispec_server")
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\\Multispec_server\\")
elif gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")
	sys.path.append("D:\\Control\\Multispec_server\\")
elif gethostname()=="ph-photonbec5":
	sys.path.append("D:\\Control\\PythonPackages\\")
	sys.path.append("D:\\Control\\Multispec_server\\")
elif gethostname()=="ph-jrodri10":
	sys.path.append("X:\\Control\\PythonPackages\\")
else:
	raise Exception('Unknown machine')

from pbec_analysis import slice_data
from single_spec_runner import SingleSpectrometer


##### Show the most recently acquired spectrum
class EmbeddedLatestSpectrumGraph(FigureCanvas):

	def __init__(self, spectrometer, parent=None, width=4, height=4.5, dpi=100):
		self.spectrometer = spectrometer
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		self.xmin, self.xmax, self.ymin, self.ymax = None, None, None, None
		self.logscale = True
		self.update_time = 50 # Plot canvas update time (in ms)

		self.plot = self.fig.add_subplot(1,1,1)
		self.xmin = 560
		self.xmax = 600
		self.ymin = 1
		self.ymax = 40000

		self.fig.subplots_adjust(bottom=0.15,left=0.20,top=0.9,right=0.95)
		
		FigureCanvas.__init__(self, self.fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.compute_initial_figure()
		
		self.timer = QtCore.QTimer(self)
		#
		# this line would work on pyqt4
		#QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		self.timer.timeout.connect(self.update_figure)
		self.timer.start(self.update_time) # in ms


	def compute_initial_figure(self):

		self.plot.plot([-40,-50], [0.1,0.1])
		if self.logscale:
			self.plot.set_yscale("log")
		else:
			self.plot.set_yscale("linear")
		self.plot.set_xlabel("Wavelength (nm)", fontsize=9)
		self.plot.set_ylabel("Spectrum", fontsize=9)
		self.plot.set_xlim(self.xmin,self.xmax)
		self.plot.set_ylim(self.ymin, self.ymax)
		self.draw()
			

	def update_figure(self):
		if self.spectrometer.spectro.allow_grabbing == True:
			try:
				# grabs data from spectrometer
				self.spectrum_time_label, self.spectrum_new_data_flag, self.lamb, self.spectrum = self.spectrometer.spectro.get_data()

				#cut = slice_data(self.lamb, self.spectrum, (self.xmin,self.xmax))
				#cutlamb, cutspec = cut[0], cut[1]
				cutlamb = self.lamb
				cutspec = self.spectrum
					
				# Updates the figure with the data just grabbed, new or not
				self.lin = self.plot.lines[0]
				self.lin.set_xdata(cutlamb)
				self.lin.set_ydata(cutspec)
				self.plot.draw_artist(self.plot.patch)
				self.plot.draw_artist(self.lin)
				self.update()
				self.flush_events()
				print("Last retrieved spectrum time label = "+str(self.spectrum_time_label)+" (new data = "+str(self.spectrum_new_data_flag)+')')
	
			except Exception as e:
				print(' *** Error grabbing data from spectrometer ***')
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				#print(exc_type, fname, exc_tb.tb_lineno)				
				print("Line: "+str(exc_tb.tb_lineno)+": "+str(e))

		


##### Main window
class ApplicationWindow(QtWidgets.QWidget):

	def __init__(self, spectrometer):
		print("Starting App window")
		self.spectrometer = spectrometer
		QtWidgets.QWidget.__init__(self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setWindowTitle("Single Spectrometer Server (V2)")
		self.setGeometry(QtCore.QRect(500, 540, 950, 450))
		# Set some useful parameters
		self.continuous_mode_flag = False

		
		# Layout of the main window
		self.main_widget = QtWidgets.QWidget(self)
		self.vbox = QtWidgets.QVBoxLayout(self.main_widget)
		self.graph_hbox = QtWidgets.QHBoxLayout()
		self.all_graph_box = QtWidgets.QHBoxLayout()
		self.vbox.addLayout(self.graph_hbox)
		self.graph_hbox.addLayout(self.all_graph_box)
		self.stop_go_hbox = QtWidgets.QHBoxLayout()
		self.vbox.addLayout(self.stop_go_hbox)
		self.spec_controls_hbox = QtWidgets.QHBoxLayout()
		self.graph_hbox.addLayout(self.spec_controls_hbox)


		
		# Add the spectrum display graph
		self.sg = EmbeddedLatestSpectrumGraph(self.spectrometer, parent=self.main_widget, width=4, height=3, dpi=100)
		self.all_graph_box.addWidget(self.sg)

		# Change integration time and n averages
		self.spec_settings_vbox = QtWidgets.QVBoxLayout()
		self.spec_controls_hbox.addLayout(self.spec_settings_vbox)
		self.int_time = QtWidgets.QLineEdit()

		self.spec_settings_vbox.addWidget(QtWidgets.QLabel("Int time: "))
		self.spec_settings_vbox.addWidget(self.int_time)
		self.n_averages = QtWidgets.QLineEdit()
		self.spec_settings_vbox.addWidget(QtWidgets.QLabel("n averages: "))
		self.spec_settings_vbox.addWidget(self.n_averages)
			
		# Change graph limits and other specs
		self.spec_lims_hbox = QtWidgets.QHBoxLayout()
		self.spec_controls_hbox.addLayout(self.spec_lims_hbox)
		self.spec_xlims_vbox = QtWidgets.QVBoxLayout()
		self.spec_ylims_vbox = QtWidgets.QVBoxLayout()
		self.spec_log_vbox = QtWidgets.QVBoxLayout()
		self.spec_lims_hbox.addLayout(self.spec_xlims_vbox)
		self.spec_lims_hbox.addLayout(self.spec_ylims_vbox)
		self.spec_lims_hbox.addLayout(self.spec_log_vbox)
		self.xmin = QtWidgets.QLineEdit()
		self.xmax = QtWidgets.QLineEdit()
		self.ymin = QtWidgets.QLineEdit()
		self.ymax = QtWidgets.QLineEdit()
		self.log = QtWidgets.QCheckBox()
		self.spec_xlims_vbox.addWidget(QtWidgets.QLabel("xmin: "))
		self.spec_xlims_vbox.addWidget(self.xmin)
		self.spec_xlims_vbox.addWidget(QtWidgets.QLabel("xmax: "))
		self.spec_xlims_vbox.addWidget(self.xmax)
		self.spec_ylims_vbox.addWidget(QtWidgets.QLabel("ymin: "))
		self.spec_ylims_vbox.addWidget(self.ymin)
		self.spec_ylims_vbox.addWidget(QtWidgets.QLabel("ymax: "))
		self.spec_ylims_vbox.addWidget(self.ymax)
		self.spec_log_vbox.addWidget(QtWidgets.QLabel("Log scale: "))
		self.spec_log_vbox.addWidget(self.log)

		self.ext_trigger_vbox = QtWidgets.QVBoxLayout() 
		self.spec_lims_hbox.addLayout(self.ext_trigger_vbox) 
		self.ext_trigger = QtWidgets.QCheckBox()
		self.ext_trigger_vbox.addWidget(QtWidgets.QLabel("Ext Trigger: "))
		self.ext_trigger_vbox.addWidget(self.ext_trigger)
			

		# Start and stop acquisition, etc
		self.start_stop_acquisition_button=QtWidgets.QPushButton("Internal mode activated\n(Press to start continuous mode)")
		self.stop_go_hbox.addWidget(self.start_stop_acquisition_button)

		self.main_widget.adjustSize()

		timer = QtCore.QTimer(self)
		timer.start(50) # in ms. Updates once per second

		#self.setCentralWidget(self.main_widget)


