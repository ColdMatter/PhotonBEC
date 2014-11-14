#modified by LZ to pass dll directory in setup functions for spectrometer and camera

from pylab import *
import pbec_analysis
#import pbec_data_format
import sys
import numpy
from scipy.misc import imsave

sys.path.append(pbec_analysis.control_root_folder + pbec_analysis.folder_separator+"camera")
sys.path.append(pbec_analysis.control_root_folder + pbec_analysis.folder_separator+"spectrometer")
sys.path.append(pbec_analysis.control_root_folder + pbec_analysis.folder_separator+"PythonPackages")
import pyflycap
import pyspectro
import SingleChannelAO, SingleChannelAI

def getLambdaRange(lamb, fromL, toL):
	assert(fromL <= toL)
	assert(fromL >= lamb[0])
	assert(toL <= lamb[-1])
	hi = 0 #this is a crap way of doing it but this function
	lo = 0 # isnt a bottleneck so the speed hit doesnt matter
	for i, v in enumerate(lamb):
		if v > fromL:
			lo = i
			break
	for i, v in enumerate(lamb):
		if v > toL:
			hi = i
			break
	return (hi, low)
	#return (
	#	int( (fromL - lamb[0]) * len(lamb) / (lamb[-1] - lamb[0]) ),
	#	int( (toL - lamb[0]) * len(lamb) / (lamb[-1] - lamb[0]) )
	#	)

class Spectrometer(object):

	instance = None
	pixelCount = 0
	lamb = None
	spectrum = None
	open = False
	

	def __new__(self, *args, **kwargs):
		if not self.instance: #makes it a singleton
			self.instance = super(Spectrometer, self).__new__(self, *args, **kwargs)
			#self.setup()
		return self.instance
		
	def setup(self):
		dllDirectory = pbec_analysis.control_root_folder + "\\spectrometer\\"
		if self.open:
			raise IOError("spectrometer is already setup")
		try:
			self.pixelCount = pyspectro.setupavs1(dllDirectory)
			self.lamb = numpy.array([0.1] * self.pixelCount)
			pyspectro.getlambda(self.lamb)
			self.open = True
		except Exception as e:
			self.close()
			raise e
	
	#lamb_range = None for the whole range
	#nMeasure = -1 for infinite measurements
	def start_measure(self, intTime, nAverage, nMeasure=-1, lamb_range=None):
		if not self.open:
			raise IOError("spectrometer has been close()d")
		try:
			pRange = (0, self.pixelCount - 1)
			if lamb_range != None:
				pRange = getLambdaRange(self.lamb, lamb_range[0], lamb_range[1])
			pyspectro.setupavs2(pRange, intTime, nAverage, nMeasure)
			self.spectrum = numpy.array([0.1] * (pRange[1] - pRange[0]+1))
		except Exception as e:
			self.close()
			raise e	
	
	def get_data(self):
		if not self.open:
			raise IOError("spectrometer has been close()d")
		try:
			timestamp = pyspectro.readavsspectrum(self.spectrum, 10000)
			#FIXME: background correction not inplace. Needs to be available.
			return self.spectrum
		except Exception as e:
			self.close()
			raise e
		
	def close(self):
		self.open = False
		#print("freeing avs spectro, hopefully this is always called")
		pyspectro.closeavs()

class __Camera(object):

	open = False
	imageData = None
	serialNumber = 0
	
	def __init__(self, serialNumber):
		self.serialNumber = serialNumber
		
	def setup(self):
		dllDirectory = pbec_analysis.control_root_folder + "\\camera\\"
		if self.open:
			raise IOError("camera is already setup")
		try:
			cam_info = pyflycap.setupflycap(self.serialNumber,dllDirectory)
			self.open = True
			keys = ("modelName", "vendorName", "sensorInfo",
				"sensorResolution", "firmwareVersion", "firmwareBuildTime")
			self.cam_info = dict(zip(keys, cam_info))
			return self.cam_info
		except Exception as e:
			self.close()
			#self.setup() #why did i put setup() here? isnt it an infinite loop
			raise e

	def get_image(self):
		if not self.open:
			#raise IOError("camera has been close()d")
			d = self.setup()
		try:
			(dataLen, row, col, bitsPerPixel) = pyflycap.getflycapimage()
			if self.imageData == None:
				self.imageData = numpy.arange(dataLen, dtype=numpy.uint8)
				#print("dataLen, row, col, BPP = " + str(dataTuple))
			pyflycap.getflycapdata(self.imageData)
			return numpy.reshape(self.imageData, (row, col, 3))
			#from scipy.misc import imsave
			#imsave("image.png", im)
		except Exception as e:
			self.close()
			#self.setup()
			raise e

	def close(self):
		self.open = False
		#print("freeing avs spectro, hopefully this is always called")
		pyflycap.closeflycap()
		#pyflycap.freelibrary()

#note: you can have many keys mapping to the same serial number
#so in the future "flea" "interferometer" "large chip" could all map to 14080462
serialNumber_cameraLabel_map = {"int_chameleon": 14110699, "chameleon": 12350594, "flea": 14080462, "grasshopper": 14110879}
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

def get_single_image_and_spectrum(cameraLabel, intTimeSpectrometer,nAverageSpectrometer=1):
	#Sequential. Would be better to run 2 threads
	lamb,spectrum = get_single_spectrum(intTimeSpectrometer,nAverage=nAverageSpectrometer)
	im = get_single_image(cameraLabel)
	ts = pbec_analysis.make_timestamp()
	return {"lamb":lamb,"spectrum":spectrum,"im":im,"ts":ts}
	
def get_multiple_images(cameraLabel, nImage=1):
	c = getCameraByLabel(cameraLabel)
	c.setup()
	im_list = []
	if nImage>3: print "Strongly advised against: too many images in memory"
	for i in range(nImage):
		im_list.append(c.get_image())
	c.close()
	return im_list