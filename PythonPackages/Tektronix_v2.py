import numpy as np
import visa
from struct import unpack


class TektronixScope():

	'''
		
		Written by  : Joao Rodrigues
		Last Update : Feb 12th 2019
	
		Sample Code:
				
			import matplotlib.pyplot as plt
			import numpy as np

			from Tektronix_v2 import TektronixScope

			# initializes the scope object
			myscope = TektronixScope(scope_number=1, channel_number=1)

			# sets the communication timeout 
			myscope.set_timeout(timeout=10000)

			# sets the number of time points to acquire
			myscope.set_horizontal_record_length(record_length=10000)
			print("Number of points = ", myscope.get_horizontal_record_length())

			# Grabs one reading
			time, voltage = myscope.read_data_single_channel()

			# Plots
			time = time * 1e6
			plt.plot(time,voltage)
			plt.xlabel("Time (microseconds)")
			plt.ylabel("Signal (Volts)")
			plt.show()		
	
	'''

	def __init__(self, scope_number=1, channel_number=1):

		"""
			The acquisition parameters are those set in the instrument (actual physical instrument)
		
			Parameters: 
				- scope_number (int) (default = 1) : Number of the scope (only address for scope 1 is implemented)
				- channel_number (int) (default = 1) : Channel to grab data from. Only one channel at a time can be used
				
			Return: 
				None
			
		"""

	
		# Creates a resource manager object
		self.rm = visa.ResourceManager()
		
		# Scope Address
		if scope_number == 1:
			scope_name = "USB::0x0699::0x0368::C010521"
		elif scope_number is None:
			pass
		else:
			raise Exception("Unknown Scope")
			
		# Opens the scope
		if scope_number is not None:
			self.scope = self.rm.open_resource(resource_name=scope_name)
			self.set_timeout()
			self.set_data_source(channel_number=channel_number)
			
		# Auxiliary attributes
		self.screen_parameters = False
		
			
		
	##### Generic and Misc methods
	
	# Lists all resources available via VISA
	def list_resources(self):
		resource_list = self.rm.list_resources()
		print("Available VISA Resources:")
		print(resource_list)
	
	# Sets the timeout of the scope (miliseconds)
	def set_timeout(self, timeout=10000):
		self.scope.timeout = timeout
		
	# Resets the screen parameters (necessary if user changes parameters in the oscilloscope)
	def reset_screen_parameters(self):
		self.screen_parameters = False
	
	
	
	##### USB Communication methods
	
	def write(self, command):
		return self.scope.write(command)
		
	def ask(self, command):
		return self.scope.ask(command)
	
	def read_raw(self):
		return self.scope.read_raw()
	

	
	##### Scope Get Methods
  
	def get_horizontal_record_length(self):
		return int(self.ask("horizontal:recordlength?"))
    
	def get_out_waveform_horizontal_sampling_interval(self):
		return float(self.ask('WFMPRE:XINC?'))		
		
	def get_out_waveform_horizontal_zero(self):
		return float(self.ask('WFMPRE:XZERO?'))
		
	def get_out_waveform_vertical_scale_factor(self):
		return float(self.ask('WFMPRE:YMUlt?'))
		
	def get_out_waveform_vertical_position(self):
		return float(self.ask('WFMPRE:YOFf?'))
		
	def get_out_waveform_vertical_zero(self):
		return float(self.ask('WFMPRE:YZERO?'))
		
			
			
	##### Scope Set Methods
	
	def set_data_source(self, channel_number):
		name = 'CH' + str(channel_number)
		self.write(command='DATA:SOU '+name)
		
	def set_horizontal_record_length(self, record_length): ############## Not available for TBS1000 Series (value is always 2500)
		self.write('HORizontal:RECOrdlength '+str(record_length))
	
	
	
	##### Data Acquisition Methods
	
	def read_data_single_channel(self):
		
		"""
			Parameters:
				
			Return: 
					Returns a dict with keys 'time' and 'voltage'
						- time (numpy array) : time axis, in seconds
						- voltage (numpy array) : voltage, in volts
			
		"""
		
		# Prelude (don't know exactly what it means)
		self.write(command = 'DATA:WIDTH 1')
		self.write(command = 'DATA:ENC RPB')

		# Gets screen parameters
		if self.screen_parameters is False:
			self.ymult = self.get_out_waveform_vertical_scale_factor()
			self.yzero = self.get_out_waveform_vertical_zero()
			self.yoff = self.get_out_waveform_vertical_position()
			self.xincr = self.get_out_waveform_horizontal_sampling_interval()
			self.screen_parameters = True
		

		# Grabs data from scope
		self.write('CURVE?')
		data = self.read_raw()
		headerlen = 2 + int(data[1])
		header = data[:headerlen]
		ADC_wave = data[headerlen:-1]
		ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))
		
		# creates the voltage and time values
		voltage_axis = (ADC_wave - self.yoff) * self.ymult  + self.yzero
		time_axis = np.arange(0, self.xincr * len(voltage_axis), self.xincr)

		# creates the dict
		scope_reading = dict()
		scope_reading['time'] = np.squeeze(time_axis)
		scope_reading['voltage'] = np.squeeze(voltage_axis)
		
		# return
		return scope_reading
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		