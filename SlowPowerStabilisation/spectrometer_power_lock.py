#Commands to run:
#ipython --gui=qt4
#>>>import sys
#>>>sys.path.append("D:\Control\learning\SpectrometerCavityLock")
#>>>import spectrometer_cavity_lock
#>>>spectrometer_cavity_lock.setSetPoint(<value>)
#>>>spectrometer_cavity_lock.s.start_acquisition()
#>>>cutoff_wavelength = spectrometer_cavity_lock.s.cutoff_wavelength

print "Let's get going"
import sys,__main__
from PyQt4 import QtGui
import time
import numpy as np
print "Done first import chunk"

from socket import gethostname
if gethostname()=="ph-photonbec":
	sys.path.append("D:\\Control\\PythonPackages\\")
	#sys.path.append("D:\\\Control\\SpectrometerCavityLock")
elif gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\\SpectrometerCavityLock\\")

print "Done socket stuff"

from spectrometerPowerStabiliser import SpectrometerPowerStabiliser
print "Imported Stabiliser class"
import spectrometer_power_lock_gui
print "Imported gui"
import pbec_ipc


print "Imported other 2 bits"

if __name__=="__main__":
	qApp = QtGui.QApplication(sys.argv)


	
print "Setting up stabiliser object"
s = SpectrometerPowerStabiliser() #The object that does the control
print "Setting up gui object"
aw = spectrometer_power_lock_gui.ApplicationWindow(s) #The main application GUI window. Knows about the stabiliser object.

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
	#s.set_voltage(np.mean(s.control_range)*1.5) #Hard coding by Ben 20171129 to allow more power through AOM as standard
	s.pic.reset()

aw.reset_button.pressed.connect(_reset_button_pushed)

def _save_buffer_button_pressed():
	filename = "cavity_lock_data.txt"
	results = s.results[-spectrometer_power_lock_gui.plot_buffer_length:]
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

def _setBECMaxChangedByText():
	try:
		newValue = float(aw.lambda0_text.text())
		newPixel = min(enumerate(s.lamb), key=lambda x: abs(x[1]-newValue))[0]
	except:
		pass
	else:
		s.lamb_bec_max = newValue
		s.pixel_bec_max = newPixel
		aw.lambda0_LCD.display(newValue)
		
aw.lambda0_text.returnPressed.connect(_setBECMaxChangedByText)

def _setBECMinChangedByText():
	try:
		newValue = float(aw.lambda1_text.text())
		newPixel = min(enumerate(s.lamb), key=lambda x: abs(x[1]-newValue))[0]
	except:
		pass
	else:
		s.lamb_bec_min = newValue
		s.pixel_bec_min = newPixel
		aw.lambda1_LCD.display(newValue)
		
aw.lambda1_text.returnPressed.connect(_setBECMinChangedByText)

def _setCloudMinChangedByText():
	try:
		newValue = float(aw.lambda2_text.text())
		newPixel = min(enumerate(s.lamb), key=lambda x: abs(x[1]-newValue))[0]
	except:
		pass
	else:
		s.lamb_cloud_min = newValue
		s.pixel_cloud_min = newPixel
		aw.lambda2_LCD.display(newValue)

aw.lambda2_text.returnPressed.connect(_setCloudMinChangedByText)
		
def _output_intensity_metric_changed():
	try:
		new_output_metric = aw.metric_menu.currentText()
	except:
		pass
	else:
		s.output_metric = new_output_metric
		
aw.metric_menu.activated.connect(_output_intensity_metric_changed)

def _setFianiumOutAmplitudeChanged():
	if s.laser == "Fianium":
		#try:
		newValue = float(aw.out_amp_text.text())
		if newValue < 36:
			print "Acceptable output amplitude"
		else:
			print "Not letting you set output amplitude higher than 35 until we've sorted safety more"
			newValue = 35
		s.change_fianium_output_amplitude(newValue)
		aw.out_amp_text.setText(str(newValue))
		aw.out_amp_LCD.display(newValue)
		#except:
		#	pass
	elif s.laser == "LaserQuantum":
		pass

aw.out_amp_text.returnPressed.connect(_setFianiumOutAmplitudeChanged)
		
aw.show()

#--------------------------------------------
#Now some functions for use when called as a package or via PBEC_IPC
def setSetPoint(newValue):
	aw.setLCD.display(newValue)
	s.set_point = newValue
	s.pic.set_point = newValue
	aw.setText.setText(str(newValue))

def setSetPointGradual(newValue, sleepTime = 3.0):
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

def stopAcquisition(stop_lock=True):
	if aw.acquisition_running:
		if aw.lock_on and stop_lock:
			_start_stop_lock_button_pushed()
		_start_stop_acquisition_button_pushed()
	else:
		pass

def startAcquisition(restart_lock=True):
	if aw.acquisition_running:
		pass
	else:
		_start_stop_acquisition_button_pushed()
		if not(aw.lock_on) and restart_lock:
			_start_stop_lock_button_pushed()

def setSpectrometerIntegrationTime(newValue,pause_lock=True):
	#s.stop_acquisition()
	#s.spec_int_time = newValue
	#s.start_acquisition()
	pause_lock = aw.lock_on and pause_lock
	stopAcquisition(stop_lock = pause_lock)
	s.spec_int_time = newValue
	startAcquisition(restart_lock = pause_lock)
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
	try:
		pbec_ipc.start_server(globals(), port = 47905)
		sys.exit(qApp.exec_())
	finally:
		s.spectro.close() #This might catch the errors.

#MISSING: when application window is closed, stabiliser thread should also be stopped.

#EoF

