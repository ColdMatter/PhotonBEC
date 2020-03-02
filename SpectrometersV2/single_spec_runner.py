import sys
from socket import gethostname
if gethostname()=="ph-rnyman-01":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec5":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-jrodri10":
	sys.path.append("X:\\Control\\PythonPackages\\")
else:
	raise Exception('Unknown machine')

	
from pbec_experiment_multispec import * #Needed for spectrometer properties
import pbec_analysis_multispec
import threading
import traceback
import copy

import ctypes
from ctypes import pointer, c_char, sizeof, c_ushort, c_ubyte
from ctypes import c_bool, c_short, c_uint, c_int8
from ctypes import c_double, c_int, Structure, c_uint32, c_float
from time import sleep
from avantes_datatypes import SmoothingType, TriggerType, ControlSettingsType, avs_id, detector_type, meas_config_type


if gethostname()=="ph-photonbec3" or gethostname()=="ph-photonbec5":
	spectrometer_names = ['grey','newbie','black']
	spectrometer_number = 0 # right order is ['grey','newbie','black']. The order may change, keep checking


spectrometer_return_codes = dict()
spectrometer_return_codes.update({0: 'SUCCESS'})
spectrometer_return_codes.update({-1: 'INVALID_PARAMETER'})
spectrometer_return_codes.update({-2: 'OPERATION_NOT_SUPPORTED'})
spectrometer_return_codes.update({-3: 'DEVICE_NOT_FOUND'})
spectrometer_return_codes.update({-4: 'INVALID_DEVICE_ID'})
spectrometer_return_codes.update({-5: 'OPERATION_PENDING'})
spectrometer_return_codes.update({-6: 'TIMEOUT'})
spectrometer_return_codes.update({-7: 'reserved (shouldt occur)'})
spectrometer_return_codes.update({-8: 'INVALID_MEAS_DATA'})
spectrometer_return_codes.update({-9: 'INVALID_SIZE'})
spectrometer_return_codes.update({-10: 'INVALID_PIXEL_RANGE'})
spectrometer_return_codes.update({-11: 'INVALID_INT_TIME'})
spectrometer_return_codes.update({-12: 'INVALID_COMBINATION'})
spectrometer_return_codes.update({-13: 'reserved (shouldt occur)'})
spectrometer_return_codes.update({-14: 'NO_MEAS_BUFFER_AVAIL'})
spectrometer_return_codes.update({-15: 'UNKNOWN'})
spectrometer_return_codes.update({-16: 'COMMUNICATION'})
spectrometer_return_codes.update({-17: 'NO_SPECTRA_IN_RAM'})
spectrometer_return_codes.update({-18: 'INVALID_DLL_VERSION'})
spectrometer_return_codes.update({-19: 'NO_MEMORY'})
spectrometer_return_codes.update({-20: 'DLL_INITIALISATION'})
spectrometer_return_codes.update({-21: 'INVALID_STATE'})
spectrometer_return_codes.update({-100: 'INVALID_PARAMETER_NR_PIXEL'})
spectrometer_return_codes.update({-101: 'INVALID_PARAMETER_ADC_GAIN'})
spectrometer_return_codes.update({-102: 'INVALID_PARAMETER_ADC_OFFSET'})
spectrometer_return_codes.update({-110: 'INVALID_MEASPARAM_AVG_SAT2'})
spectrometer_return_codes.update({-111: 'INVALID_MEASPARAM_AVG_RAM'})
spectrometer_return_codes.update({-112: 'INVALID_MEASPARAM_SYNC_RAM'})
spectrometer_return_codes.update({-113: 'INVALID_MEASPARAM_LEVEL_RAM'})
spectrometer_return_codes.update({-114: 'INVALID_MEASPARAM_SAT2_RAM'})
spectrometer_return_codes.update({-115: 'INVALID_MEASPARAM_FWVER_RAM'})
spectrometer_return_codes.update({-116: 'INVALID_MEASPARAM_DYNDARK'})
spectrometer_return_codes.update({-120: 'NOT_SUPPORTED_BY_SENSOR_TYPE'})
spectrometer_return_codes.update({-121: 'NOT_SUPPORTED_BY_FW_VER'})
spectrometer_return_codes.update({-122: 'NOT_SUPPORTED_BY_FPGA_VER'})


