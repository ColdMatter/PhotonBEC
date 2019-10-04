#Commands to run:
#ipython --gui=qt4
#>>>import sys
#>>>sys.path.append("D:\Control\learning\SpectrometerCavityLock")
#>>>import spectrometer_cavity_lock
#>>>spectrometer_cavity_lock.setSetPoint(<value>)
#>>>spectrometer_cavity_lock.s.start_acquisition()
#>>>cutoff_wavelength = spectrometer_cavity_lock.s.cutoff_wavelength

import sys,__main__
from PyQt4 import QtGui
import time
import numpy as np
from time import sleep

from socket import gethostname
if gethostname()=="ph-photonbec":
	sys.path.append("D:\\Control\\PythonPackages\\")
	#sys.path.append("D:\\\Control\\SpectrometerCavityLock")
elif gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\\Multispec_server\\")

import multispec_server_gui
from multispec_runner import MultiSpectrometers
import pbec_ipc

if __name__=="__main__":
	qApp = QtGui.QApplication(sys.argv)

s = MultiSpectrometers() #The object that does the control
print "Runner started"
aw = multispec_server_gui.ApplicationWindow(s) #The main application GUI window. Knows about the stabiliser object.
print "GUI good"

def _start_stop_acquisition_button_pushed():
	aw.acquisition_running=not(aw.acquisition_running)
	if aw.acquisition_running:
		aw.start_stop_acquisition_button.setText("Stop\nAcquisition")
		#Now do the things you need to do
		print "Calling start_acquisition"
		s.start_acquisition()
		aw.sg.update_paused = False
	else:
		aw.start_stop_acquisition_button.setText("Start\nAcquisition")
		#Now do the things you need to do
		aw.sg.update_paused = True
		sleep(0.1) #Allow current update graph loop to finish before stopping acquistion
		aw.sg.thread_paused_override = True
		s.stop_acquisition()
	aw.start_stop_acquisition_button.update()

aw.start_stop_acquisition_button.pressed.connect(_start_stop_acquisition_button_pushed)


def _save_buffer_button_pressed():
	filename = "cavity_lock_data.txt"
	results = s.results[-spectrometer_cavity_lock_gui.plot_buffer_length:]
	fil = open(filename,"w")
	for r in results:
		fil.write(str(r))
		fil.write("\n")
	fil.close()
	
aw.save_buffer_button.pressed.connect(_save_buffer_button_pressed)

def _change_limits():
	for j,axes in enumerate(aw.sg.plots):
		for limit in [[aw.xmins, aw.sg.xmins],[aw.xmaxs, aw.sg.xmaxs],[aw.ymins, aw.sg.ymins],[aw.ymaxs, aw.sg.ymaxs]]:
			try:
				new_value = float(limit[0][j].text())
				limit[1][j] = new_value
			except:
				pass
		try:
			state = aw.logs[j].checkState()
			aw.sg.logscale[j] = state
		except:
			pass
		
	aw.sg.timer.stop()
	print "Stopped timer"
	aw.sg.compute_initial_figure()
	print "Computed figure"
	aw.sg.timer.start(aw.sg.update_time) #ms between updates	
	print "Restarted timer"
	
for limit in aw.xmins+aw.xmaxs+aw.ymins+aw.ymaxs:
	limit.returnPressed.connect(_change_limits)
for scale in aw.logs:
	scale.clicked.connect(_change_limits)

def _change_spec_settings():
	for j in range(s.num_spectrometers):
		try:
			new_int_time = float(aw.int_times[j].text())
			if new_int_time > s.min_spec_int_times[j]:
				print "setting new int time", new_int_time
				s.spec_int_times[j] = new_int_time
			else:
				print "Integration time too short for this spectrometer"
				print "Setting to minimum integration time."
				s.spec_int_times[j] = s.min_spec_int_times[j]
				aw.int_times[j].setText(str(s.min_spec_int_times[j]))
		except:
				pass
		try:
			new_n_average = int(float(aw.n_averages[j].text()))
			if new_n_average!=0:
				s.spec_n_averages[j] = new_n_average
				aw.n_averages[j].setText(str(new_n_average))
			else:
				print "Can't have zero averages"
		except:
			pass
	s.stop_acquisition()
	print "Stopped"
	s.start_acquisition()
	print "Started"
	
for int_time in aw.int_times+aw.n_averages:
	int_time.returnPressed.connect(_change_spec_settings)
	
aw.show()

#--------------------------------------------
#Now some functions for use when called as a package or via PBEC_IPC
def stopAcquisition(stop_lock=True):
	if aw.acquisition_running:
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
		aw.sg.timer.start(1)
			
def setSpectrometerIntegrationTime(newValue,spec_number,pause_lock=True):
	print "Hello"
	if newValue > s.min_spec_int_times[spec_number]:
		aw.int_times[spec_number].setText(str(newValue))
	else:
		aw.int_times[spec_number].setText(str(s.min_spec_int_times[spec_number]))
	_change_spec_settings()
	
	return None

def setSpectrometerNAverages(newValue,spec_number,pause_lock=True):
	print "Hello"
	newValue = int(newValue)
	aw.n_averages[spec_number].setText(str(newValue))
	_change_spec_settings()
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
		pbec_ipc.start_server(globals(), port = 47907)
		sys.exit(qApp.exec_())
	finally:
		for spectro in s.spectros:
			spectro.close(s.dll) #This might catch the errors.
		s.free_dll()

#MISSING: when application window is closed, stabiliser thread should also be stopped.

#EoF

