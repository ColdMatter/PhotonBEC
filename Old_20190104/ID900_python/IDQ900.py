import sys
import zmq
from zmq.error import ZMQError
from socket import gethostname
if gethostname().lower() == "ph-photonbec3":
	sys.path.append("D:/Control/PythonPackages/")

#from ctypes import *
from pylab import *
import time, traceback
import numpy
from scipy.misc import imsave
from time import sleep
from pbec_analysis import *
#For saving of the data
import h5py, zipfile, io

#if gethostname().lower() in ["ph-photonbec","ph-photonbec2", "ph-photonbec3"]:
#	libtdcdir = "C:/Program Files (x86)/IDQ/IDQtdc/userlib/lib/"
#	libtdcbase = WinDLL(libtdcdir+"tdcbase.dll") 
#elif gethostname().lower()== "ph-rnyman":
#	libtdcdir = "../IDQtdc-LX64-16_05_09/userlib/lib/"
#	libtdcbase = CDLL(libtdcdir+"libtdcbase.so")

#libtdcbase.TDC_perror.restype = c_char_p	
exposure_timebase = 1e-3
id900_host = "169.254.99.143"
id900_port = "5555"
ch1_port = "4242"
#id900_host = "localhost"
#id900_port = "6666"
address = "tcp://"+id900_host+":"+id900_port
address2 = "tcp://"+id900_host+":"+ch1_port

class CorrelatorControl(object):
	"""
	Connects to our IDQ Time to Digital Converter over USB. 
	"""
	instance = None
	
	def __new__(self, *args, **kwargs):
		if not self.instance: 
			self.instance = super(CorrelatorControl, self).__new__(self, *args, **kwargs)
		return self.instance
	def __init__(self,do_setup=True,mode="HIRES"):
		self.errors=[]
		self.is_initialised = False
		if do_setup:
			self.setup(mode=mode)
		#self.timebase = self._getTimebase_()
		#self.data = CorrelatorData(ts)
		self.buffer_size=None
	def setup(self,mode):
		if not(self.is_initialised):
			context = zmq.Context()
			self.tc = context.socket(zmq.REQ)
			self.tc.connect(address)
			self.tc2 = context.socket(zmq.REQ)
			self.tc2.connect(address2)
			self.setMeasureMode(1,"LOWRES")
		else:
			print "Already initialised"		
	def writeCommand(self,mesg):
		try:
			self.tc.send(mesg)
			dump = self.receive()
			print dump
		except ZMQError:
			print "Looks like you haven't read the previous output, which was:"
			self.receive()
			try:
				print "Now that we've received, let's send"
				self.tc.send(mesg)
				dump = self.receive()
			except ZMQError:
				print "Don't know why you still get a ZMQ Error"
		return dump
	def receive(self):
		try:
			mesg = self.tc.recv()
		except ZMQError:
			"Looks like you've already received"
			mesg = None
		return mesg
	def writeCommand2(self,mesg):
		try:
			self.tc2.send(mesg)
			dump = self.receive()
			print dump
		except ZMQError:
			print "Looks like you haven't read the previous output, which was:"
			self.receive()
			try:
				print "Now that we've received, let's send"
				self.tc2.send(mesg)
				dump = self.receive()
			except ZMQError:
				print "Don't know why you still get a ZMQ Error"
		return dump
	def receive2(self):
		try:
			mesg = self.tc2.recv()
		except ZMQError:
			"Looks like you've already received"
			mesg = None
		return mesg
	def enableChannels(self, channels):
		for i in channels:
			self.writeCommand("Input"+str(i)+":ENABLE")
	def disableChannels(self, channels):
		for i in channels:
			self.writeCommand("Input"+str(i)+":ENABLE OFF")
	def setMeasureMode(self,ch,mode):
		self.measuremode = mode
		self.writeCommand("sens"+str(ch)+":mode "+self.measuremode)
	def setDelay(self,ch,delay):
		self.delay = delay
		self.writeCommand("input"+str(ch)+":delay "+str(self.delay))
	def setDataMode(self,ch,mode):
		self.datamode = mode
		self.writeCommand("tsst"+str(ch)+":mode "+self.datamode)
	def setBinWidth(self,ch,width):
		self.binwidth = width
		self.writeCommand("tsst"+str(ch)+":configuration:histogram:bwidth "+str(self.binwidth)+"TB")
	def setBinCount(self,ch,count):
		self.bincount = count
		self.writeCommand("tsst"+str(ch)+":configuration:histogram:bcount "+str(self.bincount))
	def getHistogram(self,ch):
		self.histogram = eval(self.writeCommand("tsst"+str(ch)+":data:histogram?"))
	def getChannelCounts(self,ch):
		self.channelcounts = eval(self.writeCommand("tsst"+str(ch)+":data:counter?"))
#	def err_msg(self,err_num):
#		if err_num!=0:
#			self.errors.append(err_num)
#			print "IQD-TDC error "+str(err_num)+": "+libtdcbase.TDC_perror(c_int(err_num))	
'''
	def _getTimebase_(self):
		#!!!
		return timebase
	def configureSelfTest(self,value,selftest_timebase = 20e-9):
		#!!!
	def setExposureTime(self,exposure_time = 1.0):
		#!!!
'''	
'''
	def setTimestampBufferSize(self,buf_siz = 2e4):
		#!!!
		if buf_siz!=0:
	def getTimestampBufferSize(self):
		#!!!!
		return buffer_size
	
	def getLastTimeStamps(self, exposure_time=1,reset=c_bool(False),get_raw_timestamps=False):
		#!!!
		timestamps=array([ts*timebase for ts in raw_timestamps])
		channels=array([ch for ch in raw_channels])
		if get_raw_timestamps:
			return raw_timestamps,channels
		else:
			return timestamps,channels
	def _getTimestampBufferSize(self,size,buffer_size=c_int32(0)):
		#!!!
		return buffersize
	def selftest(self):
		#Set into selftest mode
		if not(self.is_initialised):
			self.setup()
			print("-----------")
		try:
		#!!!
		except:
			pass
	def close(self):
		#!!!
		if not err_num:
			self.is_initialised=False
		else:
			pass
'''
	
#execfile("Correlator.py")
#EoF