class ctype_Spectrometer():
	
	def __init__(self, parent, index=0):
		self.parent_dll = parent.dll
		self.serial = parent.serials[index]
		self.handle = self.parent_dll.AVS_Activate(pointer(parent.avs_id_list[index]))
		num_pixels_temp = c_ushort()
		self.parent_dll.AVS_GetNumPixels(self.handle, pointer(num_pixels_temp))
		self.num_pixels = num_pixels_temp.value
		self.lamb_temp = (c_double*self.num_pixels)()
		self.spec_temp = (c_double*self.num_pixels)()
		self.spectrum_time_label_ctype = c_uint32()
		self.spectrum_time_label = None
		self.spectrum_new_data_flag = None
		self.external_trigger_flag = None
		self.parent_dll.AVS_GetLambda(self.handle, pointer(self.lamb_temp))
		self.lamb = [x for x in self.lamb_temp]
		self.spectrum = list(np.array(self.lamb)-np.array(self.lamb))
		self.allow_grabbing = False
		
		
	def start_measure(self, int_time, n_averages, continuous_mode_flag, n_measures):

		self.allow_grabbing = False

		##### Set up a measure configuration parameters
		self.continuous_mode_flag = continuous_mode_flag
		self.measureConfig = meas_config_type()
		self.measureConfig.m_StartPixel = c_ushort(0)
		self.measureConfig.m_StopPixel = c_ushort(self.num_pixels - 1)
		self.measureConfig.m_IntegrationTime = c_float(int_time)
		self.measureConfig.m_IntegrationDelay = c_uint(0)
		self.measureConfig.m_NrAverages = c_uint(n_averages)
		self.measureConfig.m_CorDynDark.m_Enable = c_ubyte(1)            # (0) means disable dark count correction, (1) enables it
		self.measureConfig.m_CorDynDark.m_ForgetPercentage = c_ubyte(50)  # (0-100) percentage of the new dark value pixels to use
		self.measureConfig.m_Smoothing.m_SmoothPix = c_ushort(1)
		self.measureConfig.m_Smoothing.m_SmoothModel = c_ubyte(0)
		self.measureConfig.m_SaturationDetection = c_ubyte(0)
		if self.external_trigger_flag is True and self.continuous_mode_flag is False:
			self.measureConfig.m_Trigger.m_Mode = c_ubyte(1)
			self.measureConfig.m_Trigger.m_Source = c_ubyte(0)       # (0) means source is external trigger rather than sync input (1) 
			self.measureConfig.m_Trigger.m_SourceType = c_ubyte(0)   # (0) means EDGE trigger rather than LEVEL (1)
		else:
			self.measureConfig.m_Trigger.m_Mode = c_ubyte(0)
			self.measureConfig.m_Trigger.m_Source = c_ubyte(0)       # (0) means source is external trigger rather than sync input (1) 
			self.measureConfig.m_Trigger.m_SourceType = c_ubyte(0)   # (0) means EDGE trigger rather than LEVEL (1)



		##### Cycles the preparation until it succeds. Some times fails
		control_flag = True
		while control_flag:
			self.err_prepare = self.parent_dll.AVS_PrepareMeasure(self.handle, pointer(self.measureConfig))
			print("     -> MESSAGE for measure preparation                 = "+spectrometer_return_codes[self.err_prepare])
			if not self.err_prepare == 0:
				sleep(0.05)
			else:
				control_flag = False


		##### Performs the measure
		if self.continuous_mode_flag is True:
			self.err_measure = self.parent_dll.AVS_Measure(self.handle, None, c_short(-1)) # last parameter is number of measures; -1 means infinity
			print("     -> MESSAGE for measure output                      = "+spectrometer_return_codes[self.err_measure])
			control_flag = True
			while control_flag:
				self.err_poll = self.parent_dll.AVS_PollScan(self.handle)
				if self.err_poll == 0:
					message = 'SUCCESS_DO_DATA_AVAILABLE'
					sleep(0.01)
				elif self.err_poll == 1:
					message = 'SUCCESS_DATA_AVAILABLE'
					control_flag = False
				else:
					message = spectrometer_return_codes[self.err_poll]
					sleep(0.01)
				print("     -> MESSAGE for spectrometer scan                   = "+message)
			self.allow_grabbing = True


		elif self.continuous_mode_flag is False:
			if n_measures is None:
				n_measures = 1
			for i in range(0, n_measures):
				self.err_measure = self.parent_dll.AVS_Measure(self.handle, None, c_short(1)) # last parameter is number of measures; -1 means infinity
				if n_measures == 1:
						print("     -> MESSAGE for measure output                      = "+spectrometer_return_codes[self.err_measure])
				control_flag = True
				while control_flag:
					self.err_poll = self.parent_dll.AVS_PollScan(self.handle)
					if self.err_poll == 0:
						message = 'SUCCESS_DO_DATA_AVAILABLE'
						sleep(0.001)
					elif self.err_poll == 1:
						message = 'SUCCESS_DATA_AVAILABLE'
						control_flag = False
					else:
						message = spectrometer_return_codes[self.err_poll]
						sleep(0.001)
					if n_measures == 1:
							print("     -> MESSAGE for spectrometer scan                   = "+message)
				self.get_data(internal_calling=True)
				self.stop_measure(verbose=False)	
				if i == 0:
					self.lock_single_measure_data(append_flag=False) # Saves the results of this single measure in a "safe" place to avoid override by an external call
				else:
					self.lock_single_measure_data(append_flag=True)
			self.combine_single_measure_data() # The combine procedure averages the different measures
			self.allow_grabbing = True
			print("-> Data from {0} measures retrieved".format(n_measures))


		
	def get_data(self, internal_calling=False):
		##### This function can be called outside the Spectrometer objects
		if (self.allow_grabbing == True and self.continuous_mode_flag==True) or internal_calling==True:
			control_flag = True
			while control_flag:	
				self.err_data = self.parent_dll.AVS_GetScopeData(self.handle, pointer(self.spectrum_time_label_ctype), pointer(self.spec_temp))
				#print("     -> MESSAGE for grabbing specrometer data           = "+spectrometer_return_codes[self.err_data])
				if not self.err_data == 0:
					sleep(0.001)
				else:
					control_flag = False
			self.spectrum = [x for x in self.spec_temp]
			if self.spectrum_time_label == self.spectrum_time_label_ctype.value:
				self.spectrum_new_data_flag = False
			else:
				self.spectrum_new_data_flag = True
			self.spectrum_time_label = self.spectrum_time_label_ctype.value
		else:
			pass

		return copy.deepcopy(self.spectrum_time_label), copy.deepcopy(self.spectrum_new_data_flag), copy.deepcopy(self.lamb), copy.deepcopy(self.spectrum)
		

	def lock_single_measure_data(self, append_flag=False):
		if append_flag is False:
			self.aux_spectrum_time_label = [copy.deepcopy(self.spectrum_time_label)]
			self.aux_spectrum_new_data_flag = [copy.deepcopy(self.spectrum_new_data_flag)]
			self.aux_spectrum = [copy.deepcopy(self.spectrum)]
		else:
			self.aux_spectrum_time_label.append(copy.deepcopy(self.spectrum_time_label))
			self.aux_spectrum_new_data_flag.append(copy.deepcopy(self.spectrum_new_data_flag))
			self.aux_spectrum.append(copy.deepcopy(self.spectrum))


	def combine_single_measure_data(self):
		
		self.spectrum = list(np.mean(np.array(self.aux_spectrum), 0))
		self.spectrum_time_label = copy.deepcopy(self.aux_spectrum_time_label[-1])
		self.spectrum_new_data_flag = copy.deepcopy(self.aux_spectrum_new_data_flag[-1])



	def stop_measure(self, verbose=True):
		self.allow_grabbing = False
		self.err_stop = self.parent_dll.AVS_StopMeasure(self.handle)
		if verbose:
				print("     -> MESSAGE for stop measure                        = "+spectrometer_return_codes[self.err_stop])


	def close(self):
		try:
			self.stop_measure()
		except:
			raise Exception("Brute force stopping")
		try:
			self.err_deactivate = self.parent_dll.AVS_Deactivate(self.handle)
			print("     -> MESSAGE for spectrometer deactivation           = "+spectrometer_return_codes[self.err_deactivate])
		except:
			raise Exception("Brute force stopping")
		


