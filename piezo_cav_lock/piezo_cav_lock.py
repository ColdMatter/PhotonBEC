#Automate human process of updating piezo to keep in voltage range of lock

from time import sleep
import sys
import smtplib
from getpass import getpass
import numpy as np

sys.path.append("D:\\Control\\PythonPackages\\")
import pbec_ipc
from pbec_analysis import make_timestamp

fromAddr = 'photonbec@gmail.com'
#pw = getpass('Type password for ' + fromAddr + ':')
toAddr = 'photonbec@gmail.com'
text='Cavity lock hit the rail'

piezo_port = pbec_ipc.PORT_NUMBERS["piezo_controller"]
piezo_host = 'localhost'
cavity_lock_port = pbec_ipc.PORT_NUMBERS["cavity_lock"]
cavity_lock_host = 'ph-photonbec4'


def read_lock_voltage():
	lock_volts = pbec_ipc.ipc_eval("s.Vout", host=cavity_lock_host, port=cavity_lock_port)
	return float(lock_volts)
	
def read_piezo_voltage():
	piezo_volts = pbec_ipc.ipc_eval("pzt_server.getYvolts()", host=piezo_host, port=piezo_port)
	return float(piezo_volts)
	
def set_piezo_voltage(v):	
	pbec_ipc.ipc_exec("piezo_gui_component.setYvolts("+str(v)+")", host=piezo_host, port=piezo_port)
	return 0
	
def send_hit_rail_email():
	print
	'''
	ts = make_timestamp()
	message = 'From: ' + fromAddr + '\r\nTo:' + toAddr + '\r\nSubject:' + ts + '\r\n\r\n'+text
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	server.set_debuglevel(1)
	server.login(fromAddr, pw)
	server.sendmail(fromAddr, toAddr, message)
	server.quit()
	'''

def find_internal_piezo_volts():
	gain = 7.43
	total_volts = read_piezo_voltage()
	lock_volts = read_lock_voltage()
	internal_piezo_volts = total_volts - gain*lock_volts
	return internal_piezo_volts


if np.abs(read_lock_voltage()-0.5)>0.05:
	raise Exception('*** Put lock voltage at 0.5 V ***')

internal_piezo_volts = find_internal_piezo_volts()
#To be sure
set_piezo_voltage(v=internal_piezo_volts)

number_fatal_errors = 0
number_voltage_corrections = 0

while True:
	lock_volts = read_lock_voltage()
	#piezo_volts = read_piezo_voltage() #Slow step for some reason...
	#true_piezo_volts = piezo_volts - 10*lock_volts #read and set have different conventions on whether they do or don't include the DAQ voltage
	if lock_volts < 0.350:
		if lock_volts<0.1:
			send_hit_rail_email()
			number_fatal_errors += 1
		print("Applying Piezo Correction")
		number_voltage_corrections += 1
		while lock_volts < 0.5:
			#set_piezo_voltage(v=true_piezo_volts)
			#true_piezo_volts += -0.01
			set_piezo_voltage(v=internal_piezo_volts)
			internal_piezo_volts += -0.01
			sleep(0.5)
			lock_volts = read_lock_voltage()
	elif lock_volts > 0.650:
		if lock_volts>0.9:
			send_hit_rail_email()
			number_fatal_errors += 1
		print("Applying Piezo Correction")
		number_voltage_corrections += 1
		while lock_volts > 0.5:
			#set_piezo_voltage(v=true_piezo_volts)
			#true_piezo_volts += 0.01
			set_piezo_voltage(v=internal_piezo_volts)
			internal_piezo_volts += 0.01
			sleep(0.5)
			lock_volts = read_lock_voltage()
	else:
		print("Cavity Lock Stable ({0} fatal errors and {1} voltage corrections)".format(number_fatal_errors, number_voltage_corrections))
	sleep(1)
			
			