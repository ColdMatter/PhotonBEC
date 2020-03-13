'''
Automate human process of updating piezo to keep in voltage range of lock:
Steps:
1) Initiate this script
2) Initiate lock as soon as possible (maybe not necessary to be as soon as possible)
'''

from time import sleep
import sys, __main__
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


#########
class CavityLockSecondLoop():

	def __init__(self, piezo_port, piezo_host, cavity_lock_port, cavity_lock_host):

		self.piezo_port = piezo_port
		self.piezo_host = piezo_host
		self.cavity_lock_port = cavity_lock_port
		self.cavity_lock_host = cavity_lock_host

		self.gain = 7.43
		self.control_range_voltage = self.read_lock_control_range_voltage()
		self.full_control_range = self.control_range_voltage[1] - self.control_range_voltage[0]
		self.mid_range_voltage = self.read_lock_mid_range_voltage()
		if np.abs(self.read_lock_voltage()-self.mid_range_voltage)>0.05:
			raise Exception('*** Put lock voltage at its mid-range, namely '+str(self.mid_range_voltage)+' V ***')
		self.internal_piezo_volts = self.find_internal_piezo_volts()
		self.set_piezo_voltage(v=self.internal_piezo_volts)
		self.number_fatal_errors = 0
		self.number_voltage_corrections = 0



	def read_lock_voltage(self):
		lock_volts = pbec_ipc.ipc_eval("s.Vout", host=self.cavity_lock_host, port=self.cavity_lock_port)
		return float(lock_volts)
	
	def read_lock_mid_range_voltage(self):
		mindrange_volts = pbec_ipc.ipc_eval("s.control_offset", host=self.cavity_lock_host, port=self.cavity_lock_port)
		return float(mindrange_volts)

	def read_lock_control_range_voltage(self):
		controlrange_volts = pbec_ipc.ipc_eval("s.control_range", host=self.cavity_lock_host, port=self.cavity_lock_port)
		first = float(controlrange_volts.split(",")[0][1:])
		second = float(controlrange_volts.split(",")[1][:-1])
		return [first, second]

	def read_piezo_voltage(self):
		piezo_volts = pbec_ipc.ipc_eval("pzt_server.getZvolts()", host=self.piezo_host, port=self.piezo_port)
		return float(piezo_volts)
	
	def set_piezo_voltage(self, v):	
		pbec_ipc.ipc_exec("piezo_gui_component.setZvolts("+str(v)+")", host=self.piezo_host, port=self.piezo_port)
		return 0

	def find_internal_piezo_volts(self):
		total_volts = self.read_piezo_voltage()
		lock_volts = self.read_lock_voltage()
		internal_piezo_volts = total_volts - self.gain*lock_volts
		return internal_piezo_volts

	def start_loop(self):

		while True:

			self.applying_correction_flag = False
			lock_volts = self.read_lock_voltage()

			if lock_volts < (self.mid_range_voltage - 0.35*self.full_control_range):
				self.applying_correction_flag = True
				if lock_volts < self.control_range_voltage[0] + 0.1*self.full_control_range:
					self.number_fatal_errors += 1
				print("Applying Piezo Correction")
				self.number_voltage_corrections += 1
				while lock_volts < (self.mid_range_voltage - 0.25*self.full_control_range):
					self.set_piezo_voltage(v=self.internal_piezo_volts)
					self.internal_piezo_volts += -0.01
					sleep(0.1)
					lock_volts = self.read_lock_voltage()

			elif lock_volts > (self.mid_range_voltage + 0.35*self.full_control_range):
				self.applying_correction_flag = True
				if lock_volts > self.control_range_voltage[1] - 0.1*self.full_control_range:
					self.number_fatal_errors += 1
				print("Applying Piezo Correction")
				self.number_voltage_corrections += 1
				while lock_volts > (self.mid_range_voltage + 0.25*self.full_control_range):
					self.set_piezo_voltage(v=self.internal_piezo_volts)
					self.internal_piezo_volts += 0.01
					sleep(0.1)
					lock_volts = self.read_lock_voltage()

			else:
				self.applying_correction_flag = False
				print("Cavity Lock Stable ({0} fatal errors and {1} voltage corrections)".format(self.number_fatal_errors, self.number_voltage_corrections))
			sleep(1)
			
			

second_loop = CavityLockSecondLoop(piezo_port=piezo_port, piezo_host=piezo_host, cavity_lock_port=cavity_lock_port, cavity_lock_host=cavity_lock_host)


def is_second_cavity_lock_loop_activated():
	return second_loop.applying_correction_flag


if __name__=="__main__":
	try:
		pbec_ipc.start_server(globals(), port=pbec_ipc.PORT_NUMBERS["cavity lock second loop"])
		second_loop.start_loop()
	finally:
		pass
