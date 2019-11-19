#NOTE: Uses pi_controller class, which is currently based in "CavityLock" folder, but will be moved to PythonPackages
#This class re-uses a lot of code from /Control/CavityLock/stabiliser_class.py
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
else:
	raise Exception('Unknown machine')

	
from hene_utils import *
from pbec_experiment_multispec import * #Needed for spectrometer properties
import pbec_analysis_multispec
from pi_controller import PI_control
import threading
import traceback

import ctypes
from ctypes import pointer, c_char, sizeof, c_ushort
from ctypes import c_bool, c_short, c_uint, c_int8
from ctypes import c_double, c_int, Structure, c_uint32, c_float
from time import sleep
from avantes_datatypes import DarkCorrectionType, SmoothingType, TriggerType, ControlSettingsType, avs_id, detector_type, meas_config_type

#----------------------------------
#COMPUTER SPECIFIC SETTINGS HERE
if gethostname()=="ph-photonbec":
	default_spec_int_time = 20
	default_spec_nAverage = 1
	default_lamb_range = (540,610) #Restrict range analysed, which might make acquisition faster
elif gethostname()=="ph-photonbec2":
	default_spec_int_time = 40
	default_spec_nAverage = 1
	default_lamb_range = (555,585) #Restrict range analysed, which might make acquisition faster
elif gethostname()=="ph-photonbec3" or gethostname()=="ph-photonbec5":
	default_lamb_range = (540,600) #Restrict range analysed, which might make acquisition faster
	only_one_spec = False
	if only_one_spec:
		default_spec_n_averages = [1]
		default_no_spectrometers = 1
		spectrometer_list = ['newbie'] #These have to be correct and in the order that avs_spectro deems fit to open them.
		default_spec_int_times = [2]
	else:	
		default_spec_n_averages = [1,1,1]
		default_no_spectrometers = 3
		spectrometer_list = ['grey','newbie','black'] #These have to be correct and in the order that avs_spectro deems fit to open them.
		default_spec_int_times = [3,10,3]
	
#----------------------------------

class _MultiSpectrometerThread(threading.Thread):
	def __init__(self,parent):
		threading.Thread.__init__(self)
		self.parent=parent
		self.daemon = True
		self.running = False
		self.paused =False
		self.parent.results=[]

	def run(self):
		self.running = True
		parent = self.parent
		spectros = parent.spectros #assumes spectrometer is setup
		fail_num = 0
		spectrum_number = 0
		#try:
		while self.running:
			#why the double loop? so it can be paused and unpaused
			time.sleep(0.1) #when paused, while loop not going mental
			while not self.paused:
				#insert the controller actions here
				try:
					temp_spectum=[]
					for spectro in parent.spectros:
						spectro.get_data(parent.dll)
						spectro.ts = pbec_analysis.make_timestamp(3)
					print "Spectrum number = ", spectrum_number
					spectrum_number += 1
					#parent.spectrum = temp_spectrum #Split into two lines so parent.spectrum can be accessed by the graph
					#if parent.spectrum == None:
					#	print('get_data() == None in spectrometer_stabiliser_class.py')
					#------------------
					parent.ts = pbec_analysis.make_timestamp(3) #Don't update the ts if acquisition fails!
					fail_num = 0
				
				#except IOError:
				#	if fail_num < 4:
				#		time.sleep(1)
				#		fail_num+=1
				#	else:
				#		self.parent.start_acquisition()
				#		fail_num=0

				except Exception as e:
					traceback.print_exc()
					self.parent.error_message = e
					print "Spectrometer acquisition error. Re-using previous data"
					print "Error is ", e
					#self.parent.stop_acquisition()
					#self.parent.start_acquisition()
					#
				time.sleep(parent.bandwidth_throttle)
					
				#Update spectrometer integration time if need be
				#HERE BE BUGS: TEST PROPERLY PLEASE
				
				#Gather the outputs
				r = {"ts":parent.ts}
				if parent.print_frequency > 0:
					if len(parent.results) % parent.print_frequency == 0: 
						print r["ts"]
				#Now output a voltage from PI_controller
				parent.results.append(r)
				#Turn this into a reasonable-length buffer, rather than a dump
				buffer_len=2500 #minimum 2000 for GUI plot
				if len(parent.results)>buffer_len: 
					del parent.results[0]
		#finally:
		#	spectro.close()
		print("Finished\n")


