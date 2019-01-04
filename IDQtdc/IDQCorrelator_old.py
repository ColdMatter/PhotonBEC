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

if gethostname().lower() in ["ph-photonbec2", "ph-photonbec3"]:
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


class CorrelatorData(ExperimentalData):
	def __init__(self, ts=None, extension='_correlator.hdf5',data=None):
		ExperimentalData.__init__(self, ts, extension,data=data)
	def setData(self, data):
		if data !=None:
			timestamps, channels = data
			self.timestamps = timestamps
			self.channels = channels
		else:
			self.timestamps = None
			self.channels = None
	def saveData(self):
		#TODO: save into  into a more compressed format: ZIP or FITS
		filename = self.getFileName(make_folder=True)
		fil = open(filename,"w")
		fil.write("timestamps, channels\n")
		timestamps=self.timestamps
		channels=self.channels
		fil.write(str(list(timestamps))+"\n")
		fil.write(str(list(channels))+"\n")
		fil.close()
		#imsave(filename, self.data)
	def loadData(self, load_params):
		#TODO: compatibility with more compressed format
		filename = self.getFileName()
		temp = open(filename,"r")
		temp.readline()
		timestamps = np.asarray(eval(temp.readline()))
		channels = np.asarray(eval(temp.readline()))
		#self.data = imread(filename)
	def copy(self):
		d = CorrelatorData(self.ts)
		d.timestamps = self.timestamps.copy()
		d.channels = self.channels.copy()
		return d
	def getHistogram(self, trigger_channel=0,signal_channel=1):
		#channels=where((self.channels==trigger_channel) or (self.channels==signal_channel))[0][1:]
		#channels=where(self.channels in [trigger_channel, signal_channel])[0][1:]
		is_usable_channel = [(c in [trigger_channel,signal_channel]) for c in self.channels]
		channels=where(is_usable_channel)[0][1:]
		timestamps_filtered=(self.timestamps)[channels]
		channel_trigger=where(self.channels==trigger_channel)[0][1:]
		timestamp_blocks=split(timestamps_filtered,channel_trigger)
		timestamp_blocks_signal = [a[1:] if len(a)>2 else [] for a in timestamp_blocks ] #TODO: check this logic really is correct
		trigger_timestamps = [a[0] for a in timestamp_blocks if len(a)!=0]
		offset_timestamps=[]
		for i,trigger_timestamp in enumerate(trigger_timestamps):
			offset_timestamps.append(timestamp_blocks_signal[i] - trigger_timestamp)
		combined_timestamps = [ts for sublist in offset_timestamps for ts in sublist]
		return combined_timestamps
		
	def plotHistogram(self,timebase, tmin=1e-9, tmax=10e-9,trigger_channel=0,signal_channel=1,fignum=432):
		figure(fignum),clf()
		combined_timestamps=self.getHistogram(trigger_channel,signal_channel)
		split_combined_timestamps = [stamp for stamp in combined_timestamps if tmin<stamp<tmax]
		print(size(split_combined_timestamps))
		min_ts,max_ts = min(split_combined_timestamps), max(split_combined_timestamps)
		nbins = int((tmax-tmin)/(2*timebase))
		print(nbins)
		hist1=hist(1e9*array(split_combined_timestamps), bins=nbins,range=(1e9*min_ts,1e9*max_ts),histtype="step")
		xlim(1e9*tmin,1e9*tmax)
		grid(1)
		xlabel(r"Time (ns)")
		ylabel("cps / bin [WRONG UNITS!]")
		show()
	
	def getTotalCounts(self,selected_channels=None):
		if selected_channels==None:
			selected_channels = set(self.channels)
		chan_counts = {}
		for c in selected_channels:
			chan_counts[c]=list(self.channels).count(c)
		chan_counts[0] = chan_counts[0]-list(self.timestamps).count(0) #remove unused buffer elements
		return chan_counts
	def plotCoincidences(self,):
		ts_ch = zip(self.timestamps,self.channels)
		detected_channels = self.getTotalCounts().keys()
		figure(2),clf()
		for c in detected_channels:
		 tsc = [tc[0] for tc in ts_ch if tc[1]==c] 
		 plot(tsc,label="Ch"+str(c))
		xlabel("count")
		ylabel("timestamp index")
		legend(loc="best")
		grid(1)
		show()
	def getAutoCorrelation(self,auto_col_channel=0):
		auto_col_indices=where(self.channels==auto_col_channel)[0][1:]
		indices_1=auto_col_indices[::2] 
		indices_2=auto_col_indices[1::2]
		fake_1=[self.timestamps[n] for n in indices_1]
		fake_2=[self.timestamps[n] for n in indices_2]
		auto_col=[b - a for a, b in zip(fake_1, fake_2)]
		return auto_col
	def plotAutoCorrelation(self,timebase,tmin=1e-9, tmax=10e-9,auto_col_channel=0):
		figure(3),clf()
		auto_col_timestamps=self.getAutoCorrelation(auto_col_channel)
		split_timestamps = [stamp for stamp in auto_col_timestamps if tmin<stamp<tmax]
		min_ts,max_ts = min(split_timestamps), max(split_timestamps)
		nbins = int((tmax-tmin)/(2*timebase))
		hist1=hist(1e9*array(split_timestamps), bins=nbins,range=(1e9*min_ts,1e9*max_ts),histtype="step")
		xlim(1e9*tmin,1e9*tmax)
		grid(1)
		xlabel(r"Time (ns)")
		ylabel("cps / bin")
		show()

	
#execfile("Correlator.py")
#EoF