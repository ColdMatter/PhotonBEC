#Allows a single spectrometer to be used when multiple spectrometers are connected. Very crude. Much better using the multispectrometer server which uses ctypes. 
#Ctypes could be implemeted here, but the multispectrometer server makes this redundant.
#Also includes important spectrometer properties for multispec server.

from pylab import *
import pbec_analysis
import sys, time, traceback
import numpy
#from scipy.misc import imsave

sys.path.append(pbec_analysis.control_root_folder + pbec_analysis.folder_separator+"camera")
sys.path.append(pbec_analysis.control_root_folder + pbec_analysis.folder_separator+"multispectrometer")
#sys.path.append(pbec_analysis.control_root_folder + pbec_analysis.folder_separator+"spectrometer")
sys.path.append(pbec_analysis.control_root_folder + pbec_analysis.folder_separator+"PythonPackages")
sys.path.append(pbec_analysis.control_root_folder + pbec_analysis.folder_separator+"thorlabsapt")
#import pyflycap
#import pyspectro
dllDirectory = pbec_analysis.control_root_folder + "\\multispectrometer\\"
#pyspectro.setupdll(dllDirectory,0)
import SingleChannelAO, SingleChannelAI, LaserQuantum

import spectrometer_utils

def getLambdaRange(lamb, fromL, toL):
	return spectrometer_utils.get_lambda_range(lamb, fromL, toL)
	
serialNumber_spectrometerLabel_map = {"black": '1504174U1',
			"grey": '1301201U1',"newbie":'1709352U1'}
pixelCount_spectrometerLabel_map = {"black": 2048,
			"grey": 2068,"newbie":2048}
min_int_time_spectrometerLabel_map = {"black": 1.05,
			"grey": 2e-3,"newbie":1.05}

class Spectrometer(object):

	instance = None
	pixelCount = 0
	lamb = None
	spectrum = None
	open = False
	

	#def __new__(self, *args, **kwargs):
	#	if not self.instance: #makes it a singleton
	#		self.instance = super(Spectrometer, self).__new__(self, *args, **kwargs)
	#		#self.setup()
	#	return self.instance
		
	def __init__(self,do_setupavs=True,handle=1,name='mini_setup'):
		#Added 27/7/16 by RAN and BTW
		self.handle=handle
		self.name = name
		self.setup(do_setupavs)
		
	def setup(self,do_setupavs=True):
		#dllDirectory = pbec_analysis.control_root_folder + "\\spectrometer\\"
		#dllDirectory = pbec_analysis.control_root_folder + "\\multispectrometer\\"
		#dllDirectory = "Y:\\Control\\spectrometer_Ben_Learning_20170330\\"
		#print "dllDirectory is" + str(dllDirectory)
		if self.open:
			print("already open")
			pass #ADDED 28/8/14 by RAN
			#raise IOError("spectrometer is already setup")
		
		try:
			self.pixelCount = pixelCount_spectrometerLabel_map[self.name]
			self.serial = serialNumber_spectrometerLabel_map[self.name]
			if do_setupavs:
				self.handle = pyspectro.setupavs1(dllDirectory, self.handle, self.serial)
			self.lamb = numpy.array([0.1] * self.pixelCount)
			pyspectro.getlambda(self.lamb, self.handle)
			self.open = True
		except Exception as e:
			###self.close() #Commented out 28/8/14 by RAN
			raise e
			
	#lamb_range = None for the whole range
	#nMeasure = -1 for infinite measurements
	def start_measure(self, intTime, nAverage, nMeasure=-1, lamb_range=None):
		'''
		NOTE: cannot call Spectrometer.start_measure more than once without a close & re-setup phase
		'''
		if not self.open:
			raise IOError("spectrometer has been close()d")
		try:
			pRange = (0, self.pixelCount - 1)
			if lamb_range != None:
				pRange = getLambdaRange(self.lamb, lamb_range[0], lamb_range[1])
			print("Parameters for setupavs2 are: ",pRange, intTime, nAverage, nMeasure, self.handle)
			pyspectro.setupavs2(pRange, intTime, nAverage, nMeasure, self.handle)
			self.spectrum = numpy.array([0.1] * (pRange[1] - pRange[0]+1))
		except Exception as e:
			###self.close() #Commented out 28/8/14 by RAN
			raise e	
	
	def change_measure(self, intTime, nAverage, nMeasure=-1, lamb_range=None):
		pyspectro.stopavsmeasure(self.handle)
		self.start_measure(intTime, nAverage, nMeasure=-1, lamb_range=None)

			
	def get_data(self):
		if not self.open:
			raise IOError("spectrometer has been close()d")
		try:
			timestamp = pyspectro.readavsspectrum(self.spectrum, 10000,self.handle)
			#FIXME: background correction not inplace. Needs to be available.
			return self.spectrum
		except Exception as e:
			self.close()
			raise e
		
	def stop_measure(self):
		pyspectro.stopmeasure(self.handle)
	
	def close(self):
		self.open = False
		#print("freeing avs spectro, hopefully this is always called")
		pyspectro.closeavs(self.handle)
	
	def closedll(self):
		self.open = False
		#print("freeing avs spectro, hopefully this is always called")
		pyspectro.closedll(dllDirectory,self.handle)
	

