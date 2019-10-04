

import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import SingleChannelAO
import tektronix


#pixels where the height is the data
#background is where there isnt data
#time scale must be 500ns per square
pulse_range = (330, 470)
background_range = (0, 150)

#see lab book 31/8/2016
T = 48
R = 232
S = 0.22

MAX_SCOPE_READING = 255

def set_AOM_amplitude(a):
	'''function for easier naming / thinking'''
	print 'setting aom amplitude to ' + str(a)
	SingleChannelAO.SetAO0(a)

class LaserPowerReader(object):

	def __init__(self):
		self.scale = 0
		self.conversion_values = None
		self.tek = tektronix.Tektronix(binary=True)
		self.tek.setChannel(chan=1)
		self.tek.setDataRange(1200, 2000)
		
	def get_laser_power(self, estimate_mW=10):

		high_threshold = 250
		low_threshold = 100
	
		##see lab book 31/8/16
		y_max = 245
		self.conversion_values = self.tek.get_voltage_conversion_values()
		#initial estimate
		scale = ((estimate_mW*S*R)/T - self.conversion_values[2]) / (y_max - self.conversion_values[0]) / 25.0
		
		while True:
			self.tek.setVoltageScale(1, scale)
			y_data = self.tek.getRawChannelDataAsString()
			y_data = array([ord(d) for d in y_data])
			y_reading = mean(y_data[pulse_range[0] : pulse_range[1]])
			print 'scale = ' + str(scale) + ' -->  y_reading = ' + str(y_reading)
			if y_reading > high_threshold:
				scale *= 3.0/4.0
				continue
			elif y_reading < low_threshold:
				scale = scale * 4.0 / 3.0
				continue
			break
		
		
		data = self.tek.convert_raw_data_to_volts(y_reading, self.tek.get_voltage_conversion_values())
		data = data*T/S/R #data is in power now
		

		reading = data
		return reading*1e3
	
lpr = LaserPowerReader()
print lpr.get_laser_power(5)
'''	
amplitude_range = linspace(0, 1.5, 101) #taken from original calibrate_AOM_amplitude.py
for a in amplitude_range:
	set_AOM_amplitude(a)
	v = read_pd_voltage_average(N = 1, sleep_time = 1)
'''