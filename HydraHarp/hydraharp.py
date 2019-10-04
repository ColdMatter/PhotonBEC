<<<<<<< HEAD
#Adapted by BTW from example code from PicoQuant
#https://github.com/PicoQuant/HH400-v3.x-Demos/tree/master/Windows/32bit/Python

#--------------------
#PQ header
#--------------------
# Demo for access to HydraHarp 400 Hardware via HHLIB.DLL v 3.0.
# The program performs a measurement based on hard coded settings.
# The resulting data is stored in a binary output file.
#
# Keno Goertz, PicoQuant GmbH, February 2018
#--------------------
#End PQ header
#--------------------

import sys
from socket import gethostname
if gethostname().lower() == "ph-photonbec3":
	sys.path.append("D:/Control/PythonPackages/")


from pylab import *
import pbec_analysis
import time
import ctypes as ct
from ctypes import byref
import binascii
from bitstring import BitArray, Bits
import copy
import numpy as np

#--------------------
#PQ comments on variables. These variables now have default definitions in the functions.
#--------------------
#Measurement parameters, these are hardcoded since this is just a demo
#mode = MODE_T2 # set T2 or T3 here, observe suitable Syncdivider and Range!
#binning = 0 # you can change this, meaningful only in T3 mode
#offset = 0 # you can change this, meaningful only in T3 mode
#tacq = 1000 # Measurement time in millisec, you can change this. BTW renamed this intTime
#syncDivider = 1 # you can change this, observe mode! READ MANUAL!
#syncCFDZeroCross = 10 # you can change this (in mV)
#syncCFDLevel = 50 # you can change this (in mV)
#syncChannelOffset = -5000 # you can change this (in ps, like a cable delay)
#inputCFDZeroCross = 10 # you can change this (in mV)
#inputCFDLevel = 50 # you can change this (in mV)
#inputChannelOffset = 0 # you can change this (in ps, like a cable delay)
#--------------------
#End PQ comments
#--------------------