CAMERA_PROPERTY_TYPE_MAPPING = {"brightness": 0, "auto_exposure": 1, "sharpness": 2, "white_balance": 3,
	"hue": 4, "saturation": 5, "gamma": 6, "iris": 7, "focus": 8, "zoom": 9, "pan": 10, "tilt": 11,
	"shutter": 12, "gain": 13, "trigger_mode": 14, "trigger_delay": 15, "frame_rate": 16, "temperature": 17}



class __Camera(object):

	open = False
	handle = -1
	imageData = None
	serialNumber = 0
	properties = None
	cam_info = None
	
	def __init__(self, serialNumber):
		self.serialNumber = serialNumber
		self.error = None
		
	def setup(self):
		self.error = None
		dllDirectory = pbec_analysis.control_root_folder + "\\camera\\"
		if self.open:
			#raise IOError("camera is already setup")
			return self.cam_info
		try:
			cam_info = pyflycap.setupflycap(self.serialNumber, dllDirectory)
			self.open = True
			keys = ("handle", "modelName", "vendorName", "sensorInfo",
				"sensorResolution", "firmwareVersion", "firmwareBuildTime")
			self.handle = cam_info[0]
			self.cam_info = dict(zip(keys, cam_info))
			return self.cam_info
		except Exception as exc:
			self.close()
			#self.setup() #why did i put setup() here? isnt it an infinite loop
			raise exc

	def get_image(self, verbose = False):
		self.__check_is_open()
		try:
			if verbose: print("_Camera.get_image: calling getflycapimage")
			(dataLen, row, col, bitsPerPixel) = pyflycap.getflycapimage(self.handle)
			if verbose: print('cam getimage = ' + str((dataLen, row, col, bitsPerPixel)))
			calcedDataLen = row*col*bitsPerPixel/8 #for some reason, this does not always equal dataLen
			if (self.imageData == None) or len(self.imageData) != calcedDataLen:
				self.imageData = numpy.arange(calcedDataLen, dtype=numpy.uint8)
				#print("rebuilding imageData handle=" + str(self.handle) +
				#	", dataLen, row, col, BPP = " + str((dataLen, row, col, bitsPerPixel)))
			if verbose: print("_Camera.get_image: calling getflycapdata")
			pyflycap.getflycapdata(self.handle, self.imageData)
			if verbose: print("_Camera.get_image: getflycapimage returned")
			return numpy.reshape(self.imageData, (row, col, 3))
			#from scipy.misc import imsave
			#imsave("image.png", im)
		except Exception as exc:
			self.close()
			if verbose: print("get_image(): " + repr(exc))
			self.error = exc 
			#raise exc #do not raise exceptions, just record the error and carry on blithely
			import traceback
			traceback.print_exc()
			return None
			
	
	def set_trigger_mode(self, enabled, software):
		self.__check_is_open()
		pyflycap.settriggermode(self.handle, enabled, software)
	def wait_for_trigger_ready(self):
		pyflycap.waitfortriggerready(self.handle)
	def fire_software_trigger(self):
		pyflycap.firesoftwaretrigger(self.handle)
	
	def get_image_now(self, verbose=False):
		
		#use the software trigger to get an image right now
		#for repeated calls its best to use settriggermode() at the start, call get_image() many times
		#and then use settriggermode() again to get it back to the same state
		
		if verbose: print("setting trigger mode..."),
		self.set_trigger_mode(True, True)
		if verbose: print("waiting for trigger ready..."),
		self.wait_for_trigger_ready()
		if verbose: print("setting trigger mode..."),
		self.fire_software_trigger()
		if verbose: print("getting image..."),
		#self.wait_for_trigger_ready() #11/5/2015: returns when camera is ready for a new trigger, i.e. has data in buffer.
		im = self.get_image(verbose = verbose)
		if verbose: print("re-setting trigger mode")
		self.set_trigger_mode(False, True)#reset trigger back to normal
		return im

	def set_property(self, property_name, value, auto=None):
		"""property_name has to be taken from CAMERA_PROPERTY_TYPE_MAPPING"""
		#TODO another parameter called autoManualMode=True/False which you then
		# set the appropriate index of prop
		self.__check_is_open()
		try:
			prop = pyflycap.getproperty(self.handle, CAMERA_PROPERTY_TYPE_MAPPING[property_name])
			prop[8] = value #index for absValue
			if auto!=None:
				prop[5]=int(auto)
			pyflycap.setproperty(self.handle, prop)
			time.sleep(0.5)
		except Exception as exc:
			self.close()
			traceback.print_exc()
			self.error = exc
	
	def extended_shutter_mode(self,shutter=10):
		self.__check_is_open()
		try:
			prop = pyflycap.getproperty(self.handle, CAMERA_PROPERTY_TYPE_MAPPING["frame_rate"])
			prop[5]=int(False) #autoManualMode -> False
			prop[4]=int(False) #onOff -> False
			pyflycap.setproperty(self.handle, prop)
			#
			prop = pyflycap.getproperty(self.handle, CAMERA_PROPERTY_TYPE_MAPPING["shutter"])
			prop[5]=int(False) #autoManualMode -> False
			prop[2]=int(True) #absControl -> True
			prop[8] = shutter #index for absValue
			pyflycap.setproperty(self.handle, prop)				
		except Exception as exc:
			self.close()
			traceback.print_exc()
			self.error = exc
		
	
	def get_all_properties(self):
		self.__check_is_open()
		property_struct_names = ("present", "absControl", "onePush",
			"onOff", "autoManualMode", "valueA", "valueB", "absValue")
		self.properties = {}
		#fill up self.properties as a dict with everything named
		for name, index in CAMERA_PROPERTY_TYPE_MAPPING.iteritems():
			prop = pyflycap.getproperty(self.handle, index)
			self.properties[name] = dict(zip(property_struct_names, prop[1:]))
		return self.properties
	
	def get_region_of_interest(self):
		"""Returns a list with 4 elements describing a rectangle of ROI"""
		#format7_conf_struct_names = ("offsetX", "offsetY", "width", "height", "pixelFormat")
		return pyflycap.getformat7config(self.handle)[:4]
		
	def set_region_of_interest(self, x, y, width, height):
		self.__check_is_open()
		#format7_info_struct_names = ("maxWidth", "maxHeight", "offsetHStepSize", "offsetVStepSize",
		#	"imageHStepSize", "imageVStepSize", "packetSize", "minPacketSize", "maxPacketSize")
		format7info = pyflycap.getformat7info(self.handle)
		x -= x % format7info[2]
		y -= y % format7info[3]
		width -= width % format7info[4]
		height -= height % format7info[5]
		if width > format7info[0] or height > format7info[1]:
			raise ValueError("width or height too large for the camera: " + str((width, height)))
		format7config = pyflycap.getformat7config(self.handle)
		#format7_conf_struct_names = ("offsetX", "offsetY", "width", "height", "pixelFormat")
		format7config[0:4] = [x, y, width, height]
		pyflycap.setformat7config(self.handle, format7config)
		self.imageData = None #force get_image() to make a new one of the right length
		
	def set_max_region_of_interest(self):
		self.__check_is_open()
		#format7_info_struct_names = ("maxWidth", "maxHeight", "offsetHStepSize", "offsetVStepSize",
		#	"imageHStepSize", "imageVStepSize", "packetSize", "minPacketSize", "maxPacketSize")
		format7info = pyflycap.getformat7info(self.handle)
		format7config = pyflycap.getformat7config(self.handle)
		#format7_conf_struct_names = ("offsetX", "offsetY", "width", "height", "pixelFormat")
		format7config[0] = 0
		format7config[1] = 0
		format7config[2] = format7info[0]
		format7config[3] = format7info[1]
		pyflycap.setformat7config(self.handle, format7config)
		self.imageData = None #force get_image() to make a new one of the right length
	
	def set_centered_region_of_interest(self, width, height):
		self.__check_is_open()
		#format7_info_struct_names = ("maxWidth", "maxHeight", "offsetHStepSize", "offsetVStepSize",
		#	"imageHStepSize", "imageVStepSize", "packetSize", "minPacketSize", "maxPacketSize")
		format7info = pyflycap.getformat7info(self.handle)
		format7config = pyflycap.getformat7config(self.handle)
		#format7_conf_struct_names = ("offsetX", "offsetY", "width", "height", "pixelFormat")
		format7config[0] = format7info[0]/2 - width/2
		format7config[1] = format7info[1]/2 - height/2
		format7config[2] = width
		format7config[3] = height
		pyflycap.setformat7config(self.handle, format7config)
		self.imageData = None #force get_image() to make a new one of the right length
		#self.set_region_of_interest(format7info[0]/2 - width/2, format7info[1]/2 - height/2, width, height)
			
	def close(self):
		self.open = False
		#print("freeing avs spectro, hopefully this is always called")
		pyflycap.closeflycap(self.handle)
		self.handle = -1
		#pyflycap.freelibrary()
		
	def __check_is_open(self):
		if not self.open:
			#raise IOError("camera has been close()d")
			self.setup()

