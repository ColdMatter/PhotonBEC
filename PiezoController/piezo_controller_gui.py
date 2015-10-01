
import sys

from PyQt4 import QtCore
from PyQt4.QtGui import *

import piezo_controller_server

min_volts = 0
max_volts = 75.0

class PiezoControllerGUI(QWidget):
	def __init__(self, pzt_server):
		self.pzt_server = pzt_server
		self.initUI()

	def initUI(self):
		QWidget.__init__(self)
		#self.setWidgetResizable(True)
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		#self.grid.setSpacing(1)
		
		'''
		self.connect_serial_checkBox = QCheckBox("Connect Serial Port", self)
		self.connect_serial_checkBox.setGeometry(QtCore.QRect(50, 0, 101, 22))
		self.connect_serial_checkBox.stateChanged.connect(self.connect_serial_checkbox_changed)
		self.grid.addWidget(self.connect_serial_checkBox, 0, 0, 1, 3, QtCore.Qt.AlignHCenter)
		'''
		
		label_text = ['Interferometer', 'Cavity Length', 'Unused Channel Z']
		callbacks = [self.xSpinnerValueChanged, self.ySpinnerValueChanged, self.zSpinnerValueChanged]
		get_value = [self.pzt_server.getXvolts, self.pzt_server.getYvolts, self.pzt_server.getZvolts]
		self.spinners = []
		for i, text in enumerate(label_text):
			self.grid.addWidget(QLabel(text), 1, i, 1, 1, QtCore.Qt.AlignHCenter)
			
			spinner = QDoubleSpinBox(self)
			spinner.setDecimals(1)
			spinner.setSingleStep(0.1)
			spinner.setRange(min_volts, max_volts)
			spinner.setSuffix('V')
			volts = get_value[i]()
			print 'measured ' + str(volts) + 'V'
			spinner.setValue(volts)
			spinner.valueChanged.connect(callbacks[i])
			self.grid.addWidget(spinner, 2, i, 1, 1, QtCore.Qt.AlignHCenter)
			self.spinners.append(spinner)
			
	def connect_serial_checkbox_changed(self, state):
		if state == QtCore.Qt.Checked:
			print 'connecting to serial'
		else:
			print 'disconnected from serial'
	
	def xSpinnerValueChanged(self, d):
		pzt_server.setXvolts(d)
	def ySpinnerValueChanged(self, d):
		pzt_server.setYvolts(d)
	def zSpinnerValueChanged(self, d):
		pzt_server.setZvolts(d)
		
app = QApplication(sys.argv)
w = QMainWindow()
pzt_server = piezo_controller_server.PiezoControllerServer()
piezo_gui_component = PiezoControllerGUI(pzt_server)

w.setWindowTitle('Piezo Controller GUI')
w.setCentralWidget(piezo_gui_component)
w.resize(piezo_gui_component.grid.minimumSize())
w.show()
sys.exit(app.exec_())