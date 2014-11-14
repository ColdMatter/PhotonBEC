#execfile("pi_controller.py")
class PI_control():
	def __init__(self,buffer_length=5,set_point=50,P_gain=1.,I_gain=1.,control_range=(0.0,0.2)):
		self.timestamps=[]
		self.measured_values=[]
		self.error_values=[]
		self.control_values=[]
		self.buffer_length=buffer_length
		self.set_point=set_point #rather arbitrary
		self.P_gain=P_gain
		self.I_gain=I_gain #needs units of 1./time. Sort of
		self.control_range=control_range #min and max acceptable values of output
	def set_set_point(set_point=50):
		self.set_point=set_point
	def proportional(self):
		if len(self.error_values)==0:
			prop = 0.0
		else:
			prop= self.error_values[-1]*self.P_gain #uses only most recent error value
		return prop
	def integral(self):
		#uses all un-weighted error values in buffer, regardless of current buffer length
		#Net integral gain is effectively buffer_length*I_gain
		return sum(self.error_values)*self.I_gain 
	def control_value(self):
		cv = self.proportional() + self.integral()
		cv_min,cv_max=self.control_range
		cv=min(max(cv_min,cv),cv_max)
		return cv
	def update(self,timestamp,measured_value):
		#Also: update control_values and error_values appropriately, once I know how to calculate P and I
		#Can try to take account of bandwidth by using timestamps too. Timestamps need at least 2 decimal places
		error_value = measured_value - self.set_point
		if len(self.timestamps)==self.buffer_length:
			for attr in [self.timestamps,self.measured_values,self.error_values,self.control_values]:
				a=attr.pop(0)
		self.timestamps.append(timestamp)
		self.measured_values.append(measured_value)
		self.error_values.append(error_value) #takes into account the changing of set points in the past
		self.control_values.append(self.control_value())

#----------------------
#TESTING
"""
from pbec_analysis import make_timestamp
pic = PI_control(P_gain=-0.001,I_gain=-0.001)
#pic = PI_control()
pic.update(make_timestamp(),5)		
pic.update(make_timestamp(),6)		
pic.update(make_timestamp(),7)		
pic.update(make_timestamp(),8)		
#print pic.timestamps, pic.error_values
pic.update(make_timestamp(),9)
pic.update(make_timestamp(),10)
pic.update(make_timestamp(),11)
#print pic.timestamps, pic.error_values
print pic.control_values
"""
#EoF