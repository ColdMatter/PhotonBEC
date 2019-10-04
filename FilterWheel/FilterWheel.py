'''

	Class to work with ND Filter Wheel

	Written by: Joao Rodrigues
	Last Update 11th March 2019

	Check example.py for sample code.

'''

import numpy as np
import sys
import ctypes as ct
import os 

class FilterWheel():

	default_OD_setting = dict()
	default_OD_setting['position 1'] = 0.0
	default_OD_setting['position 2'] = 0.5
	default_OD_setting['position 3'] = 1.0
	default_OD_setting['position 4'] = 2.0
	default_OD_setting['position 5'] = 3.0
	default_OD_setting['position 6'] = 4.0


	def __init__(self, OD_setting=None, verbose=True, COM_port=None, reset_filter_wheel_flag=False, number_communication_trials=5):

		self.verbose = verbose
		self.current_position = None
		self.current_OD = None
		self.current_attenuation = None
		self.number_communication_trials = number_communication_trials

		if OD_setting is None:
			self.set_OD_setting(OD_setting=self.default_OD_setting)
		else:
			self.set_OD_setting(OD_setting=OD_setting)
		self.compute_attenuation_correspondence()

		if sys.platform == 'win32':
			dir_path = os.path.dirname(os.path.realpath(__file__))
			self.dll = ct.CDLL(dir_path+r'\uart_library.dll')

		if COM_port is None:
			raise Exception('COM Port not specified: Check Filter Wheel Software for help')
		else:
			self.COM_port = COM_port

		self.initiate_instrument(reset_filter_wheel_flag=reset_filter_wheel_flag)



	def estabilish_communication(self, func, *args):

		"""
			Tries multiple times to execute a communication with the filter wheel before raising an Exception.
			Any dll call should be wrapped by this function.

		"""

		communication_flag = False
		number_of_trials = 0
		while communication_flag is False and number_of_trials < self.number_communication_trials:
			try:
				func_return = func(*args)
				communication_flag = True
			except Exception as e:
				print('*** Error communication with the Filter Wheel:')
				print(e)
			number_of_trials += 1
		if communication_flag is False:
			raise Exception('*** Communication with the Filter Wheel failed... ***')

		return func_return



	def initiate_instrument(self, reset_filter_wheel_flag):

		'''

		'''

		self.serial_number = ct.create_string_buffer(b"", 256)
		status = self.estabilish_communication(self.dll.fnUART_LIBRARY_list, self.serial_number, ct.c_int(255))
		#status = self.dll.fnUART_LIBRARY_list(self.serial_number, ct.c_int(255))
		if status < 0:
			raise Exception('*** Error comunicating with Filter Wheel ***')
		self.port_handle = self.estabilish_communication(self.dll.fnUART_LIBRARY_open, ct.c_int(self.COM_port), ct.c_int(115200))
		#self.port_handle = self.dll.fnUART_LIBRARY_open(ct.c_int(self.COM_port), ct.c_int(115200))

		if not self.port_handle == 0:
			raise Exception('*** Error comunicating with Filter Wheel ***')
		elif self.port_handle == 0 and self.verbose is True:
			print('')
			print('    Communication with Filter Wheel succefully established')
			print('')

		if reset_filter_wheel_flag is True:
			self.reset_filter_wheel() 
			
		status = self.get_current_status()
		reply = ct.create_string_buffer(b'', 255)
		status = self.estabilish_communication(self.dll.fnUART_LIBRARY_Get, ct.create_string_buffer(b'*idn?\r'), reply)
		#status = self.dll.fnUART_LIBRARY_Get(ct.create_string_buffer(b'*idn?\r'), reply)
		wheel_id = str(repr(reply.value))[8:23]

		if status == 0:
			print('    Model is {0}'.format(wheel_id))
			print('    Current position is         {0}'.format(self.current_position))
			print('            optical density is  {0}'.format(self.current_OD))
			print('            attenuation is      {0}'.format(self.current_attenuation))
			print('')
		else:
			raise Exception('*** Error: Could not initiate filter wheel ***')


	def set_OD_setting(self, OD_setting=default_OD_setting):

		if not len(OD_setting.keys()) == 6:
			raise Exception('Invalid OD setting')
		else:
			self.OD_setting = OD_setting


	def get_current_status(self):

		communication_flag = False
		number_of_trials = 0
		while communication_flag is False and number_of_trials < self.number_communication_trials:
			try:
				reply = ct.create_string_buffer(b'', 255)
				status = self.estabilish_communication(self.dll.fnUART_LIBRARY_Get, ct.create_string_buffer(b'pos?\r'), reply)
				#status = self.dll.fnUART_LIBRARY_Get(ct.create_string_buffer(b'pos?\r'), reply)
				self.current_position = int(str(repr(reply.value))[7])
				communication_flag = True
			except Exception as e:
				print('*** Error grabbing the status of the Filter Wheel:')
				print(e)
			number_of_trials += 1
		if communication_flag is False:
			raise Exception('*** Communication with the Filter Wheel failed... ***')

		self.current_OD = self.OD_setting['position '+str(self.current_position)]
		self.current_attenuation = self.attenuation['position '+str(self.current_position)]

		return status


	def compute_attenuation_correspondence(self):

		self.attenuation = dict()
		for key in self.OD_setting.keys():
			self.attenuation[key] = 1 - 10**-self.OD_setting[key]

		self.table_attenuation = list()
		self.table_position_key = list()
		for key in self.OD_setting.keys():
			self.table_attenuation.append(float(1 - 10**-self.OD_setting[key]))
			self.table_position_key.append(key)



	def set_filter_position(self, position):

		self.estabilish_communication(self.dll.fnUART_LIBRARY_Set, ct.create_string_buffer(b'pos=' + str(position) + '\r'), ct.c_int(0))
		#self.dll.fnUART_LIBRARY_Set(ct.create_string_buffer(b'pos=' + str(position) + '\r'), ct.c_int(0))



	def reset_filter_wheel(self):

		''' 
			Sets filter wheel attenuation to zero (or the the lowest attenuation available at position 1)
		'''

		self.set_filter_position(position=1)



	def set_wheel_attenuation(self, optimal_attenuation, side_control='lower signal'):

		'''

			Sets the wheel attenuation. If the desired attenuation is not possible, searches the closest one, either
			from below or above, dependind on the side_control parameter.

			Parameters:
				optimal_attenuation (float)

				side_control (str) (default = 'lower signal'). If side_control is 'lower signal' the actual attenuation will be 
					higher than optimal_attenuation (if possible). If side_control is 'higher signal' the actual attenuation will be 
					lower than optimal_attenuation.

			Returns:
				attenuation_flag (bool) If False, derised attenuation could not be set. Only useful if side_control is 'lower signal'

		'''

		if side_control == 'lower signal':
			temp = np.array(self.table_attenuation, dtype=float) - optimal_attenuation
			signal = 1
		elif side_control == 'higher signal':
			temp = -(np.array(self.table_attenuation, dtype=float) - optimal_attenuation)
			signal = -1
		else:
			raise Exception('*** Error: Invalid side_control parameter ***')

		temp = temp[np.where(temp >= 0)[0]]
		try:
			choosen_attenuation = (signal * np.min(temp)) + optimal_attenuation
			attenuation_flag = True
		except:
			choosen_attenuation = np.max(self.table_attenuation)
			print('*** Warning: Desired attenuation levels could not be met ***')
			attenuation_flag = False
		choosen_position = self.table_position_key[np.where(np.array(self.table_attenuation) == choosen_attenuation)[0][0]]		

		if self.verbose is True:
			print('    Desired Attenuation = {0}'.format(optimal_attenuation))
			print('    Actual Attenuation  = {0} (at {1})'.format(choosen_attenuation, choosen_position))

		position_number = int(choosen_position[9])
		self.set_filter_position(position=position_number)

		status = self.get_current_status()
		
		return attenuation_flag


	def close_port(self):

		self.estabilish_communication(self.dll.fnUART_LIBRARY_close)
		#self.dll.fnUART_LIBRARY_close()


