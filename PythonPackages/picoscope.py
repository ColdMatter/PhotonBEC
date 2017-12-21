'''
A class and some utilities for high-level work with the PicoScope 6407
Written by Rob Nyman, December 2017

Some example code:
---------------------------------------
import picoscope
scope = picoscope.Picoscope6407(open_device=True)
scope.set_active_channels(["B","C"])
scope.set_trigger("C",0.0) #trigger-channel label and fractional trigger value
scope.initialise_measurement(samples=int(1e3))
scope.acquire_and_readout(timebase=2) #see documentation for meaning. Small means short.

figure(1),clf()
for c in sorted(scope.active_channels):
	plot(1e9*scope.time_axis,1e3*scope.data[c],".--",label=c)

xlabel("time (ns)"),ylabel("signal (mV)")
xlim(0,500),grid(1),legend()
---------------------------------------
'''

from picosdk import ps6000
import time
from numpy import copy,array,linspace,float32

#--------------------------
#UTILITIES
#--------------------------
def time_per_sample(timebase):
	'''
	Go look in the programmer's manual, p17 for the explanation
	REMAINING ISSUE: timebase<2 gives PICO_INVALID_TIMEBASE error
	That means the minimum sample interval is 800 ps NOT the 350 ps we were expecting.
	'''
	if 0 <= timebase <= 4:
		sample_interval = 2**timebase / 5.0e9
	elif 5 <= timebase < 2**32:
		#INCONSISTENT DOCUMENTATION: maybe they mean 2**30 NOT 2**32 for the limit
		sample_interval = (timebase-4.0) / 156250000
	else:
		sample_interval = nan
	return sample_interval

class _Singleton(object):
	'''
	This class is needed to ensure there is only one of any class that inherits from it
	'''
	def __new__(cls, *args, **kwds):
			it = cls.__dict__.get("__it__")
			if it is not None:
				return it
			cls.__it__ = it = object.__new__(cls)
			it.init(*args, **kwds)
			return it
	def init(self, *args, **kwds):
		pass


#--------------------------
#THE MAIN OSCILLOSCOPE CLASS
#--------------------------
class Picoscope6407(_Singleton):
	'''
	Makes a Picoscope6407 high-level object. 
	Inheritance from _Singleton class ensures that there is only ever one instance
	'''
	def __init__(self,open_device = True):
		#Try not to re-initialised every time someone attempts to re-instantiate this singleton
		try:
			self._was_initialised
			#print "Picoscope6407 warning: please don't try to re-instantiate the Picoscope6407"
		except:
			self.ps = ps6000.Device() #NOTE: "ps" is the lower-level device object
			self.status = None
			if open_device: 
				self.open()
			self.active_channels = {} #TODO: implement this bit
			self._was_initialised = True
			self.samples = int(1e5)
			self.timebase = 2
			self.trigger_source = None
			self.trigger_threshold = 0.0
			self.data = {}
			self._indices = {}
			self.time_axis = array([])
	
	def _handle_errors(self):
		if self.status != 0: 
			prefix = "Picoscope6407:\t"
			try:
				print prefix+ self.ps.m.pico_tag(self.status)
			except:
				print prefix+"print_status: Something went wrong calling ps.m.picotag()"
		
	def is_open(self):
		return self.ps._handle != 0
	
	def open(self):
		if not(self.is_open()):
				self.status = self.ps.open_unit()
				self._handle_errors()

	def close(self):
		self.ps.close_unit()
	
	def set_active_channels(self,channels_to_activate=[]):
		'''
		channel_settings must have a values "A","B","C" or "D" 
		for each of the channels you wish to be active
		'''
		#TODO: Make use of the channel settings, passable as arguments
		self.open()#might be needed!
		self.active_channels = {}
		for c in channels_to_activate:
			channel = self.ps.m.Channels.__dict__[c] #WRONG WAY ROUND!
			state = self.ps.m.ChannelState()
			state.enabled=True
			state.coupling = self.ps.m.Couplings.dc50 #dc50 Ohms is only allowed value for 6407
			state.range = self.ps.m.Ranges.r100mv #100mV is the only allowed range for the 6407
			self.status = self.ps.set_channel(channel, state) 
			self._handle_errors()
			self.active_channels.update({c:channel})
		
	def set_trigger(self, source, threshold):
		'''
		Give a letter for the trigger source channel.
		The threshold is a fraction of the total signal, I think.
		'''
		self.open()#might be needed!
		enabled = True
		self.trigger_source = source #a string, "A" or "B" or "C" or "D"
		self.trigger_threshold = threshold
		direction = 0
		if source in self.active_channels:
			self.status = self.ps.set_simple_trigger(enabled, self.active_channels[source], threshold, direction,delay=0,waitfor=0)
			self._handle_errors()

		else:
			print "Picoscope6407 warning: trigger source not in active channels"
	
	def initialise_measurement(self,samples=int(1e5),segment=0):
		#this is all the buffer stuff
		self.open()#might be needed!
		self.segment = segment #between 1 and 1 million. Right now, we need one per channel, I think
		if type(samples)!=type(int(10)):
			print "Picoscope6407 warning: converting sample number to an integer"
		self.samples = int(samples) #transfer gets slow when you reach 10 million samples or more. 
		#Also, in 32 bit python more than ~3e7 float samples breaks memory
		self._indices = {}
		mode = self.ps.m.RatioModes.raw
		for c,channel in self.active_channels.iteritems():
			self.status, index = self.ps.locate_buffer(channel,self.samples,self.segment,mode=mode,downsample=0)
			self._handle_errors()
			self._indices.update({c:index})

	def _set_time_axis(self):
		tmin = 0 #trigger offsets may need to be handled properly at some point
		tmax = tmin + self.samples*time_per_sample(self.timebase)
		self.time_axis = linspace(tmin, tmax, self.samples, dtype=float32)

	def acquire_and_readout(self,timebase=2):
		'''
		Set the device into BLOCK mode, run and read out the data, just the once.
		'''
		self.open()#might be needed!
		self.timebase = timebase #at least "2" please. Must be integer.
		interval = time_per_sample(self.timebase) * self.samples * 1e9 #in nanoseconds
		self.status = self.ps.collect_segment(self.segment, interval, timebase=self.timebase)
		self._handle_errors()

		self.data = {}
		for c,index in self._indices.iteritems():
			self.status, these_data = self.ps.get_buffer_volts(index)
			self._handle_errors()
			self.data.update({c:copy(these_data)})
		
		self._set_time_axis()

	def stop_measurement(self):
		self.open()#might be needed!
		status = self.ps.stop() #I'm not sure how useful this bit really is
		self._handle_errors()

	
if __name__ == "__main__":
	import picoscope
	scope = picoscope.Picoscope6407(open_device=True)
	scope.set_active_channels(["B","C"])
	scope.set_trigger("C",0.0) #trigger-channel label and fractional trigger value
	scope.initialise_measurement(samples=int(1e3))
	scope.acquire_and_readout(timebase=2) #see documentation for meaning. Small means short.

	figure(1),clf()
	for c in sorted(scope.active_channels):
		plot(1e9*scope.time_axis,1e3*scope.data[c],".--",label=c)

	xlabel("time (ns)"),ylabel("signal (mV)")
	xlim(0,500),grid(1),legend()
#EoF 