class ctype_Spectrometer():
	def __init__(self,parent,index=0):
		self.serial = parent.serials[index]
		self.handle = parent.dll.AVS_Activate(pointer(parent.avs_id_list[index]))
		num_pixels_temp = c_ushort()
		parent.dll.AVS_GetNumPixels(self.handle, pointer(num_pixels_temp))
		self.num_pixels = num_pixels_temp.value
		self.lamb_temp = (c_double*self.num_pixels)()
		self.spec_temp = (c_double*self.num_pixels)()
		self.time_label = c_uint32()
		parent.dll.AVS_GetLambda(self.handle, pointer(self.lamb_temp))
		self.lamb = [x for x in self.lamb_temp] #Make a more pythonic array
		
		
	def start_measure(self, dll, int_time, n_averages):
		#SET UP MEASUREMENT CONFIGURATION
		self.measureConfig = meas_config_type()
		ctypes.memset(ctypes.addressof(self.measureConfig), 0, ctypes.sizeof(self.measureConfig))
		
		startPixel = c_ushort(0)
		stopPixel = c_ushort(self.num_pixels - 1)
		intTime = c_float(int_time)
		nAverages = c_uint32(n_averages)

		self.measureConfig.m_StartPixel = startPixel
		self.measureConfig.m_StopPixel = stopPixel
		self.measureConfig.m_IntegrationTime = intTime
		self.measureConfig.m_IntegrationDelay = 1
		self.measureConfig.m_NrAverages = nAverages
		self.measureConfig.m_CorDynDark.m_Enable = "0"
		n_measure = c_short(-1) #Number of measurements to make. -1 means infintity.

		self.err_prepare = dll.AVS_PrepareMeasure(self.handle, pointer(self.measureConfig))
		print "Prepare meaure error  = ", self.err_prepare
		self.err_measure = dll.AVS_Measure(self.handle, None, n_measure)
		print "AVS_Measure error = ", self.err_measure
		poll_sleep_time = n_averages*int_time*1.5e-3 + 0.5
		#poll_sleep_time = int_time*1.5e-3
		sleep(poll_sleep_time)
		self.err_poll = dll.AVS_PollScan(self.handle)
		print "0 means no new data, 1 means new data. We have ->", self.err_poll
		
	def get_data(self,dll):
		err_data = err_data = dll.AVS_GetScopeData(self.handle,pointer(self.time_label),pointer(self.spec_temp))
		self.spectrum = [x for x in self.spec_temp]
		
	def stop_measure(self,dll):
		dll.AVS_StopMeasure(self.handle)

	
	def close(self, dll):
		try:
			dll.AVS_StopMeasure(self.handle)
		finally:
			dll.AVS_Deactivate(self.handle)
		
class MultiSpectrometers():
	def __init__(self, do_setup=True):
		self.error_message = None
		self.bandwidth_throttle=0.001 #slows down acquisition so other devices can use USB
		self.print_frequency =0#for diagnostic purposes
		self.spec_int_times = default_spec_int_times
		self.spec_n_averages = default_spec_n_averages
		self.lamb_range	 = default_lamb_range
		self.min_spec_int_times = [min_int_time_spectrometerLabel_map[name] for name in spectrometer_list]
		
		if do_setup:
			self.dll = ctypes.WinDLL("D://Control/spectrometer/AS5216.dll")
			self.dll.AVS_Init(0)
			self.num_spectrometers = self.dll.AVS_GetNrOfDevices()
			self.avs_id_list = (avs_id * self.num_spectrometers)()
			ctypes.memset(ctypes.addressof(self.avs_id_list), 0, ctypes.sizeof(self.avs_id_list))

			size = c_uint32(sizeof(avs_id))
			total_size = c_uint32(sizeof(avs_id * self.num_spectrometers))
			print self.num_spectrometers, " devices found"

			self.dll.AVS_GetList(c_uint(self.num_spectrometers*size.value),pointer(total_size),pointer(self.avs_id_list))
			
			self.serials = []
			self.device_mapping = {}
			self.statuses = []
			for i in range(self.num_spectrometers):
				self.serials.append(self.avs_id_list[i].m_aSerialId)
				self.device_mapping.update({self.avs_id_list[i].m_aSerialId:i})
				self.statuses.append(self.avs_id_list[i].m_Status)
		
		#--------------------
		self.results = []
		#self.lamb, self.spectrum = [],[]
		self.ts = None
		self.spectros = [ctype_Spectrometer(self,index=i) for i in range(self.num_spectrometers)]
		buffer_length=10 #
		self.initialise_thread()
			
	def initialise_thread(self):
		self.thread = _MultiSpectrometerThread(self) #don't start the thread until you want to acquire
		self.thread.paused=True
		self.thread.start()
		
	def start_acquisition(self):
		#self.spectro.setup() #This step is really slow
		try:
			for i,spectro in enumerate(self.spectros):
				spectro.start_measure(self.dll, self.spec_int_times[i], self.spec_n_averages[i])
				spectro.get_data(self.dll)
		except IOError:
			self.stop_acquisition()
			self.start_acquisition()
		#self.lamb = copy(self.spectros[0].lamb)
		self.thread.paused=False
		
	def stop_acquisition(self):
		self.thread.paused=True
		time.sleep(0.5)#avoid race condition. Should really use mutex
		for spectro in self.spectros:
			spectro.stop_measure(self.dll)
		#spectros[-1].closedll()
		
	def close_acquisition(self):
		self.stop_acquisition()
		self.thread.running=False
		
	def free_dll(self):
		libHandle = self.dll._handle
		del self.dll
		ctypes.windll.kernel32.FreeLibrary(libHandle)

