#Commands to run:
#ipython --gui=qt4
#>>>import sys
#>>>sys.path.append("D:\Control\CavityLock")
#>>>import cavity_lock
#>>>cavity_lock.setSetPoint(<value>)
#>>>cavity_lock.s.start_acquisition()
#>>>ring_rad = cavity_lock.s.ring_rad
##Oh dear. There are threading issues: "time.sleep()" function locks GUI but not StabiliserThread!!!
#Lock fails when blocking calls are run, although time.sleep() seems not to cause too many problems.


import sys,__main__
from PyQt4 import QtGui
import time
import numpy as np
#sys.path.append("C:\\photonbec\\Control\\PythonPackages\\")
sys.path.append("D:\Control\CavityLock")

import cavity_lock_gui
from stabiliser_class import Stabiliser
import pbec_ipc

if __name__=="__main__":
	qApp = QtGui.QApplication(sys.argv)

s = Stabiliser() #The object that does the control
aw = cavity_lock_gui.ApplicationWindow(s) #The main application GUI window. Knows about the stabiliser object.

def _setValueChangedByText():
    try:
		newValue = float((aw.setText.text()))
    except:
		pass
    else:
		aw.setLCD.display(newValue)
		s.set_point = newValue
		s.pic.set_point = newValue

aw.setText.returnPressed.connect(_setValueChangedByText)

def _start_stop_acquisition_button_pushed():
	aw.acquisition_running=not(aw.acquisition_running)
	if aw.acquisition_running:
		aw.start_stop_acquisition_button.setText("Stop\nAcquisition")
		#Now do the things you need to do
		s.start_acquisition()
		aw.check_centre_button.setEnabled(True)
		aw.set_centre_button.setEnabled(True)
	else:
		aw.start_stop_acquisition_button.setText("Start\nAcquisition")
		#Now do the things you need to do
		s.stop_acquisition()
	aw.start_stop_acquisition_button.update()

aw.start_stop_acquisition_button.pressed.connect(_start_stop_acquisition_button_pushed)

def _start_stop_lock_button_pushed():
	aw.lock_on=not(aw.lock_on)
	if aw.lock_on:
		aw.start_stop_lock_button.setText("Stop\nLock")
		#Now do the things you need to do
		s.start_lock()
	else:
		aw.start_stop_lock_button.setText("Start\nLock")
		#Now do the things you need to do
		s.stop_lock()
	aw.start_stop_lock_button.update()

aw.start_stop_lock_button.pressed.connect(_start_stop_lock_button_pushed)

def _reset_button_pushed():
	s.set_voltage(np.mean(s.control_range))
	s.pic.reset()

aw.reset_button.pressed.connect(_reset_button_pushed)

def _check_centre_button_pressed():
	aw.popup_check_centre_window()

aw.check_centre_button.pressed.connect(_check_centre_button_pressed)

def _set_centre_button_pressed():
	aw.popup_set_centre_window()

aw.set_centre_button.pressed.connect(_set_centre_button_pressed)

def _save_buffer_button_pressed():
	filename = "cavity_lock_data.txt"
	results = s.results[-cavity_lock_gui.plot_buffer_length:]
	fil = open(filename,"w")
	for r in results:
		fil.write(str(r))
		fil.write("\n")
	fil.close()
	
aw.save_buffer_button.pressed.connect(_save_buffer_button_pressed)


def _setPGainChangedByText():
    try:
		newValue = float(aw.set_Pgain.text())
    except:
		pass
    else:
		s.pic.P_gain = newValue #not working...
		aw.Pgain_text.setText(str(s.pic.P_gain))

aw.set_Pgain.returnPressed.connect(_setPGainChangedByText)

def _setIGainChangedByText():
    try:
		newValue = float(aw.set_Igain.text())
    except:
		pass
    else:
		s.pic.I_gain = newValue #not working...
		aw.Igain_text.setText(str(s.pic.I_gain))

aw.set_Igain.returnPressed.connect(_setIGainChangedByText)

def _setIIGainChangedByText():
    try:
		newValue = float(aw.set_IIgain.text())
    except:
		pass
    else:
		s.pic.II_gain = newValue #not working...
		aw.IIgain_text.setText(str(s.pic.II_gain))

aw.set_IIgain.returnPressed.connect(_setIIGainChangedByText)

def _setIConstChangedByText():
    try:
		newValue = float(aw.set_Iconst.text())
    except:
		pass
    else:
		s.pic.I_const = newValue #not working...
		aw.Iconst_text.setText(str(s.pic.I_const))

aw.set_Iconst.returnPressed.connect(_setIConstChangedByText)

def _setIIConstChangedByText():
    try:
		newValue = float(aw.set_IIconst.text())
    except:
		pass
    else:
		s.pic.II_const = newValue #not working...
		aw.IIconst_text.setText(str(s.pic.II_const))

aw.set_IIconst.returnPressed.connect(_setIIConstChangedByText)

aw.show()

#--------------------------------------------
#Now some functions for use when called as a package
def setSetPoint(newValue):
	aw.setLCD.display(newValue)
	s.set_point = newValue
	s.pic.set_point = newValue
	aw.setText.setText(str(newValue))

def setSetPointGradual(newValue, sleepTime = 0.05):
	first = s.pic.set_point
	last = newValue
	if first==last:
		return None
	for p in np.arange(first, last, np.sign(last-first)):
		#NOTE: will fail when non-integer start and end points are set.
		setSetPoint(p)
		time.sleep(sleepTime)
	setSetPoint(last)
	return None
	
#--------------------------------------------
	

"""
def exit_func():
	#Could be used as		sys.exit(exit_func())
	#Instead of		sys.exit(qApp.exec_())
	s.stop_lock()
	s.stop_acquisition()
	qApp.exec_()
"""

if __name__=="__main__":
	pbec_ipc.start_server(globals(), port = 47902)
	sys.exit(qApp.exec_())

#MISSING: when application window is closed, stabiliser thread should also be stopped.

#EoF

