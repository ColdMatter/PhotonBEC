'''
	Written by:		Joao Rodrigues
	Last Update: 	October 16th 2020

'''


import numpy as np
import copy
import ctypes
import socket
import time

########## Parameters
if socket.gethostname() == "ph-photonbec5":
	dll_file = r"D:\Control\EMCCD\atmcd32d.dll"


class EMCCD():

	##### Error Codes
	emccd_return_codes = dict()
	emccd_return_codes.update({20001: 'DRV_ERROR_CODES'})
	emccd_return_codes.update({20002: 'DRV_SUCCESS'})
	emccd_return_codes.update({20003: 'DRV_VXDNOTINSTALLED'})
	emccd_return_codes.update({20004: 'DRV_ERROR_SCAN'})
	emccd_return_codes.update({20005: 'DRV_ERROR_CHECK_SUM'})
	emccd_return_codes.update({20006: 'DRV_ERROR_FILELOAD'})
	emccd_return_codes.update({20007: 'DRV_UNKNOWN_FUNCTION'})
	emccd_return_codes.update({20008: 'DRV_ERROR_VXD_INIT'})
	emccd_return_codes.update({20009: 'DRV_ERROR_ADDRESS'})
	emccd_return_codes.update({20010: 'DRV_ERROR_PAGELOCK'})
	emccd_return_codes.update({20011: 'DRV_ERROR_PAGE_UNLOCK'})
	emccd_return_codes.update({20012: 'DRV_ERROR_BOARDTEST'})
	emccd_return_codes.update({20013: 'DRV_ERROR_ACK'})
	emccd_return_codes.update({20014: 'DRV_ERROR_UP_FIFO'})
	emccd_return_codes.update({20015: 'DRV_ERROR_PATTERN'})
	emccd_return_codes.update({20017: 'DRV_ACQUISITION_ERRORS'})
	emccd_return_codes.update({20018: 'DRV_ACQ_BUFFER'})
	emccd_return_codes.update({20019: 'DRV_ACQ_DOWNFIFO_FULL'})
	emccd_return_codes.update({20020: 'DRV_PROC_UNKNOWN_INSTRUCTION'})
	emccd_return_codes.update({20021: 'DRV_ILLEGAL_OP_CODE'})
	emccd_return_codes.update({20022: 'DRV_KINETIC_TIME_NOT_MET'})
	emccd_return_codes.update({20023: 'DRV_ACCUM_TIME_NOT_MET'})
	emccd_return_codes.update({20024: 'DRV_NO_NEW_DATA'})
	emccd_return_codes.update({20025: 'PCI_DMA_FAIL'})
	emccd_return_codes.update({20026: 'DRV_SPOOLERROR'})
	emccd_return_codes.update({20027: 'DRV_SPOOLSETUPERROR'})
	emccd_return_codes.update({20029: 'SATURATED'})
	emccd_return_codes.update({20033: 'DRV_TEMPERATURE_CODES'})
	emccd_return_codes.update({20034: 'DRV_TEMPERATURE_OFF'})
	emccd_return_codes.update({20035: 'DRV_TEMP_NOT_STABILIZED'})
	emccd_return_codes.update({20036: 'DRV_TEMPERATURE_STABILIZED'})
	emccd_return_codes.update({20037: 'DRV_TEMPERATURE_NOT_REACHED'})
	emccd_return_codes.update({20038: 'DRV_TEMPERATURE_OUT_RANGE'})
	emccd_return_codes.update({20039: 'DRV_TEMPERATURE_NOT_SUPPORTED'})
	emccd_return_codes.update({20040: 'DRV_TEMPERATURE_DRIFT'})
	emccd_return_codes.update({20049: 'DRV_GENERAL_ERRORS'})
	emccd_return_codes.update({20050: 'DRV_INVALID_AUX'})
	emccd_return_codes.update({20051: 'DRV_COF_NOTLOADED'})
	emccd_return_codes.update({20052: 'DRV_FPGAPROG'})
	emccd_return_codes.update({20053: 'DRV_FLEXERROR'})
	emccd_return_codes.update({20054: 'DRV_GPIBERROR'})
	emccd_return_codes.update({20055: 'ERROR_DMA_UPLOAD'})
	emccd_return_codes.update({20064: 'DRV_DATATYPE'})
	emccd_return_codes.update({20065: 'DRV_DRIVER_ERRORS'})
	emccd_return_codes.update({20066: 'DRV_P1INVALID'})
	emccd_return_codes.update({20067: 'DRV_P2INVALID'})
	emccd_return_codes.update({20068: 'DRV_P3INVALID'})
	emccd_return_codes.update({20069: 'DRV_P4INVALID'})
	emccd_return_codes.update({20070: 'DRV_INIERROR'})
	emccd_return_codes.update({20071: 'DRV_COFERROR'})
	emccd_return_codes.update({20072: 'DRV_ACQUIRING'})
	emccd_return_codes.update({20073: 'DRV_IDLE'})
	emccd_return_codes.update({20074: 'DRV_TEMPCYCLE'})
	emccd_return_codes.update({20075: 'DRV_NOT_INITIALIZED'})
	emccd_return_codes.update({20076: 'DRV_P5INVALID'})
	emccd_return_codes.update({20077: 'DRV_P6INVALID'})
	emccd_return_codes.update({20078: 'DRV_INVALID_MODE'})
	emccd_return_codes.update({20079: 'DRV_INVALID_FILTER'})
	emccd_return_codes.update({20080: 'DRV_I2CERRORS'})
	emccd_return_codes.update({20081: 'DRV_DRV_I2CDEVNOTFOUND'})
	emccd_return_codes.update({20082: 'DRV_I2CTIMEOUT'})
	emccd_return_codes.update({20083: 'DRV_P7INVALID'})
	emccd_return_codes.update({20089: 'DRV_USBERROR'})
	emccd_return_codes.update({20090: 'DRV_IOCERROR'})
	emccd_return_codes.update({20091: 'DRV_VRMVERSIONERROR'})
	emccd_return_codes.update({20093: 'DRV_USB_INTERRUPT_ENDPOINT_ERROR'})
	emccd_return_codes.update({20094: 'DRV_RANDOM_TRACK_ERROR'})
	emccd_return_codes.update({20095: 'DRV_INVALID_TRIGGER_MODE'})
	emccd_return_codes.update({20096: 'DRV_LOAD_FIRMWARE_ERROR'})
	emccd_return_codes.update({20097: 'DRV_DIVIDE_BY_ZERO_ERROR'})
	emccd_return_codes.update({20098: 'DRV_INVALID_RINGEXPOSURES'})
	emccd_return_codes.update({20099: 'DRV_BINNING_ERROR'})
	emccd_return_codes.update({20990: 'DRV_ERROR_NOCAMERA'})
	emccd_return_codes.update({20991: 'DRV_NOT_SUPPORTED'})
	emccd_return_codes.update({20992: 'DRV_NOT_AVAILABLE'})
	emccd_return_codes.update({20115: 'DRV_ERROR_MAP'})
	emccd_return_codes.update({20116: 'DRV_ERROR_UNMAP'})
	emccd_return_codes.update({20117: 'DRV_ERROR_MDL'})
	emccd_return_codes.update({20118: 'DRV_ERROR_UNMDL'})
	emccd_return_codes.update({20119: 'DRV_ERROR_BUFFSIZE'})
	emccd_return_codes.update({20121: 'DRV_ERROR_NOHANDLE'})
	emccd_return_codes.update({20130: 'DRV_GATING_NOT_AVAILABLE'})
	emccd_return_codes.update({20131: 'DRV_FPGA_VOLTAGE_ERROR'})
	emccd_return_codes.update({20099: 'DRV_BINNING_ERROR'})
	emccd_return_codes.update({20100: 'DRV_INVALID_AMPLIFIER'})
	emccd_return_codes.update({20101: 'DRV_INVALID_COUNTCONVERT_MODE'})

	##### Camera attributes
	acquisition_modes = {"single scan":1, "accumulate":2, "kinetics":3, "fast kinetics":4, "run till abort":5}
	output_amplifier_modes = {"EMCCD":0, "CCD":1}
	read_modes = {"full vertical binning":0, "multi-track":1, "random-track":2, "single-track":3, "image":4}
	shutter_modes = {"fully auto":0, "permanently open":1, "permanently closed":2, "open for FVB series":4, "open for any series":5}
	trigger_modes = {"internal":0, "external":1, "external start":6, "external exposure (bulb)":7, "external FVB EM":9, "software trigger":10, "external charge shifting":12}



	def __init__(self, VERBOSE=True, frontend=None):
		
		self.VERBOSE = VERBOSE
		self.frontend = frontend

		self.COOLER = False
		self.STABLE_TEMPERATURE = False

		# Loads the dll
		self.dll = ctypes.WinDLL(dll_file)

		# Initializes EMCCD SDK
		self.printout(message="Initializing SDK:")
		dummy = ctypes.c_char()
		out = self.dll.Initialize(dummy)
		self.printout(code=out)
		if not out == 20002:
			raise Exception("Could not load SDK")

		# Retrives the valid range of temperatures in centrigrades to which the detector can be cooled
		self.printout(message="Getting sensor temperature range:")
		Tmin = ctypes.c_int()
		Tmax = ctypes.c_int()
		out = self.dll.GetTemperatureRange(ctypes.pointer(Tmin), ctypes.pointer(Tmax))
		self.printout(code=out)
		if not out == 20002:
			raise Exception("Could not retrive detector temperature range: "+self.emccd_return_codes[out])
		self.Tmin = Tmin.value
		self.Tmax = Tmax.value
		self.printout(message="Temperature min = "+str(self.Tmin))
		self.printout(message="Temperature max = "+str(self.Tmax))

		# Gets horizontal shifting speeds from the camera
		self.printout(message="Calibrating horizontal shifting speeds")
		self.horizontal_shifting_speeds = dict() # Shifting speeds in MHz
		for typ in [0, 1]: # 0:electron multiplication, 1: conventional
			self.horizontal_shifting_speeds[typ] = dict()
			speeds = ctypes.c_int()
			out = self.dll.GetNumberHSSpeeds(ctypes.c_int(0), ctypes.c_int(typ), ctypes.pointer(speeds))
			speeds = speeds.value
			if out == 20002:
				for i in range(0, speeds):
					speedMHz = ctypes.c_float()
					out1 = self.dll.GetHSSpeed(ctypes.c_int(0), ctypes.c_int(typ), ctypes.c_int(i), ctypes.pointer(speedMHz))
					if out1 == 20002:
						self.horizontal_shifting_speeds[typ][i] = speedMHz.value
					else:
						raise Exception("Could not retrieve horizontal shift speed: "+self.emccd_return_codes[out1])
			else:
				raise Exception("Could not retrieve number of horizontal shift speeds: "+self.emccd_return_codes[out])

		# Gets vertical shifting speeds from the camera
		self.printout(message="Calibrating vertical shifting speeds")
		self.vertical_shifting_speeds = dict() # Shifting speeds in microseconds per pixel shift
		speeds = ctypes.c_int()
		out = self.dll.GetNumberVSSpeeds(ctypes.pointer(speeds))
		speeds = speeds.value
		if out == 20002:
			for i in range(0, speeds):
				speed_ms = ctypes.c_float()
				out1 = self.dll.GetVSSpeed(ctypes.c_int(i), ctypes.pointer(speed_ms))
				if out1 == 20002:
					self.vertical_shifting_speeds[i] = speed_ms.value
				else:
					raise Exception("Could not retrieve vertical shift speed: "+self.emccd_return_codes[out1])
		else:
			raise Exception("Could not retrieve number of vertical shift speeds: "+self.emccd_return_codes[out])

		# Gets Preamp gain values
		self.printout(message="Calibrating pre-amp gain values")
		self.preamp_gain_values = dict()
		gains = ctypes.c_int()
		out = self.dll.GetNumberPreAmpGains(ctypes.pointer(gains))
		gains = gains.value
		if out == 20002:
			for i in range(0, gains):
				gain = ctypes.c_float()
				out1 = self.dll.GetPreAmpGain(ctypes.c_int(i), ctypes.pointer(gain))
				if out1 == 20002:
					self.preamp_gain_values[i] = gain.value
				else:
					raise Exception("Could not retrieve pre-amp gain value: "+self.emccd_return_codes[out1])
		else:
			raise Exception("Could not retrieve number of pre-amp gains: "+self.emccd_return_codes[out])


		# Gets the detector size, in pixels
		self.printout(message="Getting number of detector pixels")
		xpixels = ctypes.c_int()
		ypixels = ctypes.c_int()
		out = self.dll.GetDetector(ctypes.pointer(xpixels), ctypes.pointer(ypixels))
		if not out == 20002:
			raise Exception("Could not retrive number of pixels: "+self.emccd_return_codes[out])
		self.xpixels = xpixels.value
		self.ypixels = ypixels.value
		self.image_format = None


	def printout(self, code=None, message=None):
		# Prints to the frontend, if it exists
		if not self.frontend is None:
			if not message is None:
				self.frontend.write_camera_message(message=message)
			if not code is None:
				self.frontend.write_camera_message(message=self.emccd_return_codes[code])

		# Prints to the command line
		if self.VERBOSE:
			if not message is None:
				print("EMCCD object: "+message)
			if not code is None:
				print("EMCCD object: "+self.emccd_return_codes[code])




	def SetTemperature(self, temperature):
		""" 
			Sets the desired temperature of the detector. To turn the cooling ON and OFF the user
			must use the CoolerON and CoolerOFF methods.

			Parameters:
				temperature (int): Desired detector temperature (in C)

		"""
		temperature = int(temperature)
		if temperature<self.Tmin or temperature>self.Tmax:
			raise Exception("Invalid temperature")
		self.printout(message="Setting temperature to "+str(temperature)+" C")
		out = self.dll.SetTemperature(ctypes.c_int(temperature))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def CoolerON(self):
		"""
			Switches ON the cooling.

		"""

		self.printout(message="Switching ON the cooling")
		out = self.dll.CoolerON()
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
			self.COOLER = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def CoolerOFF(self):
		"""
			Switches OFF the cooling.

		"""

		self.printout(message="Switching OFF the cooling")
		out = self.dll.CoolerOFF()
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
			self.COOLER = False
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def StabilizeTemperature(self):
		""" 
			Waits until detector temperature has stabilized to set point

		"""

		self.printout(message="Stabilizing detector temperature...")
		current_temperature_c = ctypes.c_int()
		out = self.dll.GetTemperature(ctypes.pointer(current_temperature_c))
		if out == 20037:
			while out == 20037:
				self.printout(message="    Current temperature: "+str(current_temperature_c.value))
				time.sleep(1)
				out = self.dll.GetTemperature(ctypes.pointer(current_temperature_c))
			self.printout(code=out)
		if out == 20036:
			SUCCESS = True
			self.STABLE_TEMPERATURE = True
			self.printout(message="Detector temperature has stabilized at set point")
		else:
			SUCCESS = False
			self.STABLE_TEMPERATURE = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out]), current_temperature_c.value




	def SetAcquisitionMode(self, mode):
		"""
			Sets the acquisition mode.

			Parameters:
				mode (str):		Option are "single scan", "accumulate", "kinetics", "fast kinetics", "run till abort"

		"""

		self.printout(message="Setting acquisition mode")
		if not any([mode==possibility for possibility in self.acquisition_modes.keys()]):
			raise Exception("Unkown acquisition mode")
		out = self.dll.SetAcquisitionMode(ctypes.c_int(self.acquisition_modes[mode]))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetOutputAmplifier(self, mode):
		"""
			Some EMCCD systems have the capability to use a second output amplifier. This
				function will set the type of output amplifier to be used when reading data from the head
				for these systems.


			Parameters:
				mode (str):		"EMCCD": Standard EMCCD gain register (default)/Conventional(clara)
								"CCD": Conventional CCD register/Extended NIR mode(clara).

		"""

		self.printout(message="Setting output amplifier mode")
		if not any([mode==possibility for possibility in self.output_amplifier_modes.keys()]):
			raise Exception("Unkown output amplifier mode")
		out = self.dll.SetOutputAmplifier(ctypes.c_int(self.output_amplifier_modes[mode]))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetReadMode(self, mode):
		"""
			Sets the read mode.

			Parameters:
				mode (str):		Option are "full vertical binning", "multi-track", "random-track", "single-track", "image"

		"""

		self.printout(message="Setting read mode")
		if not any([mode==possibility for possibility in self.read_modes.keys()]):
			raise Exception("Unkown read mode")
		out = self.dll.SetReadMode(ctypes.c_int(self.read_modes[mode]))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetShutter(self, typ, mode, closingtime, openingtime):
		"""
			This function controls the behaviour of the shutter.
			The typ parameter allows the user to control the TTL signal output to an external shutter.
			The mode parameter configures whether the shutter opens and closes automatically
				(controlled by the camera) or is permanently open or permanently closed.
			The opening and closing time specify the time required to open and close the shutter
				(this information is required for calculating acquisition timings - see SHUTTER TRANSFER TIME in the manual).


			Parameters:
				typ (int): 0: Output TTL low signal to open shutter
							1: Output TTL high signal to open shutter

				mode (str): Option are "fully auto", "permanently open", "permanently closed", "open for FVB series", "open for any series"

				closingtime (int): time shutter takes to close (miliseconds)

				openingtime (int): time shutter takes to open (miliseconds)

		"""

		self.printout(message="Setting shutter mode")
		if not (typ==0 or typ==1):
			raise Exception("Invalid shutter TTL type")

		if not any([mode==possibility for possibility in self.shutter_modes.keys()]):
			raise Exception("Unkown shutter mode")
		out = self.dll.SetShutter(
			ctypes.c_int(typ),
			ctypes.c_int(self.shutter_modes[mode]),
			ctypes.c_int(closingtime),
			ctypes.c_int(openingtime))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetExposureTime(self, time):
		"""
			This function will set the exposure time to the nearest valid value not less than the given
				value. The actual exposure time used is obtained by GetAcquisitionTimings.. Please
				refer to SECTION 5 - ACQUISITION MODES for further information.

			Parameters:
				time (float): The exposure time in seconds

		"""

		self.printout(message="Setting exposure time")
		out = self.dll.SetExposureTime(ctypes.c_float(time))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetTriggerMode(self, mode):
		"""
			This function will set the trigger mode that the camera will operate in.
			
			Parameters:
				mode (str): Options are "internal", "external", "external start", "external exposure (bulb)",
								"external FVB EM", "software trigger", "external charge shifting"

		"""

		self.printout(message="Setting trigger mode")
		if not any([mode==possibility for possibility in self.trigger_modes.keys()]):
			raise Exception("Unkown trigger mode")
		out = self.dll.SetTriggerMode(ctypes.c_int(self.trigger_modes[mode]))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetAccumulationCycleTime(self, time):
		"""
			This function will set the accumulation cycle time to the nearest valid value not less than
				the given value. The actual cycle time used is obtained by GetAcquisitionTimings. Please
				refer to SECTION 5 - ACQUISITION MODES for further information.

			Parameters:
				time (float): The accumulation cycle time in seconds

		"""

		self.printout(message="Setting accumulation cycle time")
		out = self.dll.SetAccumulationCycleTime(ctypes.c_float(time))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])





	def SetNumberAccumulations(self, number):
		"""
			This function will set the number of scans accumulated in memory. This will only take
				effect if the acquisition mode is either Accumulate or Kinetic Series.

			Parameters:
				number (int): Number of scans to accumulate

		"""

		self.printout(message="Setting number of accumulations")
		out = self.dll.SetNumberAccumulations(ctypes.c_int(number))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetNumberKinetics(self, number):
		"""
			This function will set the number of scans (possibly accumulated scans) to be taken
				during a single acquisition sequence. This will only take effect if the acquisition mode is
				Kinetic Series.

			Parameters:
				number (int): Number of scans to store

		"""

		self.printout(message="Setting number of kinetic scans")
		out = self.dll.SetNumberKinetics(ctypes.c_int(number))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetKineticCycleTime(self, time):
		"""
			This function will set the kinetic cycle time to the nearest valid value not less than the
				given value. The actual time used is obtained by GetAcquisitionTimings. Please refer to
				SECTION 5 - ACQUISITION MODES for further information.

			Parameters:
				time (float): The kinetic cycle time in seconds

		"""

		self.printout(message="Setting kinetic cycle time")
		out = self.dll.SetKineticCycleTime(ctypes.c_float(time))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetFrameTransferMode(self, FRAME_TRANSFER_MODE):
		"""
			 This function will set whether an acquisition will readout in Frame Transfer Mode. If the
				acquisition mode is Single Scan or Fast Kinetics this call will have no affect.

			Parameters:
				FRAME_TRANSFER_MODE (bool)

		"""

		dummy = {True: "ON", False: "OFF"}
		command = {True: 1, False: 0}
		self.printout(message="Setting frame transfer mode to "+dummy[FRAME_TRANSFER_MODE])
		out = self.dll.SetFrameTransferMode(ctypes.c_int(command[FRAME_TRANSFER_MODE]))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])	




	def SetHSSpeed(self, typ, index):
		"""
			This function will set the speed at which the pixels are shifted into the output node during
				the readout phase of an acquisition. Typically your camera will be capable of operating at
				several horizontal shift speeds. To get the actual speed that an index corresponds to use
				the GetHSSpeed function. 
			The actual speed in MHz are stored in self.horizontal_shifting_speeds

			Parameters:
				typ (int): 	Output amplification mode
							Valid values: 	0: electron multiplication/Conventional(clara).
											1: conventional/Extended NIR mode(clara).

				index (int): The index of the horizontal speed to be used

		"""

		if not (typ==0 or typ==1):
			raise Exception("Invalid amplification mode")
		if not any([index == element for element in self.horizontal_shifting_speeds[typ].keys()]):
			raise Exception("Invalid horizontal shifting speed")
		self.printout(message="Setting horizontal shift speed to "+str(self.horizontal_shifting_speeds[typ][index])+" MHz")
		out = self.dll.SetHSSpeed(ctypes.c_int(typ), ctypes.c_int(index))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetVSSpeed(self, index):
		"""
			This function will set the vertical speed to be used for subsequent acquisitions

			Parameters:
				
				index (int): The index into the vertical speed table

		"""

		if not any([index == element for element in self.vertical_shifting_speeds.keys()]):
			raise Exception("Invalid vertical shifting speed")
		self.printout(message="Setting vertical shift speed to "+str(self.vertical_shifting_speeds[index])+" ms per pixel shift")
		out = self.dll.SetVSSpeed(ctypes.c_int(index))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetPreAmpGain(self, index):
		"""
			This function will set the pre amp gain to be used for subsequent acquisitions. The actual gain factor that will 
				be applied can be found through a call to the GetPreAmpGain function.
			The number of Pre Amp Gains available is found by calling the GetNumberPreAmpGains function.

			Parameters:
				index (int): The index into the pre amp gain table
		"""

		if not any([index == element for element in self.preamp_gain_values.keys()]):
			raise Exception("Invalid pre-amp gain index")
		self.printout(message="Setting pre-amp gain to "+str(self.preamp_gain_values[index])+"x")
		out = self.dll.SetPreAmpGain(ctypes.c_int(index))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def SetEMCCDGain(self, gain):
		"""
			Allows the user to change the gain value. The valid range for the gain depends on what gain mode the camera is operating in. See SetEMGainMode to set the mode and
				GetEMGainRange to get the valid range to work with. To access higher gain values (>x300) see SetEMAdvanced.

			Parameters:
				gain (int): gain values

		"""

		self.printout(message="Setting EMCCD gain")
		FLAG, message, info = self.GetEMGainRange()
		lowest = info["lowest gain setting"]
		highest = info["highest gain setting"]
		if (gain>=lowest and gain<=highest):
			out = self.dll.SetEMCCDGain(ctypes.c_int(int(gain)))
			self.printout(code=out)
			if out == 20002:
				SUCCESS = True
			else:
				SUCCESS = False
			code = copy.deepcopy(self.emccd_return_codes[out])
		else:
			self.printout(message="EMCCD gain value outside allowed range. Allowed range is [{0}, {1}]".format(lowest, highest))
			SUCCESS = False
			code = None

		return SUCCESS, code




	def SetEMAdvanced(self, STATE):
		"""
			This function turns on and off access to higher EM gain levels within the SDK. Typically, 
				optimal signal to noise ratio and dynamic range is achieved between x1 to x300 EM Gain.
			Higher gains of > x300 are recommended for single photon counting only. Before using
				higher levels, you should ensure that light levels do not exceed the regime of tens of
				photons per pixel, otherwise accelerated ageing of the sensor can occur.

			Parameters:
				STATE (bool): 	True: Allow access
								False: Don't allow access

		"""

		if not (STATE==True or STATE==False):
			raise Exception("Invalid state: bool expeccted")
		self.printout(message="Setting EM advanced settings to "+str(STATE))
		modes = {True: 1, False: 0}
		out = self.dll.SetEMAdvanced(ctypes.c_int(modes[STATE]))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])





	def SetImage(self, hbin, vbin, hstart, hend, vstart, vend):
		"""
			This function will set the horizontal and vertical binning to be used when taking a full
			resolution image.

			Parameters:

				hbin (int)		: number of pixels to bin horizontally.
				vbin (int)		: number of pixels to bin vertically.
				hstart (int)	: Start column (inclusive).
				hend (int)		: End column (inclusive).
				vstart (int)	: Start row (inclusive).
				vend (int)		: End row (inclusive).
		
		"""

		self.printout(message="Setting image format ")
		out = self.dll.SetImage(
			ctypes.c_int(hbin),
			ctypes.c_int(vbin),
			ctypes.c_int(hstart),
			ctypes.c_int(hend),
			ctypes.c_int(vstart),
			ctypes.c_int(vend))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
			self.image_format = {"x": int(((hend-hstart+1)/hbin)), "y": int(((vend-vstart+1)/vbin))}
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])




	def GetEMGainRange(self):
		"""
			Returns the minimum and maximum values of the current selected EM Gain mode and temperature of the sensor.

		"""

		self.printout(message="Getting EM Gain range")
		lowest_gain_setting = ctypes.c_int()
		highest_gain_setting = ctypes.c_int()
		out = self.dll.GetEMGainRange(ctypes.pointer(lowest_gain_setting), ctypes.pointer(highest_gain_setting))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		info = {"lowest gain setting": lowest_gain_setting.value, "highest gain setting": highest_gain_setting.value}

		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out]), info



	def GetAcquisitionTimings(self):
		"""
			This function will return the current "valid" acquisition timing information. This function
				should be used after all the acquisitions settings have been set, e.g. SetExposureTime,
				SetKineticCycleTime and SetReadMode etc. The values returned are the actual times
				used in subsequent acquisitions.
			This function is required as it is possible to set the exposure time to 20ms, accumulate
				cycle time to 30ms and then set the readout mode to full image. As it can take 250ms to
				read out an image it is not possible to have a cycle time of 30ms.

		"""

		self.printout(message="Getting acquisition timings:")
		exposure_time = ctypes.c_float()
		accumulate_cycle_time = ctypes.c_float()
		kinetic_cycle_time = ctypes.c_float()
		out = self.dll.GetAcquisitionTimings(
			ctypes.pointer(exposure_time), 
			ctypes.pointer(accumulate_cycle_time),
			ctypes.pointer(kinetic_cycle_time))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		info = {"exposure time": exposure_time.value,
				"accumulate cycle time": accumulate_cycle_time.value,
				"kinetic cycle time": kinetic_cycle_time.value}

		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out]), info




	def GetStatus(self, VERBOSE=True):
		"""
			This function will return the current status of the Andor SDK system. This function should
				be called before an acquisition is started to ensure that it is IDLE and during an acquisition
				to monitor the process.

		"""
		if VERBOSE:
			self.printout(message="Getting Status")
		status = ctypes.c_int()
		out = self.dll.GetStatus(ctypes.pointer(status))
		if VERBOSE:
			self.printout(code=out)
		if out == 20002:
			SUCCESS = True
			status = status.value
			info = self.emccd_return_codes[status]
		else:
			SUCCESS = False
			info = None
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out]), info




	def GetAcquiredData(self, VERBOSE=True):
		"""
			This function will return the data from the last acquisition. The data are returned as long
				integers (32-bit signed integers). The "array" must be large enough to hold the complete
				data set.

		"""

		if not self.image_format is None:
			if VERBOSE:
				self.printout(message="Getting acquired data")
			full_size = self.image_format["x"]*self.image_format["y"]
			array = (ctypes.c_int*full_size)()
			out = self.dll.GetMostRecentImage(ctypes.pointer(array), ctypes.c_ulong(full_size))
			if out == 20002:
				SUCCESS = True
				array = np.array([value for value in array])
				image = np.reshape(array, (self.image_format["x"], self.image_format["y"]))
				image = np.transpose(np.flip(image,1))
			else:
				SUCCESS = False
				image = None
			message = copy.deepcopy(self.emccd_return_codes[out])
		else:
			self.printout(message="Cannot acquire data before setting image format. Use SetImage() method")
			SUCCESS = False
			message = None
			image = None
		return SUCCESS, message, image



	def StartAcquisition(self):
		"""
			This function starts an acquisition. The status of the acquisition can be monitored via
				GetStatus().

		"""

		self.printout(message="Starting Acquisition")
		out = self.dll.StartAcquisition()
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])	



	def AbortAcquisition(self):
		"""
				This function aborts the current acquisition if one is active.

		"""
		self.printout(message="Aborting Acquisition")
		out = self.dll.AbortAcquisition()
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])	




	def ShutDown(self, temperature):
		"""
			Shutdown procedure.
			1) Sets the temperature to "temperature". It is important not to shut down
				the SDK while temperature if below -20 C
			2) Waits for temperature to stabilize around the input temperature. 
			3) Cooler off
			4) Shuts down SDK

			Parameters:

				temperature (int): 	Desired detector temperature (in C)

		"""

		self.printout(message="Closing shutter")
		self.SetShutter(typ=0, mode="permanently closed", closingtime=0, openingtime=0)
		self.printout(message="Starting shut down procedure")
		self.SetTemperature(temperature=temperature)
		self.StabilizeTemperature()
		self.CoolerOFF()
		self.printout(message="Shutting down SDK")
		out = self.dll.ShutDown()
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])		



