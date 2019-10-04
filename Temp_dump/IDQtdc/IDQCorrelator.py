import sys
from socket import gethostname
if gethostname().lower() == "ph-photonbec3":
	sys.path.append("D:/Control/PythonPackages/")

from ctypes import *
from pylab import *
import time, traceback
import numpy
from scipy.misc import imsave
from time import sleep
from pbec_analysis import *
#For saving of the data
import h5py, zipfile, io

if gethostname().lower() in ["ph-photonbec","ph-photonbec2", "ph-photonbec3"]:
	libtdcdir = "C:/Program Files (x86)/IDQ/IDQtdc/userlib/lib/"
	libtdcbase = WinDLL(libtdcdir+"tdcbase.dll") 
elif gethostname().lower()== "ph-rnyman":
	libtdcdir = "../IDQtdc-LX64-16_05_09/userlib/lib/"
	libtdcbase = CDLL(libtdcdir+"libtdcbase.so")

libtdcbase.TDC_perror.restype = c_char_p	
exposure_timebase = 1e-3 


class CorrelatorControl(object):
	"""
	Connects to our IDQ Time to Digital Converter over USB. 
	"""
	instance = None
	
	def __new__(self, *args, **kwargs):
		if not self.instance: 
			self.instance = super(CorrelatorControl, self).__new__(self, *args, **kwargs)
		return self.instance
	def __init__(self,do_setup=True):
		self.errors=[]
		self.is_initialised = False
		if do_setup:
			self.setup()
		self.timebase = self._getTimebase_()
		#self.data = CorrelatorData(ts)
		self.buffer_size=None
	def setup(self):
		if not(self.is_initialised):
			err_num = libtdcbase.TDC_init(c_int(-1))
			self.err_msg(err_num)
			if not(err_num):
				self.is_initialised=True
		else:
			print "Already initialised"		
	def err_msg(self,err_num):
		if err_num!=0:
			self.errors.append(err_num)
			print "IQD-TDC error "+str(err_num)+": "+libtdcbase.TDC_perror(c_int(err_num))	
	def _getTimebase_(self):
		libtdcbase.TDC_getTimebase.restype=c_double
		timebase = libtdcbase.TDC_getTimebase() 
		return timebase
	def configureSelfTest(self,value,selftest_timebase = 20e-9):
		#range=?????
		self.err_msg(libtdcbase.TDC_configureSelfTest( c_int(value) ))
		#self.lastSelftestTimebase=value
	def setExposureTime(self,exposure_time = 1.0):
		#range=?????
		self.err_msg(libtdcbase.TDC_setExposureTime( c_int(int(exposure_time/exposure_timebase)) ))
		#self.lastExposureTime=value
	def enableChannels(self, channel_mask = c_int32(3)):
		#binary by channels, e.g. 00000101 means activate channels 1 and 3
		#Therfore "3" means activate channels 1 and 2	
		self.err_msg(libtdcbase.TDC_enableChannels( channel_mask ))
		#self.lastChannelMask=c_int32(value)
	def setTimestampBufferSize(self,buf_siz = 2e4):
		self.buffer_size=c_int32(int(buf_siz))
		##buffer_size=c_int32(int(buf_siz))
		if buf_siz!=0:
			self.err_msg(libtdcbase.TDC_setTimestampBufferSize(self.buffer_size))
	def getTimestampBufferSize(self):
		buffer_size=c_int32(int(0))
		self.err_msg(libtdcbase.TDC_getTimestampBufferSize(byref(buffer_size)))
		return buffer_size
	
	def getLastTimeStamps(self, exposure_time=1,reset=c_bool(False),get_raw_timestamps=False):
		valid = c_int(0)
		sleep(exposure_time*1.3) #Magic number programming!
		raw_timestamps=(c_int64 * self.buffer_size.value)()
		raw_channels=(c_int8*self.buffer_size.value)()
		self.err_msg(libtdcbase.TDC_getLastTimestamps(reset,byref(raw_timestamps),byref(raw_channels),byref(valid)))
		timebase=libtdcbase.TDC_getTimebase()
		timestamps=array([ts*timebase for ts in raw_timestamps])
		channels=array([ch for ch in raw_channels])
		if get_raw_timestamps:
			return raw_timestamps,channels
		else:
			return timestamps,channels
	def _getTimestampBufferSize(self,size,buffer_size=c_int32(0)):
		libtdcbase.TDC_getTimestampBufferSize.restype=c_double
		buffersize=libtdcbase.TDC_getTimestampBufferSize(byref(buffer_size))
		return buffersize
	def selftest(self):
		#Set into selftest mode
		if not(self.is_initialised):
			self.setup()
			print("-----------")
		try:
			period=c_int(int(1e-6/selftest_timebase))
			burstDist=c_int(int(15e-6/selftest_timebase))
			burstSize=c_int(7)
			self.err_msg(libtdcbase.TDC_configureSelftest(channel_mask,period,burstSize,burstDist))
		except:
			pass
	def close(self):
		err_num=libtdcbase.TDC_deInit()
		self.err_msg(err_num)
		if not err_num:
			self.is_initialised=False
		else:
			pass

	
#execfile("Correlator.py")
#EoF