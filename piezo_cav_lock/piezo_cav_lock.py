#Automate human process of updating piezo to keep in voltage range of lock

from time import sleep
import sys
import smtplib
from getpass import getpass
import numpy as np

sys.path.append("D:\\Control\\PythonPackages\\")
import pbec_ipc
from pbec_analysis import make_timestamp

######### Parameters
piezo_port = pbec_ipc.PORT_NUMBERS["piezo_controller"]
piezo_host = 'localhost'
cavity_lock_port = pbec_ipc.PORT_NUMBERS["cavity_lock"]
cavity_lock_host = 'ph-photonbec3'


def read_lock_voltage():
	lock_volts = pbec_ipc.ipc_eval("s.Vout", host=cavity_lock_host, port=cavity_lock_port)
	return float(lock_volts)
	
def read_lock_mid_range_voltage():
	mindrange_volts = pbec_ipc.ipc_eval("s.control_offset", host=cavity_lock_host, port=cavity_lock_port)
	return float(mindrange_volts)

def read_lock_control_range_voltage():
	controlrange_volts = pbec_ipc.ipc_eval("s.control_range", host=cavity_lock_host, port=cavity_lock_port)
	first = float(controlrange_volts.split(",")[0][1:])
	second = float(controlrange_volts.split(",")[1][:-1])
	return [first, second]

def read_piezo_voltage():
	piezo_volts = pbec_ipc.ipc_eval("pzt_server.getZvolts()", host=piezo_host, port=piezo_port)
	return float(piezo_volts)
	
def set_piezo_voltage(v):	
	pbec_ipc.ipc_exec("piezo_gui_component.setZvolts("+str(v)+")", host=piezo_host, port=piezo_port)
	return 0

def find_internal_piezo_volts():
	gain = 7.43
	total_volts = read_piezo_voltage()
	lock_volts = read_lock_voltage()
	internal_piezo_volts = total_volts - gain*lock_volts
	return internal_piezo_volts



control_range_voltage = read_lock_control_range_voltage()
full_control_range = control_range_voltage[1] - control_range_voltage[0]
mid_range_voltage = read_lock_mid_range_voltage()
if np.abs(read_lock_voltage()-mid_range_voltage)>0.05:
	raise Exception('*** Put lock voltage at 0.5 V ***')

internal_piezo_volts = find_internal_piezo_volts()
set_piezo_voltage(v=internal_piezo_volts)

number_fatal_errors = 0
number_voltage_corrections = 0

while True:

	lock_volts = read_lock_voltage()

	if lock_volts < (mid_range_voltage - 0.25*full_control_range):
		if lock_volts < control_range_voltage[0] + 0.1*full_control_range:
			number_fatal_errors += 1
		print("Applying Piezo Correction")
		number_voltage_corrections += 1
		while lock_volts < mid_range_voltage:
			set_piezo_voltage(v=internal_piezo_volts)
			internal_piezo_volts += -0.01
			sleep(0.1)
			lock_volts = read_lock_voltage()

	elif lock_volts > (mid_range_voltage + 0.25*full_control_range):
		if lock_volts > control_range_voltage[1] - 0.1*full_control_range:
			number_fatal_errors += 1
		print("Applying Piezo Correction")
		number_voltage_corrections += 1
		while lock_volts > mid_range_voltage:
			set_piezo_voltage(v=internal_piezo_volts)
			internal_piezo_volts += 0.01
			sleep(0.1)
			lock_volts = read_lock_voltage()

	else:
		print("Cavity Lock Stable ({0} fatal errors and {1} voltage corrections)".format(number_fatal_errors, number_voltage_corrections))
	sleep(1)
			
			