class HydraHarp(object):	
	def __init__(self, do_setup=True):

		self.open = False
		if do_setup:
			self.setup()
			
	def setup(self, MAXDEVNUM = 8, mode_name = "MODE_T2",calibrate=True, syncDivider = 1, syncCFDLevel = 50, syncCFDZeroCross = 10, syncChannelOffset = -5000, inputCFDLevel = 50, inputCFDZeroCross = 10, inputChannelOffset = 0, binning = 0, offset = 0, intTime = 1000):
		#Masks for decoding PQ custom data type. 32 bits per event
		self.time_mask = BitArray(format(2**25-1,'#034b'))
		self.channel_mask = BitArray(format((2**31-1)-(2**25-1),'#034b'))
		self.special_mask = BitArray(format(2**31,'#034b'))
		self.mode_dictionary = {"MODE_T2": 2, "MODE_T3": 3}
		self.mode = self.mode_dictionary[mode_name]
		self.MAXDEVNUM = MAXDEVNUM
		self.numChannels = ct.c_int()
		self.syncDivider = syncDivider
		self.syncCFDLevel = syncCFDLevel
		self.syncCFDZeroCross = syncCFDZeroCross
		self.syncChannelOffset = syncChannelOffset
		self.inputCFDLevel = inputCFDLevel
		self.inputCFDZeroCross = inputCFDZeroCross
		self.inputChannelOffset = inputChannelOffset
		self.binning = binning
		self.offset = offset
		self.intTime = intTime
		dllDirectory = pbec_analysis.control_root_folder + "\\HydraHarp\\"
		# From hhdefin.h
		self.MAXLENCODE = 6
		self.HHMAXINPCHAN = 8
		self.TTREADMAX = 131072
		self.FLAG_OVERFLOW = 0x0001
		self.FLAG_FIFOFULL = 0x0002
		self.TTREADMAX = 131072
		if self.open:
			print "already open"
			pass
		try:
			self.dll = ct.WinDLL(dllDirectory + "hhlib.dll")
			self.hwSerial = ct.create_string_buffer(b"", 8)
			self.dev = []
			self.resolution = ct.c_double()
			self.syncRate = ct.c_int()
			self.countRate = ct.c_int()
			self.errorString = ct.create_string_buffer(b"", 40)
			self.warnings = ct.c_int()
			self.warningstext = ct.create_string_buffer(b"", 16384)

			print("\nSearching for HydraHarp devices...")
			print("Devidx     Status")

			for i in range(0, self.MAXDEVNUM):
				self.retcode = self.dll.HH_OpenDevice(ct.c_int(i), self.hwSerial)
				if self.retcode == 0:
					print("  %1d        S/N %s" % (i, self.hwSerial.value.decode("utf-8")))
					self.dev.append(i)
				else:
					if self.retcode == -1: # HH_ERROR_DEVICE_OPEN_FAIL
						print("  %1d        no device" % i)
					else:
						self.dll.HH_GetErrorString(self.errorString, ct.c_int(self.retcode))
						print("  %1d        %s" % (i, self.errorString.value.decode("utf8")))
			
			if len(self.dev) < 1:
				print("No device available.")
				self.closeDevices()
			# In this demo we will use the first HydraHarp device we find, i.e. self.dev[0].
			# You can also use multiple devices in parallel.
			# You can also check for specific serial numbers, so that you always know 
			# which physical device you are talking to.
			print("Using device #%1d" % self.dev[0])
			print("\nInitializing the device...")
			# with internal clock
			self.tryfunc(self.dll.HH_Initialize(ct.c_int(self.dev[0]), ct.c_int(self.mode), ct.c_int(0)),\
					"Initialize")
			self.getNInputChannels()
			if calibrate:
				self.calibrate()
			self.SetSyncDiv(self.syncDivider)
			self.SetSyncCFD(self.syncCFDLevel, self.syncCFDZeroCross)
			self.SetSyncChannelOffset(self.syncChannelOffset)
			self.SetInputChannelSettings(inputCFDLevel = self.inputCFDLevel, inputCFDZeroCross = self.inputCFDZeroCross, inputChannelOffset = self.inputChannelOffset,\
										binning = self.binning, offset = self.offset)
		except Exception as e:
			raise e

	def getNInputChannels(self):
		self.tryfunc(self.dll.HH_GetNumOfInputChannels(ct.c_int(self.dev[0]), byref(self.numChannels)),\
				"GetNumOfInputChannels")
		print("Device has %i input channels." % self.numChannels.value)
	def calibrate(self):
		print("\nCalibrating...")
		self.tryfunc(self.dll.HH_Calibrate(ct.c_int(self.dev[0])), "Calibrate")

	def SetSyncDiv(self, syncDivider = None):
		if syncDivider == None:
			pass
		else:
			self.syncDivider = syncDivider
		self.tryfunc(self.dll.HH_SetSyncDiv(ct.c_int(self.dev[0]), ct.c_int(self.syncDivider)), "SetSyncDiv")

	def SetSyncCFD(self, syncCFDLevel = None, syncCFDZeroCross = None):
		if syncCFDLevel == None:
			pass
		else:
			self.syncCFDLevel = syncCFDLevel
		if syncCFDZeroCross == None:
			pass
		else:
			self.syncCFDZeroCross = syncCFDZeroCross
		self.tryfunc(
			self.dll.HH_SetSyncCFD(ct.c_int(self.dev[0]), ct.c_int(self.syncCFDLevel),
								ct.c_int(self.syncCFDZeroCross)),\
			"SetSyncCFD"
		)
	def SetSyncChannelOffset(self, syncChannelOffset = None):
		if syncChannelOffset == None:
			pass
		else:
			self.syncChannelOffset = syncChannelOffset
		self.tryfunc(self.dll.HH_SetSyncChannelOffset(ct.c_int(self.dev[0]), ct.c_int(self.syncChannelOffset)),\
					"SetSyncChannelOffset")
	
	def SetInputChannelSettings(self, inputCFDLevel = None, inputCFDZeroCross = None, inputChannelOffset = None,\
										binning = None, offset = None):
			if inputCFDLevel == None:
				pass
			else:
				self.inputCFDLevel = inputCFDLevel
			if inputCFDZeroCross == None:
				pass
			else:
				self.inputCFDZeroCross = inputCFDZeroCross
			if inputChannelOffset == None:
				pass
			else:
				self.inputChannelOffset = inputChannelOffset
			if binning == None:
				pass
			else:
				self.binning = binning
			if offset == None:
				pass
			else:
				self.offset = offset
			# we use the same input settings for all channels, you can change this
			for i in range(0, self.numChannels.value):
				self.tryfunc(
					self.dll.HH_SetInputCFD(ct.c_int(self.dev[0]), ct.c_int(i), ct.c_int(self.inputCFDLevel),\
										 ct.c_int(self.inputCFDZeroCross)),\
					"SetInputCFD"
				)

				self.tryfunc(
					self.dll.HH_SetInputChannelOffset(ct.c_int(self.dev[0]), ct.c_int(i),\
												   ct.c_int(self.inputChannelOffset)),\
					"SetInputChannelOffset"
				)

			# Meaningful only in T3 mode
			if self.mode == self.mode_dictionary["MODE_T3"]:
				self.tryfunc(self.dll.HH_SetBinning(ct.c_int(self.dev[0]), ct.c_int(self.binning)), "SetBinning")
				self.tryfunc(self.dll.HH_SetOffset(ct.c_int(self.dev[0]), ct.c_int(self.offset)), "SetOffset")
				self.tryfunc(self.dll.HH_GetResolution(ct.c_int(self.dev[0]), byref(self.resolution)), "GetResolution")
				print("Resolution is %1.1lfps" % self.resolution.value)
			# Note: after Init or SetSyncDiv you must allow >100 ms for valid  count rate readings
			time.sleep(0.2)


			self.open = True
		


	def closeDevices(self):
		for i in range(0, self.MAXDEVNUM):
			self.dll.HH_CloseDevice(ct.c_int(i))
		#sys.exit(0)

	def stoptttr(self):
		self.retcode = self.dll.HH_StopMeas(ct.c_int(self.dev[0]))
		if self.retcode < 0:
			print("HH_StopMeas error %1d. Aborted." % self.retcode)
		#self.closeDevices()

	def tryfunc(self, retcode, funcName, measRunning=False):
		self.retcode = retcode
		if self.retcode < 0:
			self.dll.HH_GetErrorString(self.errorString, ct.c_int(self.retcode))
			print("HH_%s error %d (%s). Aborted." % (funcName, self.retcode,\
				  self.errorString.value.decode("utf-8")))
			if measRunning:
				self.stoptttr()
			else:
				self.closeDevices()
	
	def test(self):
		self.GetLibraryInfo()
		self.GetHardwareInfo()
		self.GetSyncRate()
		self.GetCountRates()
		self.printProperties()
	
	def GetLibraryInfo(self, LIB_VERSION = "3.0"):
		self.libVersion = ct.create_string_buffer(b"", 8)
		self.dll.HH_GetLibraryVersion(self.libVersion)
		print("Library version is %s" % self.libVersion.value.decode("utf-8"))
		if self.libVersion.value.decode("utf-8") != LIB_VERSION:
			print("Warning: The application was built for version %s" % LIB_VERSION)
		
	def GetHardwareInfo(self):
		self.hwPartno = ct.create_string_buffer(b"", 8)
		self.hwVersion = ct.create_string_buffer(b"", 8)
		self.hwModel = ct.create_string_buffer(b"", 16)
		self.tryfunc(self.dll.HH_GetHardwareInfo(self.dev[0], self.hwModel, self.hwPartno, self.hwVersion),\
				"GetHardwareInfo")
		print("Found Model %s Part no %s Version %s" % (self.hwModel.value.decode("utf-8"),\
			  self.hwPartno.value.decode("utf-8"), self.hwVersion.value.decode("utf-8")))
		
	def printProperties(self):
		print("\nMode             : %d" % self.mode)
		print("Binning           : %d" % self.binning)
		print("Offset            : %d" % self.offset)
		print("AcquisitionTime   : %d" % self.intTime)
		print("SyncDivider       : %d" % self.syncDivider)
		print("SyncCFDZeroCross  : %d" % self.syncCFDZeroCross)
		print("SyncCFDLevel      : %d" % self.syncCFDLevel)
		print("InputCFDZeroCross : %d" % self.inputCFDZeroCross)
		print("InputCFDLevel     : %d" % self.inputCFDLevel)
		
	def GetSyncRate(self):
		self.tryfunc(self.dll.HH_GetSyncRate(ct.c_int(self.dev[0]), byref(self.syncRate)), "GetSyncRate")
		print("\nSyncrate=%1d/s" % self.syncRate.value)
		
	def GetCountRates(self):
		count_rates = list()
		for i in range(0, self.numChannels.value):
			self.tryfunc(self.dll.HH_GetCountRate(ct.c_int(self.dev[0]), ct.c_int(i), byref(self.countRate)),\
				"GetCountRate")
			count_rates.append(float(self.countRate.value))
		count_rates = np.array(count_rates)
		return count_rates
			# print("Countrate[%1d]=%1d/s" % (i, self.countRate.value))

		

	def start_measure(self, intTime):
		self.intTime = intTime
		self.progress = 0
		self.stop_condition = True
		sys.stdout.write("\nProgress:%9u" % self.progress)
		sys.stdout.flush()

		self.tryfunc(self.dll.HH_StartMeas(ct.c_int(self.dev[0]), ct.c_int(self.intTime)), "StartMeas")

	def get_data(self, intTime):
		self.intTime = intTime
		self.progress = 0
		self.stop_condition = True

		sys.stdout.write("\nProgress:%9u" % self.progress)
		sys.stdout.flush()

		self.tryfunc(self.dll.HH_StartMeas(ct.c_int(self.dev[0]), ct.c_int(self.intTime)), "StartMeas")
		# Variables to store information read from DLLs
		self.mybuffer = (ct.c_uint * self.TTREADMAX)()
		self.flags = ct.c_int()
		self.nRecords = ct.c_int()
		self.ctcstatus = ct.c_int()
		
		self.times = []
		self.channels = []
		self.specials = []
		T2WrapAround = 2**25
		self.overrun_time = 0
		
		while self.stop_condition:
			if self.mode == self.mode_dictionary["MODE_T3"]:
				print "Haven't coded reading the output from T3 mode yet"
				self.stop_condition = False
				sys.exit(0)
			self.tryfunc(self.dll.HH_GetFlags(ct.c_int(self.dev[0]), byref(self.flags)), "GetFlags")

			if self.flags.value & self.FLAG_FIFOFULL > 0:
				print("\nFiFo Overrun!")
				self.stoptttr()

			self.tryfunc(
				self.dll.HH_ReadFiFo(ct.c_int(self.dev[0]), byref(self.mybuffer), self.TTREADMAX,\
								  byref(self.nRecords)),\
				"ReadFiFo", measRunning=True
			)
			still_values=True
			#BTW bitwise manipulation. Slower than saving directly to PTU file, but saves in a more useful format for later analysis.
			#NOTE: this doesn't distinguish between the sync channel and channel 0 due to a mistake. Needs fixing soon.
			if self.nRecords.value > 0:
				# We could just iterate through our buffer with a for loop, however,
				# this is slow and might cause a FIFO overrun. So instead, we shrinken
				# the buffer to its appropriate length with array slicing, which gives
				# us a python list. This list then needs to be converted back into
				# a ctype array which can be written at once to the output file
				for i,event in enumerate(self.mybuffer[0:self.nRecords.value]):
					bin_rep = format(event,'#034b')
					special_str = '0b0'+bin_rep[2]
					channel_str = '0b0'+bin_rep[3:9]
					time_str = '0b0'+bin_rep[10:35]
					special = int(special_str,2)
					channel = int(channel_str,2)
					single_time = int(time_str,2)
					
					if special == 0:
						self.times.append(single_time+self.overrun_time)
						self.channels.append(channel+1)
						#self.overrun_time = 0
					else:
						if channel==0:#Sync event
							self.times.append(single_time+self.overrun_time)
							self.channels.append(channel)
							#self.overrun_time = 0
						elif channel==63:#Overrun the 25 bits single_time times
							if single_time == 0:
								self.overrun_time+=T2WrapAround
							else:
								self.overrun_time += T2WrapAround * single_time
						else:
							print 'We dont deal with markers yet'
							sys.exit(0)
				#outputfile.write((ct.c_uint*self.nRecords.value)(*self.mybuffer[0:self.nRecords.value]))
				self.progress += self.nRecords.value
				sys.stdout.write("\rHH events read:%9u" % self.progress)
				sys.stdout.flush()
			else:
				self.tryfunc(self.dll.HH_CTCStatus(ct.c_int(self.dev[0]), byref(self.ctcstatus)),\
						"CTCStatus")
				if self.ctcstatus.value > 0: 
					print("\nDone reading HydraHarp")
					self.stoptttr()
					self.stop_condition = False
		# within this loop you can also read the count rates if needed.
