
import sys

from PyQt4 import QtCore
from PyQt4.QtGui import *

import piezo_controller_server

min_volts = 0
max_volts = 75.0

print "Starting"

class PiezoControllerGUI(QWidget):
	def __init__(self, pzt_server):
		self.pzt_server = pzt_server
		self.pzt_server.gui = self #Line added 31/5/17 by RAN. Experimental.
		self.initUI()

	def initUI(self):
		QWidget.__init__(self)
		#self.setWidgetResizable(True)
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		#self.grid.setSpacing(1)
		
		self.connect_serial_checkBox = QCheckBox("Connect Serial Port", self)
		#self.connect_serial_checkBox.setGeometry(QtCore.QRect(50, 0, 101, 22))
		self.connect_serial_checkBox.setCheckState(QtCore.Qt.Checked if self.pzt_server.isEnabled() else QtCore.Qt.Unchecked)
		self.connect_serial_checkBox.stateChanged.connect(self.connect_serial_checkbox_changed)
		self.grid.addWidget(self.connect_serial_checkBox, 0, 0, 1, 3, QtCore.Qt.AlignHCenter)
		
		#self.grid.addWidget(QLabel(text), 2, i, 1, 1, QtCore.Qt.AlignHCenter)
		
		label_text = ['Interferometer', 'Cavity Length', 'Unused Channel Z']
		callbacks = [self.xSpinnerValueChanged, self.ySpinnerValueChanged, self.zSpinnerValueChanged]
		get_value = [self.pzt_server.getXvolts, self.pzt_server.getYvolts, self.pzt_server.getZvolts]
		self.spinners = []
		for i, text in enumerate(label_text):
			self.grid.addWidget(QLabel(text), 2, i, 1, 1, QtCore.Qt.AlignHCenter)
			
			spinner = QDoubleSpinBox(self)
			spinner.setDecimals(1)
			spinner.setSingleStep(0.1)
			spinner.setRange(min_volts, max_volts)
			spinner.setSuffix('V')
			if self.pzt_server.isEnabled():
				volts = get_value[i]()
			else:
				volts = 0
			print 'measured ' + str(volts) + 'V'
			spinner.setValue(volts)
			spinner.valueChanged.connect(callbacks[i])
			self.grid.addWidget(spinner, 3, i, 1, 1, QtCore.Qt.AlignHCenter)
			self.spinners.append(spinner)
			
	def connect_serial_checkbox_changed(self, state):
		try:
			self.pzt_server.setEnabled(state == QtCore.Qt.Checked)
		except Exception as e:
			print 'exception ' + str(e)
			self.connect_serial_checkBox.setCheckState(QtCore.Qt.Unchecked)
			QMessageBox.critical(piezo_gui_component, "Piezo Driver Switched Off", "Turn on piezo driver\nException = " + repr(e))
	
	def xSpinnerValueChanged(self, d):
		self.pzt_server.setXvolts(d)
	def ySpinnerValueChanged(self, d):
		self.pzt_server.setYvolts(d)
	def zSpinnerValueChanged(self, d):
		self.pzt_server.setZvolts(d)
		
	def setXvolts(self, d):
		self.pzt_server.setXvolts(d)
		self.spinners[0].setValue(d)
	def setYvolts(self, d):
		self.pzt_server.setYvolts(d)
		self.spinners[1].setValue(d)
	def setZvolts(self, d):
		self.pzt_server.setZvolts(d)
		self.spinners[2].setValue(d)
		
app = QApplication(sys.argv)
w = QMainWindow()
piezo_gui_component = None
pzt_server = piezo_controller_server.PiezoControllerServer(globals())
#eval piezo_gui_component.setXvolts(3.5)

piezo_gui_component = PiezoControllerGUI(pzt_server)

w.setWindowTitle('Piezo Controller GUI')
w.setCentralWidget(piezo_gui_component)
w.resize(piezo_gui_component.grid.minimumSize())
			
screen = QDesktopWidget().screenGeometry()
mysize = w.geometry()
w.move(screen.width() - mysize.width() - 15, 240) #magic numbers found by trial and error
		
w.show()
sys.exit(app.exec_())