#note: you can have many keys mapping to the same serial number
#so in the future "flea" "interferometer" "large chip" could all map to 14080462
#TODO this is copied to pbec_analysis, stop using this version in pbec_experiment
camera_pixel_size_map = {"int_chameleon": 3.75e-6, "chameleon": 3.75e-6,
			"flea": 4.8e-6, "grasshopper": 5.86e-6, "grasshopper_2d":5.86e-6, "minisetup_chameleon":1e-6} #Check minisetup_chameleon!!!

serialNumber_cameraLabel_map = {"chameleon": 15299245,
			"flea": 14080462, "grasshopper": 14110879,"grasshopper_2d":14435619, "minisetup_chameleon": 12350594}
def getCameraByLabel(label):
	number = 0
	if label != None:
		number = serialNumber_cameraLabel_map[label.lower()]
	return __Camera(number)




		
#---------------------------------
#SOME USEFUL FUNCTIONS
#----------------------------------
def get_single_spectrum(intTime,nAverage=1):
	"""
	intTime: integration time in ms
	nAverage: number of averages
	Typical usage: plot(*get_single_spectrum(200))
	"""
	s = Spectrometer()
	s.setup()
	s.start_measure(intTime,nAverage,1)
	spec = s.get_data()
	s.close()
	return s.lamb,s.spectrum

def get_single_image(cameraLabel):
	"""
	Uses parameters set by FlyCap GUI
	Typical usage: imshow(get_single_image())
	"""
	c = getCameraByLabel(cameraLabel)
	c.setup()
	im = c.get_image()
	c.close()
	return im

def get_single_image_and_spectrum(cameraLabel, intTimeSpectrometer, nAverageSpectrometer=1):
	#Sequential. Would be better to run 2 threads
	lamb,spectrum = get_single_spectrum(intTimeSpectrometer, nAverage=nAverageSpectrometer)
	im = get_single_image(cameraLabel)
	ts = pbec_analysis.make_timestamp()
	return {"lamb":lamb,"spectrum":spectrum,"im":im,"ts":ts}
	
def get_multiple_images(cameraLabel, nImage=1):
	c = getCameraByLabel(cameraLabel)
	c.setup()
	im_list = []
	if nImage>3: print("Strongly advised against: too many images in memory")
	for i in range(nImage):
		im_list.append(c.get_image())
	c.close()
	return im_list