#closeDevices()
#outputfile = open("tttrmode.out", "wb+")


	#
	#
	#
	# in development...
	def get_number_of_coincidences(self, channel1, channel2, acquisition_time, coincidence_time):
		'''
			Parameters:
				channel1 (int)
				channel2 (int)
				acquisition_time (int) in units of miliseconds
				coincidence_time (int) in units of miliseconds

		'''

		self.get_data(intTime=acquisition_time)
		self.channels = np.array(self.channels)
		self.times = np.array(self.times)

		channel1_times = self.times[np.where(self.channels == channel1)[0]]
		channel1_times = channel1_times[np.argsort(channel1_times)]
		channel2_times = self.times[np.where(self.channels == channel2)[0]]
		channel2_times = channel2_times[np.argsort(channel2_times)]

		coincidence_count = 0
		last_coincidence_on_second_channel = 0
		for time in channel1_times:
			i = copy.deepcopy(last_coincidence_on_second_channel)
			coincidence_flag = False
			while channel2_times[i] < (time + coincidence_time) and coincidence_flag is False and i < len(channel2_times)-1:
				if np.abs(time - channel2_times[i]) < coincidence_time:
					coincidence_flag = True
					last_coincidence_on_second_channel = copy.deepcopy(i)
					coincidence_count += 1
				else:
					i += 1

		return coincidence_count





