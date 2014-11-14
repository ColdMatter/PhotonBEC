#python main.py
import sys,__main__
from serial import *
import time
from cavity_lock_gui import *
from stabiliser_class import Stabiliser

qApp = QtGui.QApplication(sys.argv)


s = Stabiliser() #The object that does the control
aw = ApplicationWindow(s) #The main application GUI window. Knows about the stabiliser object.


def setValueChangedByText():
    try:
		newValue = int(aw.setText.text())
    except:
		pass
    else:
		aw.setLCD.display(newValue)
		aw.dc.update_parameter(newValue)
		s.set_point = newValue
		s.pic.set_point = newValue
		#
aw.setText.returnPressed.connect(setValueChangedByText)

def start_stop_acquisition_button_pushed():
	aw.acquisition_running=not(aw.acquisition_running)
	if aw.acquisition_running:
		aw.start_stop_acquisition_button.setText("Stop\nAcquisition")
		#Now do the things you need to do
		s.start_acquisition()
	else:
		aw.start_stop_acquisition_button.setText("Start\nAcquisition")
		#Now do the things you need to do
		s.stop_acquisition()
	aw.start_stop_acquisition_button.update()

aw.start_stop_acquisition_button.pressed.connect(start_stop_acquisition_button_pushed)

def start_stop_lock_button_pushed():
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

aw.start_stop_lock_button.pressed.connect(start_stop_lock_button_pushed)


#from pylab import *
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure

def check_centre_button_pushed():
	aw.popup()
	
	
aw.check_centre_button.pressed.connect(check_centre_button_pushed)


aw.show()
sys.exit(qApp.exec_())
#MISSING: when application window is closed, stabiliser thread should also be stopped.
#MISSING: push-button to find centre and display graph showing how well ring has been found
#EoF

