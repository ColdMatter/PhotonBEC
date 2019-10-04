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
def enableUpdate(newValue):
	ui.enable_checkBox
	print "enableUpdate: called with "+str(newValue)
	#Called every time the enable tickbox is toggled.
	with fia_lock:
		#fia = FianiumLaser()
		if newValue==True:
			fia.enable()
			ui.currentLCD_alarms.setText("")
		else:
			fia.disable()
			ui.currentLCD_alarms.setText("Enable first before setting the parameters.")

	ui.enable_checkBox.setChecked(newValue)
	
#---Enable tick box------
ui.enable_checkBox.clicked.connect(enableUpdate)

def setValueUpdate_pe(newValue):
	#Called every time the pulse is set.
	with fia_lock:
		#fia = FianiumLaser()
		p = fia.setPulseEnergy(newValue)
		LaserSafetyAlarms()
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
	power=fia.getPower()
	pe=fia.getPulseEnergy()
	if power>=15 or pe>=6:
		ui.currentLCD_alarms.setText('NOT SAFE. LASER GOOGLES ON.')
		ui.currentLCD_pulse_energy.palette.setColor(QtGui.Palette.WindowText,QtGui.QColor(85,85,255))
		ui.currentLCD_pulse_energy.palette.setColor(QtGui.Palette.Background,QtGui.QColor(85,85,255))
		ui.setPalette(palette)
	else:
		ui.currentLCD_alarms.setText('SAFE. LASER GOOGLES OFF.')
	return None
		
#########################################################################
class PollPowerThread(threading.Thread):
	def run(self):
		#self.daemon = True
		time.sleep(2)
		while True:
			time.sleep(0.2)
			if ui.power_timer_checkBox.isChecked():
				getCurrentPulseEnergy()
				getCurrentRepetitionRate()
		return None
			

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