class OpAcquire(EMCCD):
	""" 
		Wraps the OpAcquire functionality
	"""

	param_type = dict()
	param_type.update({"mode_description": "str"})
	param_type.update({"output_amplifier": "str"})
	param_type.update({"frame_transfer": "str"})
	param_type.update({"readout_rate": "float"})
	param_type.update({"electron_multiplying_gain": "int"})
	param_type.update({"vertical_clock_amplitude": "int"})
	param_type.update({"preamplifier_gain": "int"})
	param_type.update({"shift_speed": "float"})


	def __init__(self, VERBOSE=True):
		super().__init__(VERBOSE=VERBOSE)


	def OA_Initialize(self, file=None):
		"""
			This function will initialise the OptAcquire settings from a Preset file and a User defined file if it exists.

		"""
		self.printout(message="OA: Initialing OpAcquire")
		if file == None:
			file = "MyFile.xml"
		cfile = (ctypes.c_char*len(file))()
		out = self.dll.OA_Initialize(ctypes.pointer(cfile), ctypes.c_ulong(len(file)))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		info = None

		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out]), info



	def OA_GetNumberOfPreSetModes(self):
		"""
			This function will return the number of modes defined in the Preset file. The Preset file must exist.

		"""
		self.printout(message="OA: Getting number of OpAcquire modes.")
		n_modes = ctypes.c_int()
		out = self.dll.OA_GetNumberOfPreSetModes(ctypes.pointer(n_modes))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
			info = n_modes.value
		else:
			SUCCESS = False
			info = None

		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out]), info



	def OA_GetPreSetModeNames(self):
		"""
			This function will return the available mode names from the Preset file. The mode and the Preset file must exist.
			The user must allocate enough memory for all of the acquisition parameters.

		"""
		self.printout(message="OA: Getting OpAcquire modes names")
		SUCCESS, message, n_modes = self.OA_GetNumberOfPreSetModes()
		if SUCCESS:
			array = (ctypes.c_char*(255*n_modes))()
			out = self.dll.OA_GetPreSetModeNames(ctypes.pointer(array))
			self.printout(code=out)
			if out == 20002:
				SUCCESS = True
				info = array.value.decode()
				info = info.split(",")[:-1]
			else:
				SUCCESS = False
				info = None
			message = self.emccd_return_codes[out]
		else:
			SUCCESS = False

		return SUCCESS, message, info



	def OA_GetNumberOfAcqParams(self, mode_name):
		"""
			This function will return the parameters associated with a specified mode. The mode must be present in either the Preset file or the User defined file.

			Parameters:
				mode_name (str):	Mode name

		"""
		self.printout(message="OA: Getting number of parameters associated with mode: "+mode_name)
		mode = ctypes.c_char_p(mode_name.encode())
		n = ctypes.c_int()
		out = self.dll.OA_GetNumberOfAcqParams(mode, ctypes.pointer(n))
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
			info = n.value
		else:
			SUCCESS = False
			info = None

		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out]), info



	def OA_GetModeAcqParams(self, mode_name):
		"""
			This function will return all acquisition parameters associated with the specified mode. 
			The mode specified by the user must be in either the Preset file or the User defined file.

			Parameters:
				mode_name (str):	Mode name

		"""
		self.printout(message="OA: Getting parameters for mode: "+mode_name)
		SUCCESS, message, n_params = self.OA_GetNumberOfAcqParams(mode_name=mode_name)
		if SUCCESS is True:
			mode = ctypes.c_char_p(mode_name.encode())
			params = (ctypes.c_char*(255*n_params))()
			out = self.dll.OA_GetModeAcqParams(mode, ctypes.pointer(params))
			self.printout(code=out)
			message = copy.deepcopy(self.emccd_return_codes[out])
			if out == 20002:
				SUCCESS = True
				info = params.value.decode()
				info = info.split(",")[:-1]
			else:
				SUCCESS = False
				info = None

			return SUCCESS, message, info



	def GetParamValue(self, mode_name, param_name):
		"""
			Grabs the value of the parameter "param_name", in the mode "mode_name"

			Parameters:
				mode_name (str)
				param_name (str)
		
		"""
		self.printout(message="OA: Getting parameter value")
		SUCCESS, message, params_list = self.OA_GetModeAcqParams(mode_name=mode_name)
		if SUCCESS:
			if not param_name in params_list:
				raise Exception("Invalid parameter name")
			else:
				mode = ctypes.c_char_p(mode_name.encode())
				param = ctypes.c_char_p(param_name.encode())
				param_type = self.param_type[param_name]
				if param_type == "str":
					value = (ctypes.c_char*255)()
					out = self.dll.OA_GetString(mode, param, ctypes.pointer(value), ctypes.c_ulong(255))
				elif param_type == "int":
					value = ctypes.c_ulong()
					out = self.dll.OA_GetInt(mode, param, ctypes.pointer(value))
				elif param_type == "float":
					value = ctypes.c_float()
					out = self.dll.OA_GetFloat(mode, param, ctypes.pointer(value))
				else:
					raise Exception("Coding error")
				self.printout(code=out)
				message = copy.deepcopy(self.emccd_return_codes[out])
				if out == 20002:
					SUCCESS = True
					if param_type == "str":
						info = value.value.decode()
					else:
						info = value.value
				else:
					SUCCESS = False
					info = None
		else:
			info = None
		return SUCCESS, message, info



	def OA_EnableMode(self, mode_name):
		"""
			This function will set all the parameters associated with the specified mode to be used for all subsequent acquisitions. 
			The mode specified by the user must be in either the Preset file or the User defined file.

			Parameters:
				mode_name (str)

		"""
		self.printout(message="OA: Setting mode to: "+mode_name)
		mode = ctypes.c_char_p(mode_name.encode())

		out = self.dll.OA_EnableMode(mode)
		self.printout(code=out)
		if out == 20002:
			SUCCESS = True
		else:
			SUCCESS = False
		return SUCCESS, copy.deepcopy(self.emccd_return_codes[out])


