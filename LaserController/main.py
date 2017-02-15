#!/usr/bin/env python
#exit()

import sys
sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("Y:\\Control\\PythonPackages\\")

#ipython --gui=qt
#exec(open("main.py").read())
import __main__
from serial import *
import time, threading
import pbec_ipc
from InterfaceGUI import *

app = QtGui.QApplication(sys.argv)
mw = QtGui.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(mw)


#---------------------------------
#SERIAL PORT UTILITIES
#---------------------------------
from LaserQuantum import *	
#lq = LaserQuantum()

lq_lock = threading.Lock()

def updateSetPowerGUI(newSetValue):
    ui.setLCD.display(newSetValue)
    ui.setText.setText(str(newSetValue))
    
#---------------------------------
#ADDITIONAL SETUP
#---------------------------------
def enableUpdate(newValue):
	ui.enable_checkBox
	#Called every time the enable tickbox is toggled.
	with lq_lock:
		lq = LaserQuantum()
		if newValue==True:
			lq.LaserOn()
		else:
			lq.LaserOff()
	ui.enable_checkBox.setChecked(newValue)

def setValueUpdate(newValue):
	#Called every time the power is set.
	with lq_lock:
		lq = LaserQuantum()
		p = lq.setPower(newValue)
	updateSetPowerGUI(newValue)

#---Enable tick box------
ui.enable_checkBox.clicked.connect(enableUpdate)


#---Slider control for power------
def setValueChangedBySlider():
    newSetValue = ui.powerSlider.value()
    setValueUpdate(newSetValue)

ui.powerSlider.sliderReleased.connect(setValueChangedBySlider)

#---Text control for power------
def setValueChangedByText():
    try:
		newValue = float(ui.setText.text())
    except:
		pass
    else:
		ui.setLCD.display(newValue)
		ui.powerSlider.setValue(newValue)
		setValueUpdate(newValue)
	#

ui.setTextButton.clicked.connect(setValueChangedByText)
ui.setText.returnPressed.connect(setValueChangedByText)

#----CURRENT VALUE BOX-----
def getCurrentPower():
	with lq_lock:
		lq = LaserQuantum()
		p = lq.getPower()
	if p==None:
		p="ERR"
	print 'got current power = ' + str(p)
	ui.currentLCD.display(p)
	#ui.powerSlider.setValue(p)
	return p
	
def guiSetPowerAndWait(p, tolerance=0.01):
	updateSetPowerGUI(p)
	def power_gui_update(p):
		ui.currentLCD.display(p)
	with lq_lock:
		lq = LaserQuantum()
		lq.setPowerAndWait(p, tolerance=0.01, callback_power=power_gui_update)
	
#ui.currentLCD.connect(getCurrentPower)
ui.getPowerPushButton.clicked.connect(getCurrentPower)

class PollPowerThread(threading.Thread):
	def run(self):
		#self.daemon = True
		time.sleep(2)
		while True:
			time.sleep(0.2)
			if ui.power_timer_checkBox.isChecked():
				getCurrentPower()

if LaserQuantum().isEnabled():
	ui.enable_checkBox.setCheckState(QtCore.Qt.Checked)
else:
	ui.enable_checkBox.setCheckState(QtCore.Qt.Unchecked)

	
mw.show()

#---------------------------------
#FINAL COMMANDS FOR RUNNING IN NON-INTERACTIVE MODE
#---------------------------------
def isInteractive():
    return not(hasattr(__main__, '__file__'))

if ~isInteractive():
	bind_success = pbec_ipc.start_server(globals(), port = 47903)
	if not bind_success:
		print 'Laser Controller already running, quitting...'
	ppt = PollPowerThread()
	ppt.daemon = True
	ppt.start()
	ui.power_timer_checkBox.setCheckState(QtCore.Qt.Checked)
	sys.exit(app.exec_())


#EOF