class SingleSpectrometer():

	def __init__(self, int_time, n_averages, continuous_mode_flag=True, external_trigger_flag=False):

		##### Some defaults
		self.external_trigger_flag = external_trigger_flag
		self.continuous_mode_flag = continuous_mode_flag
		self.spectrometer_name = spectrometer_names[spectrometer_number]
		self.bandwidth_throttle = 0.001 # slows down acquisition so other devices can use USB
		self.spec_int_time = int_time
		self.spec_n_averages = n_averages
		self.min_spec_int_time = min_int_time_spectrometerLabel_map[spectrometer_names[spectrometer_number]]
		
		##### Sets up the spectrometer
		self.dll = ctypes.WinDLL("D://Control/spectrometer/AS5216.dll")
		self.dll.AVS_Init(0) # '0' means connection will be established via USB
		self.num_spectrometers = self.dll.AVS_GetNrOfDevices()
		self.avs_id_list = (avs_id * self.num_spectrometers)()
		ctypes.memset(ctypes.addressof(self.avs_id_list), 0, ctypes.sizeof(self.avs_id_list))
		size = c_uint32(sizeof(avs_id))
		total_size = c_uint32(sizeof(avs_id * self.num_spectrometers))
		print("\n Found {0} devices\n".format(self.num_spectrometers))
		self.dll.AVS_GetList(c_uint(self.num_spectrometers*size.value),pointer(total_size),pointer(self.avs_id_list))
		self.serials = []
		for i in range(self.num_spectrometers):
			self.serials.append(self.avs_id_list[i].m_aSerialId)
		self.all_spectros = [ctype_Spectrometer(self,index=i) for i in range(self.num_spectrometers)]	

		##### Selects just one of all the found devices
		self.spectro = self.all_spectros[spectrometer_number]
		print("\n Using spectrometer called "+self.spectrometer_name+'\n')
		self.spectro.stop_measure()
		self.spectro.external_trigger_flag = self.external_trigger_flag

		
	def start_acquisition(self, n_measures=None):

		print('-> Trying to start acquisition...')
		try:
			if self.continuous_mode_flag is True:
				print('  -> Continuous measure initiated')
			else:
				print('  -> Single measure initiated')
			self.spectro.start_measure(self.spec_int_time, self.spec_n_averages, continuous_mode_flag=self.continuous_mode_flag, n_measures=n_measures)
		except Exception as e:
			print("*** Error starting acquisition, trying again ***")
			print(e)


	def set_external_trigger(self, external_trigger=False):
		self.external_trigger_flag = external_trigger
		self.spectro.external_trigger_flag = external_trigger
		if external_trigger == False:
			print('-> External trigger is deactivated')
		else:
			print('-> External trigger is activated')
		self.stop_acquisition()
		if self.continuous_mode_flag is True:
			self.start_acquisition()


	def stop_acquisition(self):
		self.spectro.stop_measure()
		

	def free_dll(self):
		libHandle = self.dll._handle
		del self.dll
		ctypes.windll.kernel32.FreeLibrary(libHandle)

