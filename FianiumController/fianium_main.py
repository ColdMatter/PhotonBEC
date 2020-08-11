#!/usr/bin/env python
import sys
import socket
if socket.gethostname().lower()=="ph-photonbec":
	fianium_comport=4
	sys.path.append("Z:\\Control\\PythonPackages\\")
	sys.path.append("Z:\\Control\\FianiumController\\")
elif socket.gethostname().lower()=="ph-photonbec3":
	fianium_comport=6
	sys.path.append("D:\\Control\\PythonPackages\\")
	sys.path.append("D:\\Control\\FianiumController\\")
elif socket.gethostname().lower()=="ph-photonbec5":
	fianium_comport=14
	sys.path.append("D:\\Control\\PythonPackages\\")
	sys.path.append("D:\\Control\\FianiumController\\")

import __main__
from serial import *
import time, threading
import pbec_ipc
from InterfaceGUI_fianium import *

app = QtGui.QApplication(sys.argv)
mw = QtGui.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(mw)


#---------------------------------
#SERIAL PORT UTILITIES
#---------------------------------
from fianium import *
fia = FianiumLaser()

fia_lock = threading.Lock()


def updateSetPulseEnergyGUI(newSetValue):
	ui.setLCD_pulse_energy.display(newSetValue)
	ui.setText_pulse_energy.setText(str(newSetValue))
    
#---------------------------------
#ADDITIONAL SETUP
#---------------------------------
def enableUpdate(newValue=None):
	if newValue==None:
		print "I think you are using PySides, getting value from GUI"
		state = ui.enable_checkBox.checkState()
		if state==QtCore.Qt.CheckState.Unchecked:
			print "trying to disable"
			newValue = False
		elif state==QtCore.Qt.CheckState.Checked:
			print "trying to enable"
			newValue = True
		elif state==QtCore.Qt.CheckState.PartiallyChecked: 
			print "what are you trying to do?"
		else:
			print "something went wrong"
	else:
		print "I think you are using PyQt4, with newValue="+str(newValue)
	
	ui.enable_checkBox #What is this line doing?
	#Called every time the enable tickbox is toggled.
	with fia_lock:
		#fia = FianiumLaser()
		if newValue==True:
			fia.enable()
			ui.currentLCD_alarms.setText("")
		else:
			fia.disable()
			ui.currentLCD_alarms.setText("Enable first before setting up the parameters.")

	ui.enable_checkBox.setChecked(newValue)

#---Enable tick box------
ui.enable_checkBox.clicked.connect(enableUpdate)

def setValueUpdate_pe(newValue):
	#Called every time the pulse is set.
	with fia_lock:
		#fia = FianiumLaser()
		p = fia.setPulseEnergy(newValue)
		LaserSafetyAlarms() #This line gives trouble. Why?
	updateSetPulseEnergyGUI(newValue)



#---Text control for pulse energy------
def setValueChangedByText_pe():
    try:
		newValue = float(ui.setText_pulse_energy.text())
    except:
		pass
    else:
		ui.setLCD_pulse_energy.display(newValue)
		setValueUpdate_pe(newValue)
	#

ui.setTextButton_pulse_energy.clicked.connect(setValueChangedByText_pe)
ui.setText_pulse_energy.returnPressed.connect(setValueChangedByText_pe)

def updateSetRepetitionRateGUI(newSetValue):
    ui.setLCD_rr.display(newSetValue)
    ui.setText_rr.setText(str(newSetValue))
    
#---------------------------------
#ADDITIONAL SETUP
#---------------------------------


def setValueUpdate_rr(newValue):
	#Called every time the power is set.
	with fia_lock:
		#fia = FianiumLaser()
		p = fia.setRepetitionRate(newValue)
		LaserSafetyAlarms()
	updateSetRepetitionRateGUI(newValue)

#---Text control for pulse energy------
def setValueChangedByText_rr():
    try:
		newValue = float(ui.setText_rr.text())
    except:
		pass
    else:
		ui.currentLCD_rr.display(newValue)
		setValueUpdate_rr(newValue)
	#

ui.setTextButton_rr.clicked.connect(setValueChangedByText_rr)
ui.setText_rr.returnPressed.connect(setValueChangedByText_rr)

#----CURRENT VALUE BOX PULSE ENERGY-----
def getCurrentPulseEnergy():
	with fia_lock:
		#fia = FianiumLaser()
		p = fia.getPulseEnergy()
	if p==None:
		p="ERR"
	print 'got current pulse energy = ' + str(p)
	ui.currentLCD_pulse_energy.display(p)
	return p
	
def getData(self):
	pass
#ui.currentLCD.connect(getCurrentPower)
ui.getDataPushButton.clicked.connect(getData)

#----CURRENT VALUE BOX REPETITION RATE-----
def getCurrentRepetitionRate():
	with fia_lock:
		#fia = FianiumLaser()
		p = fia.getRepetitionRate()
	if p==None:
		p="ERR"
	print 'got current repetition rate = ' + str(p)
	ui.currentLCD_rr.display(p)
	return p
	
def LaserSafetyAlarms():
	#This is a very slow step, and I can't see why it should be
	#print "LaserSafetyAlarms: getting power...",
	#pow=fia.getPower()
	#print "pulse energy...",
	#pe=fia.getPulseEnergy()
	print "LaserSafetyAlarms: getting pulse energy and rep rate...",
	pe,rr = fia.getPulseEnergyAndRepetitionRate()
	pow = float(pe)*float(rr)
	print "done"
	if pow>=15 or pe>=6:
		new_text = "NOT SAFE. LASER GOOGLES ON."
	else:
		new_text = "SAFE. LASER GOOGLES OFF."
	ui.currentLCD_alarms.setText(new_text)
	



	
#########################################################################
class PollPowerThread(threading.Thread):
	def run(self):
		#self.daemon = True
		time.sleep(1)
		while True:
			time.sleep(0.2)
			if ui.power_timer_checkBox.isChecked():
				getCurrentPulseEnergy()
				getCurrentRepetitionRate()
			

#if FianiumLaser().isEnabled():
if fia.isEnabled():
	ui.enable_checkBox.setCheckState(QtCore.Qt.Checked)
else:
	ui.enable_checkBox.setCheckState(QtCore.Qt.Unchecked)
	ui.currentLCD_alarms.setText("Enable first before setting up the parameters.")
mw.show()

#---------------------------------
#FINAL COMMANDS FOR RUNNING IN NON-INTERACTIVE MODE
#---------------------------------
def isInteractive():
    return not(hasattr(__main__, '__file__'))

if ~isInteractive():
	bind_success = pbec_ipc.start_server(globals(), port = pbec_ipc.PORT_NUMBERS['fianium_controller'])
	if not bind_success:
		print 'Laser Controller already running, quitting...'
	ppt = PollPowerThread()
	ppt.daemon = True
	ppt.start()
	ui.power_timer_checkBox.setCheckState(QtCore.Qt.Checked)
	sys.exit(app.exec_())
###########################################################################
#EOF