#!/usr/bin/env python
#exit()

#ipython --gui=qt
#exec(open("main.py").read())
import sys,__main__
from serial import *
import time
from InterfaceGUI import *

def isInteractive():
    return not(hasattr(__main__, '__file__'))

app = QtGui.QApplication(sys.argv)
mw = QtGui.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(mw)


#---------------------------------
#SERIAL PORT UTILITIES
#---------------------------------
from LaserQuantum import *	

#lq = LaserQuantum()

#---------------------------------
#ADDITIONAL SETUP
#---------------------------------
def enableUpdate(newValue):
	#Called every time the enable tickbox is toggled.
	lq = LaserQuantum()
	if newValue==True:
		lq.LaserOn()
	else:
		lq.LaserOff()
	

def setValueUpdate(newValue):
	#Called every time the power is set.
	lq = LaserQuantum()
	p = lq.setPower(newValue)

#---Enable tick box------
ui.enable_checkBox.clicked.connect(enableUpdate)


#---Slider control for power------
def setValueChangedBySlider():
    newSetValue=ui.powerSlider.value()
    ui.setLCD.display(newSetValue)
    ui.setText.setText(str(newSetValue))
    setValueUpdate(newSetValue)

ui.powerSlider.sliderReleased.connect(setValueChangedBySlider)

#---Text control for power------
def setValueChangedByText():
    try:
		newValue = int(ui.setText.text())
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
	print("getting current power")
	lq = LaserQuantum()
	p = lq.getPower()
	if p==None:
	    p="ERR"
	ui.currentLCD.display(p)
	#ui.powerSlider.setValue(p)
    
#ui.currentLCD.connect(getCurrentPower)
ui.getPowerPushButton.clicked.connect(getCurrentPower)


ui.powerTimer = QtCore.QTimer()
ui.powerTimer.timeout.connect(getCurrentPower)

def power_timer_checked(newValue):
	if newValue:
		ui.powerTimer.start(500)
	else:
		ui.powerTimer.stop()

ui.powerTimer.start(500)
ui.power_timer_checkBox.setCheckState(QtCore.Qt.Checked)
ui.power_timer_checkBox.clicked.connect(power_timer_checked)

if LaserQuantum().isEnabled():
	ui.enable_checkBox.setCheckState(QtCore.Qt.Checked)
else:
	ui.enable_checkBox.setCheckState(QtCore.Qt.Unchecked)

	
mw.show()

#---------------------------------
#FINAL COMMANDS FOR RUNNING IN NON-INTERACTIVE MODE
#---------------------------------
if ~isInteractive():
    sys.exit(app.exec_())


#EOF
