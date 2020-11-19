'''
	Written by:		Joao Rodrigues
	Last Update: 	October 16th 2020

'''

import sys,__main__
from PyQt5 import QtCore, QtWidgets
import time
import numpy as np
from time import sleep

from socket import gethostname
if gethostname()=="ph-photonbec":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\\Multispec_server\\")
elif gethostname()=="ph-photonbec5":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-jrodri10":
	sys.path.append("X:\\Control\\PythonPackages\\")
else:
	raise Exception('Unknown machine')

import single_spec_server_gui
from single_spec_runner import SingleSpectrometer
import pbec_ipc


if __name__=="__main__":
	qApp = QtWidgets.QApplication(sys.argv)
s = SingleSpectrometer(int_time=10, n_averages=1, continuous_mode_flag=False, external_trigger_flag=False)
aw = single_spec_server_gui.ApplicationWindow(s)
# Fills the GUI entries
aw.int_time.setText(str(s.spec_int_time))
aw.n_averages.setText(str(s.spec_n_averages))
aw.xmin.setText(str(aw.sg.xmin))
aw.xmax.setText(str(aw.sg.xmax))
aw.ymin.setText(str(aw.sg.ymin))
aw.ymax.setText(str(aw.sg.ymax))
aw.log.setChecked(aw.sg.logscale)
aw.ext_trigger.setChecked(s.external_trigger_flag)



def _start_stop_acquisition_button_pushed():
	aw.continuous_mode_flag = not(aw.continuous_mode_flag)
	if aw.continuous_mode_flag is True:
		s.stop_acquisition()
		s.continuous_mode_flag = True
		s.start_acquisition()
		aw.start_stop_acquisition_button.setText("Continuous mode activated\n(Press to start internal mode)")
	else:
		s.stop_acquisition()
		s.continuous_mode_flag = False
		aw.start_stop_acquisition_button.setText("Internal mode activated\n(Press to start continuous mode)")
	aw.start_stop_acquisition_button.update()
aw.start_stop_acquisition_button.pressed.connect(_start_stop_acquisition_button_pushed)



def _change_limits():

	try:
		aw.sg.xmin = float(aw.xmin.text())
	except:
		pass
	try:
		aw.sg.xmax = float(aw.xmax.text())
	except:
		pass
	try:
		aw.sg.ymin = float(aw.ymin.text())
	except:
		pass
	try:
		aw.sg.ymax = float(aw.ymax.text())
	except:
		pass
	try:
		state = aw.log.isChecked()
		aw.sg.logscale = state
	except:
		pass

	aw.sg.timer.stop()
	aw.sg.compute_initial_figure()
	aw.sg.timer.start(aw.sg.update_time) # ms between updates	

for limit in [aw.xmin] + [aw.xmax] + [aw.ymin] + [aw.ymax]:
	limit.returnPressed.connect(_change_limits)
aw.log.clicked.connect(_change_limits)



def _change_external_trigger():
	try:
		state = aw.ext_trigger.isChecked()
		s.set_external_trigger(external_trigger=state)
	except:
		pass
aw.ext_trigger.clicked.connect(_change_external_trigger)



def _change_spec_settings():
	try:
		new_int_time = float(aw.int_time.text())
		if new_int_time >= s.min_spec_int_time:
			s.spec_int_time = new_int_time
			print('-> Setting integration time to '+str(new_int_time)+ ' ms')
		else:
			print("-> Trying to set an invalid integration time. Setting integration time to {0} ms instead".format(s.min_spec_int_time))
			s.spec_int_time = s.min_spec_int_time
			aw.int_time.setText(str(s.min_spec_int_time))
	except Exception as e:
		print("\n\n *** Error setting up spectrometer integration time *** \n\n")
		raise(e)
	
	try:
		new_n_average = int(float(aw.n_averages.text()))
		if new_n_average!=0:
			s.spec_n_averages = new_n_average
			print('-> Setting number of averages to '+str(new_n_average))
		else:
			print("-> Can't have zero averages... Keeping previous number of averages.")
	except Exception as e:
		print("\n\n *** Error setting up spectrometer averages *** \n\n")
		raise Exception(e)

	if s.continuous_mode_flag is True:
		s.stop_acquisition()
		s.start_acquisition()
	
for parameter in [aw.int_time] + [aw.n_averages]:
	parameter.returnPressed.connect(_change_spec_settings)
	

aw.show()




##### Functions to be called as a package or via IPC

def set_spectrometer_mode(mode='continuous'):
	if mode == 'continuous':
		if aw.continuous_mode_flag is True:
			pass
		else:
			_start_stop_acquisition_button_pushed()
	elif mode == 'internal':
		if aw.continuous_mode_flag is True:
			_start_stop_acquisition_button_pushed()
		else:
			pass
	else:
		raise Exception("\n\n***Invalid spectrometer mode ***\n\n")


def getSpectrometerIntegrationTime():
	return float(aw.int_time.text())


def setSpectrometerIntegrationTime(newValue):
	if not newValue == float(aw.int_time.text()):
		if newValue >= s.min_spec_int_time:
			aw.int_time.setText(str(newValue))
		else:
			print("Trying to set an invalid integration time. Setting integration time to {0} ms instead".format(s.min_spec_int_time))
			aw.int_time.setText(str(s.min_spec_int_time))
		_change_spec_settings()
	return None


def getSpectrometerNAverages():
	return int(aw.n_averages.text())


def setSpectrometerNAverages(newValue):
	newValue = int(newValue)
	if not newValue == int(aw.n_averages.text()):
		aw.n_averages.setText(str(newValue))
		_change_spec_settings()
	return None
		


def setSpectrometerExternalTrigger(external_trigger_flag):
	if (external_trigger_flag is True and aw.ext_trigger.isChecked() is False):
		aw.ext_trigger.setChecked(True)
		_change_external_trigger()
	elif (external_trigger_flag is False and aw.ext_trigger.isChecked() is True):
		aw.ext_trigger.setChecked(False)
		_change_external_trigger()
	else:
		pass
		


def get_single_spectrum(int_time, n_averages, n_measures):
	if aw.continuous_mode_flag == True:
		print("-> Warning: Spectrometer is in continuous mode... Changing to internal mode")
		set_spectrometer_mode(mode='internal')
	setSpectrometerIntegrationTime(newValue=int_time)
	setSpectrometerNAverages(newValue=n_averages)
	s.start_acquisition(n_measures=n_measures)
	return None


if __name__=="__main__":
	try:
		pbec_ipc.start_server(globals(), port=47908)
		sys.exit(qApp.exec_())
	finally:
		s.spectro.close()
		s.free_dll()