=======
#Adapted from example code from PicoQuant

#--------------------
#PQ header
#--------------------
# Demo for access to HydraHarp 400 Hardware via HHLIB.DLL v 3.0.
# The program performs a measurement based on hard coded settings.
# The resulting data is stored in a binary output file.
#
# Keno Goertz, PicoQuant GmbH, February 2018
#--------------------
#End PQ header
#--------------------

import sys
from socket import gethostname
if gethostname().lower() == "ph-photonbec3":
	sys.path.append("D:/Control/PythonPackages/")


from pylab import *
import pbec_analysis
import time
import ctypes as ct
from ctypes import byref
import binascii
from bitstring import BitArray, Bits

#--------------------
#PQ comments on variables. These variables now have default definitions in the functions.
#--------------------
#Measurement parameters, these are hardcoded since this is just a demo
#mode = MODE_T2 # set T2 or T3 here, observe suitable Syncdivider and Range!
#binning = 0 # you can change this, meaningful only in T3 mode
#offset = 0 # you can change this, meaningful only in T3 mode
#tacq = 1000 # Measurement time in millisec, you can change this. BTW renamed this intTime
#syncDivider = 1 # you can change this, observe mode! READ MANUAL!
#syncCFDZeroCross = 10 # you can change this (in mV)
#syncCFDLevel = 50 # you can change this (in mV)
#syncChannelOffset = -5000 # you can change this (in ps, like a cable delay)
#inputCFDZeroCross = 10 # you can change this (in mV)
#inputCFDLevel = 50 # you can change this (in mV)
#inputChannelOffset = 0 # you can change this (in ps, like a cable delay)
#--------------------
#End PQ comments
#--------------------


