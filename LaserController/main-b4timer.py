#!/usr/bin/env python
#exit()

#ipython --gui=qt
#exec(open("main.py").read())
import sys,__main__
#from serial import *
import time
from InterfaceGUI import *
from LaserQuantum import *

def isInteractive():
    return not(hasattr(__main__, '__file__'))

app = QtGui.QApplication(sys.argv)
mw = QtGui.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(mw)
mw.show()

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

#----CURRENT VALUE BOX-----
def getCurrentPower():
	lq = LaserQuantum()
	p = lq.getPower()
	if p==None:
	    p="ERR"
	ui.currentLCD.display(p)
    
#ui.currentLCD.connect(getCurrentPower)
ui.getPowerPushButton.clicked.connect(getCurrentPower)

#---------------------------------
#FINAL COMMANDS FOR RUNNING IN NON-INTERACTIVE MODE
#---------------------------------
if ~isInteractive():
    sys.exit(app.exec_())


#EOF