class HydraHarp(object):	
	def __init__(self, do_setup=True):
		self.open = False
		if do_setup:
			self.setup()
			
	def setup(self, MAXDEVNUM = 8, mode_name = "MODE_T2",calibrate=True, syncDivider = 1, syncCFDLevel = 50, syncCFDZeroCross = 10, syncChannelOffset = -5000, inputCFDLevel = 50, inputCFDZeroCross = 10, inputChannelOffset = 0, binning = 0, offset = 0, intTime = 1000):
		#Masks for decoding PQ custom data type. 32 bits per event
		self.time_mask = BitArray(format(2**25-1,'#034b'))
		self.channel_mask = BitArray(format((2**31-1)-(2**25-1),'#034b'))
		self.special_mask = BitArray(format(2**31,'#034b'))
		self.mode_dictionary = {"MODE_T2": 2, "MODE_T3": 3}
		self.mode = self.mode_dictionary[mode_name]
		self.MAXDEVNUM = MAXDEVNUM
		self.numChannels = ct.c_int()
		self.syncDivider = syncDivider
		self.syncCFDLevel = syncCFDLevel
		self.syncCFDZeroCross = syncCFDZeroCross
		self.syncChannelOffset = syncChannelOffset
		self.inputCFDLevel = inputCFDLevel
		self.inputCFDZeroCross = inputCFDZeroCross
		self.inputChannelOffset = inputChannelOffset
		self.binning = binning
		self.offset = offset
		self.intTime = intTime
		dllDirectory = pbec_analysis.control_root_folder + "\\HydraHarp\\"
		# From hhdefin.h
		self.MAXLENCODE = 6
		self.HHMAXINPCHAN = 8
		self.TTREADMAX = 131072
		self.FLAG_OVERFLOW = 0x0001
		self.FLAG_FIFOFULL = 0x0002
		self.TTREADMAX = 131072
		if self.open:
			print "already open"
			pass
		try:
			self.dll = ct.WinDLL(dllDirectory + "hhlib.dll")
			self.hwSerial = ct.create_string_buffer(b"", 8)
			self.dev = []
			self.resolution = ct.c_double()
			self.syncRate = ct.c_int()
			self.countRate = ct.c_int()
			self.errorString = ct.create_string_buffer(b"", 40)
			self.warnings = ct.c_int()
			self.warningstext = ct.create_string_buffer(b"", 16384)

			print("\nSearching for HydraHarp devices...")
			print("Devidx     Status")

			for i in range(0, self.MAXDEVNUM):
				self.retcode = self.dll.HH_OpenDevice(ct.c_int(i), self.hwSerial)
				if self.retcode == 0:
					print("  %1d        S/N %s" % (i, self.hwSerial.value.decode("utf-8")))
					self.dev.append(i)
				else:
					if self.retcode == -1: # HH_ERROR_DEVICE_OPEN_FAIL
						print("  %1d        no device" % i)
					else:
						self.dll.HH_GetErrorString(self.errorString, ct.c_int(self.retcode))
						print("  %1d        %s" % (i, self.errorString.value.decode("utf8")))
			
			if len(self.dev) < 1:
				print("No device available.")
				self.closeDevices()
			# In this demo we will use the first HydraHarp device we find, i.e. self.dev[0].
			# You can also use multiple devices in parallel.
			# You can also check for specific serial numbers, so that you always know 
			# which physical device you are talking to.
			print("Using device #%1d" % self.dev[0])
			print("\nInitializing the device...")
			# with internal clock
			self.tryfunc(self.dll.HH_Initialize(ct.c_int(self.dev[0]), ct.c_int(self.mode), ct.c_int(0)),\
					"Initialize")
			self.getNInputChannels()
			if calibrate:
				self.calibrate()
			self.SetSyncDiv(self.syncDivider)
			self.SetSyncCFD(self.syncCFDLevel, self.syncCFDZeroCross)
			self.SetSyncChannelOffset(self.syncChannelOffset)
			self.SetInputChannelSettings(inputCFDLevel = self.inputCFDLevel, inputCFDZeroCross = self.inputCFDZeroCross, inputChannelOffset = self.inputChannelOffset,\
										binning = self.binning, offset = self.offset)
		except Exception as e:
			raise e

	def getNInputChannels(self):
		self.tryfunc(self.dll.HH_GetNumOfInputChannels(ct.c_int(self.dev[0]), byref(self.numChannels)),\
				"GetNumOfInputChannels")
		print("Device has %i input channels." % self.numChannels.value)
	def calibrate(self):
		print("\nCalibrating...")
		self.tryfunc(self.dll.HH_Calibrate(ct.c_int(self.dev[0])), "Calibrate")

	def SetSyncDiv(self, syncDivider = None):
		if syncDivider == None:
			pass
		else:
			self.syncDivider = syncDivider
		self.tryfunc(self.dll.HH_SetSyncDiv(ct.c_int(self.dev[0]), ct.c_int(self.syncDivider)), "SetSyncDiv")

	def SetSyncCFD(self, syncCFDLevel = None, syncCFDZeroCross = None):
		if syncCFDLevel == None:
			pass
		else:
			self.syncCFDLevel = syncCFDLevel
		if syncCFDZeroCross == None:
			pass
		else:
			self.syncCFDZeroCross = syncCFDZeroCross
		self.tryfunc(
			self.dll.HH_SetSyncCFD(ct.c_int(self.dev[0]), ct.c_int(self.syncCFDLevel),
								ct.c_int(self.syncCFDZeroCross)),\
			"SetSyncCFD"
		)
	def SetSyncChannelOffset(self, syncChannelOffset = None):
		if syncChannelOffset == None:
			pass
		else:
			self.syncChannelOffset = syncChannelOffset
		self.tryfunc(self.dll.HH_SetSyncChannelOffset(ct.c_int(self.dev[0]), ct.c_int(self.syncChannelOffset)),\
					"SetSyncChannelOffset")
	
	def SetInputChannelSettings(self, inputCFDLevel = None, inputCFDZeroCross = None, inputChannelOffset = None,\
										binning = None, offset = None):
			if inputCFDLevel == None:
				pass
			else:
				self.inputCFDLevel = inputCFDLevel
			if inputCFDZeroCross == None:
				pass
			else:
				self.inputCFDZeroCross = inputCFDZeroCross
			if inputChannelOffset == None:
				pass
			else:
				self.inputChannelOffset = inputChannelOffset
			if binning == None:
				pass
			else:
				self.binning = binning
			if offset == None:
				pass
			else:
				self.offset = offset
			# we use the same input settings for all channels, you can change this
			for i in range(0, self.numChannels.value):
				self.tryfunc(
					self.dll.HH_SetInputCFD(ct.c_int(self.dev[0]), ct.c_int(i), ct.c_int(self.inputCFDLevel),\
										 ct.c_int(self.inputCFDZeroCross)),\
					"SetInputCFD"
				)

				self.tryfunc(
					self.dll.HH_SetInputChannelOffset(ct.c_int(self.dev[0]), ct.c_int(i),\
												   ct.c_int(self.inputChannelOffset)),\
					"SetInputChannelOffset"
				)

			# Meaningful only in T3 mode
			if self.mode == self.mode_dictionary["MODE_T3"]:
				self.tryfunc(self.dll.HH_SetBinning(ct.c_int(self.dev[0]), ct.c_int(self.binning)), "SetBinning")
				self.tryfunc(self.dll.HH_SetOffset(ct.c_int(self.dev[0]), ct.c_int(self.offset)), "SetOffset")
				self.tryfunc(self.dll.HH_GetResolution(ct.c_int(self.dev[0]), byref(self.resolution)), "GetResolution")
				print("Resolution is %1.1lfps" % self.resolution.value)
			# Note: after Init or SetSyncDiv you must allow >100 ms for valid  count rate readings
			time.sleep(0.2)


			self.open = True
		


	def closeDevices(self):
		for i in range(0, self.MAXDEVNUM):
			self.dll.HH_CloseDevice(ct.c_int(i))
		#sys.exit(0)

	def stoptttr(self):
		self.retcode = self.dll.HH_StopMeas(ct.c_int(self.dev[0]))
		if self.retcode < 0:
			print("HH_StopMeas error %1d. Aborted." % self.retcode)
		#self.closeDevices()

	def tryfunc(self, retcode, funcName, measRunning=False):
		self.retcode = retcode
		if self.retcode < 0:
			self.dll.HH_GetErrorString(self.errorString, ct.c_int(self.retcode))
			print("HH_%s error %d (%s). Aborted." % (funcName, self.retcode,\
				  self.errorString.value.decode("utf-8")))
			if measRunning:
				self.stoptttr()
			else:
				self.closeDevices()
	
	def test(self):
		self.GetLibraryInfo()
		self.GetHardwareInfo()
		self.GetSyncRate()
		self.GetCountRates()
		self.printProperties()
	
	def GetLibraryInfo(self, LIB_VERSION = "3.0"):
		self.libVersion = ct.create_string_buffer(b"", 8)
		self.dll.HH_GetLibraryVersion(self.libVersion)
		print("Library version is %s" % self.libVersion.value.decode("utf-8"))
		if self.libVersion.value.decode("utf-8") != LIB_VERSION:
			print("Warning: The application was built for version %s" % LIB_VERSION)
		
	def GetHardwareInfo(self):
		self.hwPartno = ct.create_string_buffer(b"", 8)
		self.hwVersion = ct.create_string_buffer(b"", 8)
		self.hwModel = ct.create_string_buffer(b"", 16)
		self.tryfunc(self.dll.HH_GetHardwareInfo(self.dev[0], self.hwModel, self.hwPartno, self.hwVersion),\
				"GetHardwareInfo")
		print("Found Model %s Part no %s Version %s" % (self.hwModel.value.decode("utf-8"),\
			  self.hwPartno.value.decode("utf-8"), self.hwVersion.value.decode("utf-8")))
		
	def printProperties(self):
		print("\nMode             : %d" % self.mode)
		print("Binning           : %d" % self.binning)
		print("Offset            : %d" % self.offset)
		print("AcquisitionTime   : %d" % self.intTime)
		print("SyncDivider       : %d" % self.syncDivider)
		print("SyncCFDZeroCross  : %d" % self.syncCFDZeroCross)
		print("SyncCFDLevel      : %d" % self.syncCFDLevel)
		print("InputCFDZeroCross : %d" % self.inputCFDZeroCross)
		print("InputCFDLevel     : %d" % self.inputCFDLevel)
		
	def GetSyncRate(self):
		self.tryfunc(self.dll.HH_GetSyncRate(ct.c_int(self.dev[0]), byref(self.syncRate)), "GetSyncRate")
		print("\nSyncrate=%1d/s" % self.syncRate.value)
		
	def GetCountRates(self):
		for i in range(0, self.numChannels.value):
			self.tryfunc(self.dll.HH_GetCountRate(ct.c_int(self.dev[0]), ct.c_int(i), byref(self.countRate)),\
				"GetCountRate")
			print("Countrate[%1d]=%1d/s" % (i, self.countRate.value))
		

	def start_measure(self, intTime):
		self.intTime = intTime
		self.progress = 0
		self.stop_condition = True
		sys.stdout.write("\nProgress:%9u" % self.progress)
		sys.stdout.flush()

		self.tryfunc(self.dll.HH_StartMeas(ct.c_int(self.dev[0]), ct.c_int(self.intTime)), "StartMeas")

	def get_data(self, intTime):
		self.intTime = intTime
		self.progress = 0
		self.stop_condition = True
		sys.stdout.write("\nProgress:%9u" % self.progress)
		sys.stdout.flush()

		self.tryfunc(self.dll.HH_StartMeas(ct.c_int(self.dev[0]), ct.c_int(self.intTime)), "StartMeas")
		# Variables to store information read from DLLs
		self.mybuffer = (ct.c_uint * self.TTREADMAX)()
		self.flags = ct.c_int()
		self.nRecords = ct.c_int()
		self.ctcstatus = ct.c_int()
		
		self.times = []
		self.channels = []
		self.specials = []
		T2WrapAround = 2**25
		self.overrun_time = 0
		
		t1 = time.time()
		while self.stop_condition:
			if self.mode == self.mode_dictionary["MODE_T3"]:
				print "Haven't coded reading the output from T3 mode yet"
				self.stop_condition = False
				sys.exit(0)
			self.tryfunc(self.dll.HH_GetFlags(ct.c_int(self.dev[0]), byref(self.flags)), "GetFlags")

			if self.flags.value & self.FLAG_FIFOFULL > 0:
				print("\nFiFo Overrun!")
				self.stoptttr()

			self.tryfunc(
				self.dll.HH_ReadFiFo(ct.c_int(self.dev[0]), byref(self.mybuffer), self.TTREADMAX,\
								  byref(self.nRecords)),\
				"ReadFiFo", measRunning=True
			)
			still_values=True
			#BTW bitwise manipulation. Slower than saving directly to PTU file, but saves in a more useful format for later analysis.
			#NOTE: this doesn't distinguish between the sync channel and channel 0 due to a mistake. Needs fixing soon.
			if self.nRecords.value > 0:
				# We could just iterate through our buffer with a for loop, however,
				# this is slow and might cause a FIFO overrun. So instead, we shrinken
				# the buffer to its appropriate length with array slicing, which gives
				# us a python list. This list then needs to be converted back into
				# a ctype array which can be written at once to the output file
				for i,event in enumerate(self.mybuffer[0:self.nRecords.value]):
					bin_rep = format(event,'#034b')
					bindata = BitArray(format(event,'#034b'))
					special = Bits('0b0'+bin_rep[2]).int
					channel = Bits('0b0'+bin_rep[3:9]).int
					single_time = Bits('0b0'+bin_rep[10:35]).int
					if special == 0:
						self.times.append(single_time+self.overrun_time)
						self.channels.append(channel)
						#self.overrun_time = 0
					else:
						if channel==0:#Sync event
							self.times.append(single_time+self.overrun_time)
							self.channels.append(channel)
							#self.overrun_time = 0
						elif channel==63:#Overrun the 25 bits single_time times
							if single_time == 0:
								self.overrun_time+=T2WrapAround
							else:
								self.overrun_time += T2WrapAround * single_time
						else:
							print 'We dont deal with markers yet'
							sys.exit(0)
				#outputfile.write((ct.c_uint*self.nRecords.value)(*self.mybuffer[0:self.nRecords.value]))
				self.progress += self.nRecords.value
				sys.stdout.write("\rProgress:%9u" % self.progress)
				sys.stdout.flush()
			else:
				self.tryfunc(self.dll.HH_CTCStatus(ct.c_int(self.dev[0]), byref(self.ctcstatus)),\
						"CTCStatus")
				if self.ctcstatus.value > 0: 
					print("\nDone")
					self.stoptttr()
					self.stop_condition = False
		t2 = time.time()
		print t2-t1
		# within this loop you can also read the count rates if needed.
		
#closeDevices()
#outputfile = open("tttrmode.out", "wb+")
>>>>>>> 2dd14f412c2e41dc41fe249d9a9e1057f214665a
