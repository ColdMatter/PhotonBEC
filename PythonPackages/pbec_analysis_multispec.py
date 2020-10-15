#Utilities for data analysis on Photon BEC experiment
#heavily added to and some names changed by JM 1/4/2014
from socket import gethostname
import time, datetime
import os
import csv
import json
from pylab import *
from scipy.interpolate import interp1d
from scipy import constants
from numbers import Number
import zipfile
import io
#from numpy import ones

#pbec_prefix = "pbec" #TO OVERRIDE THE pbec_prefix, DO THIS,FOR EXAMPLE:
#>>>> import pbec_analysis
#>>>> pbec_analysis.pbec_prefix = "mini"
point_grey_chameleon_pixel_size = 3.75e-6
point_grey_grasshopper_pixel_size = 5.86e-6
point_grey_flea_pixel_size = 4.8e-6

interferometer_piezo_calibration_nm_movement_per_volt = 294.1 #see lab book 24/11/2014

#note: you can have many keys mapping to the same serial number
#so in the future "flea" "interferometer" "large chip" could all map to 14080462
camera_pixel_size_map = {"int_chameleon": 3.75e-6, "chameleon": 3.75e-6,
			"flea": 4.8e-6, "grasshopper": 5.86e-6, "grasshopper_2d":5.86e-6}


hostname = gethostname()
if gethostname()=="ph-rnyman-01":
	#ph-photonbec is also carries the name "ph-rnyman-01". Bah.
	data_root_folder = "D:\\Data"
	control_root_folder = "D:\\Control"
	folder_separator="\\"
	pbec_prefix = "pbec"
elif gethostname()=="ph-photonbec2": #laptop
	#data_root_folder = "C:\\photonbec\\Data"
	control_root_folder = "C:\\photonbec\\Control"
	data_root_folder = "Y:\\Data"
	#control_root_folder = "Y:\\Control"
	folder_separator="\\"
	pbec_prefix = "mini"
elif gethostname()=="ph-rnyman":
	#only works for data that has been backed up to the local d_drive
	data_root_folder = "/home/d_drive/Experiment/photonbec/Data"
	#data_root_folder = "/run/user/1001/gvfs/ftp:host=ph-photonbec.qols.ph.ic.ac.uk/Data"
	#data_root_folder = "./Data"
	control_root_folder = "/home/d_drive/Experiment/photonbec/Control"
	folder_separator="/"
	pbec_prefix = "pbec"
elif gethostname()=="ph-rnyman2":
	#only works for data that has been backed up to the local d_drive
	data_root_folder = "/home/d_drive/Experiment/photonbec/Data"
	#data_root_folder = "./Data"
	control_root_folder = "/home/d_drive/Experiment/photonbec/Control"
	folder_separator="/"
	pbec_prefix = "pbec"
elif gethostname()=="Potato3":
	#only works for data that copied to correct part of Temp folder
	data_root_folder =  "C:\\stuff\\temp\\Imperial_PhotonBEC\\Data\\"
	control_root_folder = "C:\\stuff\\temp\\Imperial_PhotonBEC\\Control_partial\\"
	folder_separator="\\"
	pbec_prefix = "pbec"
elif gethostname()=="ph-photonbec3":
	data_root_folder = "D:\\Data"
	control_root_folder = "D:\\Control"
	folder_separator="\\"
	pbec_prefix = "pbec"
elif gethostname()=="ph-photonbec5":
	data_root_folder = "D:\\Data"
	control_root_folder = "D:\\Control"
	folder_separator="\\"
	pbec_prefix = "pbec"
else:
	pbec_prefix = "pbec"
	folder_separator = os.sep
	test_dirs = ["Analysis", "analysis", "Data", "data"] #coded 01/4/14 by JM, with luck should work anywhere
	pathlist = os.getcwd().split(os.sep)
	found = False
	for t in test_dirs:
		try:
			i = pathlist.index(t)
			found = True
			pathlist[i] = "Data"
			data_root_folder = os.sep.join(pathlist[:6])
		except ValueError:
			pass
	if not found:
		print("failed to find data root folder")
		

#pbec_prefix can be overridden by defining the variable pbec_prefix_override before importing pbec_analysis
import __main__
try:
    pbec_prefix = __main__.pbec_prefix_override
except:
    pass
#
# physics / photon bec specific functions
#

kB = 0
try:
	kB = constants.Bolzmann
except AttributeError:
	pass
try:
	kB = constants.Boltzmann
except AttributeError:
	pass

def number_distn(lam, lam0, T, amplitude, mu, offset):
	"""
	Calculation of expected number vs energy for thermalised photons
	uses bose-einstein distribution, or boltzmann distribution if mu=0
	
	equations taken from 201404_normalising_be_distn.pdf
	"""
	#lam: wavelength
	#lam0: cutoff wavelengths, corresponding to minimum accesible energy
	ll = lam0 / lam
	const = constants.h * constants.c / lam0
	DoS = const * (ll-1) * (ll>1) #returns zero for energies below cutoff, lam0
	de_dlam = (const / lam0) * (ll**2) #a minus sign, deliberately dropped here
	#####boltz_distn = exp(-const*(ll-1)/(constants.Bolzmann*T) )
	boltz_distn = exp(-const*(ll-1)/(kB*T) )
	bose_einstein_distn = 1.0/ (exp(+(const*(ll-1) - mu)/(kB*T) )  -1)
	#Choose: Boltzmann or Bose-Einstein distribution
	distn = bose_einstein_distn
	if mu == 0:
		distn = boltz_distn
	num = amplitude*DoS*distn*de_dlam
	return num/constants.h + offset

def number_dist_log_residuals(pars, ydata, xdata):
	#Takes 5 parameters. Calculated residuals in log space
	#"number_distn" is to be found in pbec_analysis
	#Setting mu=0 returns the Boltzmann distribution
	(lam0, T, amplitude, offset) = pars
	mu=0
	pars = (lam0, T, amplitude, mu, offset)
	return (log(number_distn(xdata, *pars)) - log(ydata))**2

#
# Timestamp manipulation functions
#

def make_timestamp(precision=0):
	"""
	Returns timestamp string that represents the current time
	Precision is number of decimal places to add after the seconds
	"""
	#Outputs time stamp in format YYYYMMDD_hhmmss
	t = time.localtime()
	d = time.time()%1 #decimal places. May be needed later
	YYYY = str(t.tm_year)
	MM= str(100+t.tm_mon)[-2:] #pre-pends zeroes where needed
	DD = str(100+t.tm_mday)[-2:]
	hh = str(100+t.tm_hour)[-2:]
	mm = str(100+t.tm_min)[-2:]
	ss = str(100+t.tm_sec)[-2:]
	l=[YYYY,MM,DD,"_",hh,mm,ss]
	if precision<0:
		print("For backwards compatibility, the timestamp will include seconds anyway")
	elif precision>0:
		d = time.time()%1
		d_str=str(d)[2:2+int(round(precision))]
		l.append("_")
		l.append(d_str)
		#timestamp format YYMMDD_hhmmss_dddd with "precision" digits in place of "dddd" 
	return "".join(l) #JM: could be rewritten using time format strings, YYYYMMDD_hhmmss etc

def datafolder_from_timestamp(ts=make_timestamp(),make=False):
	"""
	Returns the name of the correct folder to save data.
	If folder does not exist, makes it and higher level folders as needed.
	"""
	folder_day = ts.split("_")[0]
	folder_month=folder_day[:-2]
	folder_year=folder_month[:-2]
	#Yearly folders
	year_folder = data_root_folder+folder_separator+folder_year
	if (os.listdir(data_root_folder).count(folder_year)==0) & make:
		os.mkdir(year_folder)
	#
	#Monthly folders
	month_folder = year_folder+folder_separator+folder_month
	if (os.listdir(year_folder).count(folder_month)==0) & make:
		os.mkdir(month_folder)
	#
	#Daily folders
	day_folder = month_folder+folder_separator+folder_day
	if (os.listdir(month_folder).count(folder_day)==0) & make:
		os.mkdir(day_folder)

	return day_folder+folder_separator

def timestamp_to_filename(ts,file_end=".txt",make_folder= False):
	return datafolder_from_timestamp(ts,make=make_folder)+pbec_prefix+"_"+ts+file_end

def time_from_timestamp(ts):
    return ts.split("_")[1]

def date_from_timestamp(ts):
    return ts.split("_")[0]

def timestamp_from_filename(filename):
    #intermediate = filename.split(folder_separator)[-1].split(".")[0].split(pbec_prefix+"_")
    #return intermediate[0][:15]#15 characters for YYYYMMDD_HHMMSS
    select_index= 1
    if filename.count(pbec_prefix): select_index=2 #test me!
    [date,time]=filename.split(".")[0].split("_")[select_index-1:select_index+1]
    return date+"_"+time


def time_from_filename(filename):
    return time_from_timestamp(timestamp_from_filename(filename))


def timestamps_in_range_single_day(first_ts, last_ts, extension=".json"):
	foldername = datafolder_from_timestamp(first_ts)
	first_time = time_from_timestamp(first_ts)
	last_time = time_from_timestamp(last_ts)
	ls = os.listdir(foldername)
	file_list = [s for s in ls if s.lower().endswith(extension.lower())] #filters by extension; case insensitive
	#Strip any preceding pbec_prefixes if necessary
	file_list_cropped = [f.split(pbec_prefix+"_")[0] if f.split("_")[0]!=pbec_prefix else f.split(pbec_prefix+"_")[1] for f in file_list]
	#
	ts_list = [s.lower().split(extension.lower())[0] for s in file_list_cropped]
	selected_ts_list = [ts for ts in ts_list if ((ts<=last_ts)&(ts>=first_ts))]
	all_files = [foldername+s for s in selected_ts_list]
	return selected_ts_list

def data_files_in_range_single_day(first_ts,last_ts,extension = ".json"):
	foldername = datafolder_from_timestamp(first_ts)
	first_time = time_from_timestamp(first_ts)
	last_time = time_from_timestamp(last_ts)
	ls = os.listdir(foldername)
	full_file_list = [s for s in ls if s.lower().endswith(extension.lower())] #filters by extension; case insensitive
	selected_file_list = [f for f in full_file_list if (timestamp_from_filename(f)>=first_ts)&(timestamp_from_filename(f)<=last_ts)]
	#filters by extension; case insensitive
	#
	#foldername = datafolder_from_timestamp(first_ts)
	#selected_ts_list = timestamps_in_range_single_day(first_ts, last_ts, extension)
	#DETECT CORRECT FULL FILENAME, WITH OR WITHOUT pbec_prefix
	#return [foldername + s + extension for s in selected_ts_list]
	return selected_file_list

def data_files_in_range(first_ts,last_ts,extension=".json"):
	#Untested if data span more than one month, or year
	if date_from_timestamp(first_ts)==date_from_timestamp(last_ts):
		df= data_files_in_range_single_day(first_ts, last_ts, extension=extension)
	else:
		df = []
		[first_date,last_date] = map(date_from_timestamp,[first_ts,last_ts])
		#detect all days in range, find all possible data files for each date, within range, etc...
		#explicitly assumes only one month is relevant
		month = first_date[:6] #date format YYYYMMDD
		month_folder = datafolder_from_timestamp(first_ts).rsplit(folder_separator,2)[0]+folder_separator
		all_dates_in_month = os.listdir(month_folder)
		selected_dates_in_month = [m for m in all_dates_in_month if (m>=first_date)&(m<=last_date)]
		for date in selected_dates_in_month:
			start_ts=date+"_000000"
			end_ts =date+"_235959"
			if date==first_date: start_ts = first_ts
			if date==last_date: end_ts = last_ts
			df+=data_files_in_range_single_day(start_ts, end_ts, extension=extension)
		#===might be useful in future
		#year_folder = month_folder.rsplit(folder_separator,2)[0]+folder_separator
		#all_folder = data_root_folder
	return df


def timestamps_in_range(first_ts, last_ts, extension=".json"):
    df_list = data_files_in_range(first_ts,last_ts,extension=extension)
    ts_list = map(timestamp_from_filename,df_list)
    return ts_list
    
def timestamp_to_datetime(ts):
    return datetime.datetime.strptime(ts, "%Y%m%d_%H%M%S")
    
def exclude_timestamps(ts_list, excluded_range):
	'''
	Exclude timestamps in ts_list. Extended_range is a tuple with the first
	and last timestamp to be excluded, or a list of such tuples.
	'''
	if not isinstance(excluded_range, list):
		excluded_range = [excluded_range]
	result = ts_list
	for e in excluded_range:
		first = timestamp_to_datetime(e[0])
		last = timestamp_to_datetime(e[1])
		result = [ts for ts in result if first > timestamp_to_datetime(ts) or timestamp_to_datetime(ts) > last]
	return result

def save_image_set(im_list, ts=None, file_end=''):
	if ts == None:
		ts = make_timestamp()

	zip_buffer = io.BytesIO()
	zip_fd = zipfile.ZipFile(zip_buffer, 'w')
	for i, im in enumerate(im_list):
		im_buf = io.BytesIO()
		imsave(im_buf, im, format='png')
		zip_fd.writestr('image%03d.png' % (i), im_buf.getvalue())
	zip_fd.close()
	
	zip_filename = timestamp_to_filename(ts, file_end, True)
	zip_file = open(zip_filename, 'wb')
	zip_file.write(zip_buffer.getvalue())
	zip_file.close()

def load_image_set(ts, file_end=''):
	zip_filename = timestamp_to_filename(ts, file_end)
	zip_fd = zipfile.ZipFile(zip_filename, 'r')
	im_list = []
	for name in zip_fd.namelist():
		im_bytes = zip_fd.read(name)
		im_buffer_fd = io.BytesIO(im_bytes)
		im = imread(im_buffer_fd)
		im_list.append(im)

	zip_fd.close()
	return im_list
    
#-------------------------
#CLASSES TO HELP ORGANISE DATA, BOTH FOR ANALYSIS AND FOR INITIAL DATA SAVING

#holds a certain type of experiment data
#this class knows how to save and load itself
class ExperimentalData(object):
	def __init__(self, ts, extension,data=None):
		self.ts = ts
		self.extension = extension
		if data!=None:
			self.setData(data)
		else:
			self.setData(None)
	def getFileName(self, make_folder = False):
		return timestamp_to_filename(self.ts, file_end = self.extension,
			make_folder = make_folder)

	#a lot of the time you wont use this function
	# d.lamb and d.spectrum are examples when you dont
	#one day we'll combine lamb and spectrum into one
	# variable using zip()
	def setData(self, data):
		self.data = data
	def saveData(self):
		raise Exception('called an abstract method')
	def loadData(self, load_params):
		raise Exception('called an abstract method')
	def copy(self):
		raise Exception('called an abstract method')

class CameraData(ExperimentalData):
	def __init__(self, ts, extension='_camera.png',data=None):
		ExperimentalData.__init__(self, ts, extension,data=data)
	def saveData(self):
		filename = self.getFileName(make_folder=True)
		imsave(filename, self.data)
	def loadData(self, load_params):
		filename = self.getFileName()
		self.data = imread(filename)
	def copy(self):
		d = CameraData(self.ts)
		d.data = self.data.copy()
		return d

class SpectrometerData(ExperimentalData):
	def __init__(self, ts, extension='_spectrum.json'):
		ExperimentalData.__init__(self, ts, extension=extension)
	def saveData(self):
		d = {"ts": self.ts, "lamb": list(self.lamb), "spectrum": list(self.spectrum)}
		filename = self.getFileName(make_folder=True)
		js = json.dumps(d, indent=4)
		fil = open(filename, "w")
		fil.write(js)
		fil.close()	
	def loadData(self, load_params, correct_transmission=True, shift_spectrum="spherical",mirrorTransmissionFunc=None):
		###this is borderline backwards compatible
		filename = self.getFileName()
		fil = open(filename, "r")
		raw_json = fil.read()
		fil.close()
		decoded = json.loads(raw_json)
		self.__dict__.update(decoded)
		self.lamb = array(self.lamb)
		self.spectrum = array(self.spectrum)
		if mirrorTransmissionFunc==None:
			#modified 25/3/2016 by RAN
			mirrorTransmissionFunc = UltrafastMirrorTransmission
		if (load_params != None and load_params['spectrum_correct_transmission']) or (load_params == None and correct_transmission):
			transmissions = mirrorTransmissionFunc(self.lamb, shift_spectrum=load_params['spectrum_shift_spectrum'])
			self.spectrum = self.spectrum / transmissions	
	def copy(self):
		d = SpectrometerData(self.ts)
		d.lamb = self.lamb.copy()
		d.spectrum = self.spectrum.copy()
		return d
		
class InterferometerFringeData(ExperimentalData):
	def __init__(self, ts, extension='_fringes.zip'):
		ExperimentalData.__init__(self, ts, extension)
		self.data=None
	def saveData(self):
		if self.data!=None:
			save_image_set(self.data, self.ts, self.extension)
		else:
			print("pbec_analysis.InterferometerFringeData warning: .data nonexistent, hence not saved")
	def loadData(self, load_params):
		self.data = load_image_set(self.ts, self.extension)
	def copy(self):
		c = InterferometerFringeData(self.ts)
		if self.data != None:
			c.data = self.data.copy()
		return c

class InterferometerSpectrometerFringeData(ExperimentalData):
	def __init__(self, ts, extension='_spec_fringes.json'):
		ExperimentalData.__init__(self, ts, extension)
		self.spectra=None
		self.lamb=None
		self.fine_position_volts=None
	def saveData(self):
		#TODO: make sure it can handle 2D arrays, or lists of arrays
		d = {"ts": self.ts, "lamb": list(self.lamb), "spectra": list(self.spectra),"fine_position_volts":list(self.fine_position_volts)}
		filename = self.getFileName(make_folder=True)
		js = json.dumps(d, indent=4)
		fil = open(filename, "w")
		fil.write(js)
		fil.close()
	def loadData(self, load_params, correct_transmission=True, shift_spectrum="spherical",mirrorTransmissionFunc=None):
		#TODO: load some data.
		filename = self.getFileName()
		fil = open(filename, "r")
		raw_json = fil.read()
		fil.close()
		decoded = json.loads(raw_json)
		self.__dict__.update(decoded)
		self.lamb = array(self.lamb)
		self.spectra = array(self.spectra)
		self.fine_position_volts = array(self.fine_position_volts)
		if mirrorTransmissionFunc==None:
			#modified 25/3/2016 by RAN
			mirrorTransmissionFunc = UltrafastMirrorTransmission
		if (load_params != None and load_params['spectrum_correct_transmission']) or (load_params == None and correct_transmission):
			transmissions = mirrorTransmissionFunc(self.lamb, shift_spectrum=load_params['spectrum_shift_spectrum'])
			#FOLLOWING LINE IS UNTESTED
			for s in list(self.spectra):
				s = s/transmissions
			#self.spectrum = self.spectrum / transmissions	

	def copy(self):
		c = InterferometerSpectrometerFringeData(self.ts)
		for arr in [self.fine_position_volts,self.lamb,self.spectra]:
			if self.arr != None:
				c.arr = self.arr.copy()
		return c
class DAQData(ExperimentalData):
	def __init__(self, ts, extension='_daq.json', data=None, rate=1e4, channel="ai0", minval=0.0, maxval=3.5):
		ExperimentalData.__init__(self, ts, extension, data=data)
		self.rate = rate
		self.channel = channel
		self.minval = minval
		self.maxval = maxval
	def saveData(self):
		d = {"ts": self.ts, "rate_s_per_sec": self.rate, "minval_V": self.minval, "maxval_V": self.maxval,
			"data": list(self.data)}
		filename = self.getFileName(make_folder=True)
		js = json.dumps(d, indent=4)
		fil = open(filename, "w")
		fil.write(js)
		fil.close()
	def loadData(self, load_params):
		filename = self.getFileName()
		fil = open(filename, "r")
		raw_json = fil.read()
		fil.close()
		decoded = json.loads(raw_json)
		self.__dict__.update(decoded)
		self.data = array(self.data)
	def copy(self):
		d = DAQData(self.ts, rate=self.rate, channel=self.channel, minval=self.minval, maxval=self.maxval)
		d.data = self.data.copy()
		return d

class MetaData():
	def __init__(self, ts, parameters={}, comments=""):
		self.ts = ts
		self.parameters=parameters
		self.comments=""
		self.fileExtension ="_meta.json"
		self.errors = ""
		self.dataset={} #intended to be a dictionary: keys are data names, values are tuples (Class (as string), filename)
	def copy(self):
		c = MetaData(self.ts, comments = self.comments)
		c.parameters=self.parameters.copy()
		c.fileExtension = self.fileExtension
		c.errors = self.errors
		return c
	def getFileName(self,make_folder = False):
		return timestamp_to_filename(\
			self.ts, file_end=self.fileExtension, make_folder=make_folder)
	def save(self):
		d = {"ts":self.ts, "parameters":self.parameters, "comments":self.comments, "errors": self.errors,"dataset":self.dataset}
		filename = self.getFileName(make_folder=True)
		js = json.dumps(d,indent=4)
		fil = open(filename,"w")
		fil.write(js)
		fil.close()
	def load(self):
		filename = self.getFileName()
		fil = open(filename,"r")
		raw_json = fil.read()
		fil.close()
		decoded = json.loads(raw_json)
		self.__dict__.update(decoded)
	def printMe(self,prefix="\t"):
		print(prefix + "timestamp: "+self.ts)
		print(prefix + "parameters: "+str(self.parameters))
		print(prefix + "comments: "+self.comments)
		print(prefix + "errors: " + self.errors)

class ExperimentalDataSet():
	'''
	to analyse, construct this class with the right timestamp and call loadAllData()
	then use ExperimentalDataSet.dataset['your data'].data
	'''
	def __init__(self, ts=None):
		if ts==None:
			ts = make_timestamp()
		self.ts = ts
		self.dataset = {}
		self.meta = MetaData(ts = self.ts)
	def copy(self):
		c = ExperimentalDataSet(ts=self.ts)
		c.meta = self.meta.copy() #remember to copy sub-objects
		import copy
		c.dataset = copy.deepcopy(self.dataset)
		#for name in self.dataset:
			#print 'name = ' + str(name)
			#c.dataset[name] = self.dataset[name].copy()
		#for name, data in self.dataset.iteritems():
		#	print 'name, data = ' + str(name) + ', ' + str(data)
		#	c.dataset[name] = data.copy()
		return c
	def saveAllData(self):
		for data in self.dataset.values():
			data.saveData()
		#
		self.meta.dataset=dict([(k,(v.__class__.__name__,v.extension)) for k,v in self.dataset.iteritems()])
		self.meta.save()
	def constructDataSet(self):
		#does not load actual data, only contructs ExperimentalData objects, ready for loading
		self.meta.load()
		for (data_name,(data_class, extension)) in self.meta.dataset.iteritems():
			self.dataset[data_name]=eval(data_class+"('"+self.ts+"', extension ='"+extension+"')")
	def loadAllData(self, load_params=None):
		#Should really try...except...finally
		self.constructDataSet()
		for data in self.dataset.values():
			data.loadData(load_params)




# file format functions
#
#def read_spectrometer_data(data_file, transmission_correct=False, shift_spectrum="planar"):
#TODO: update with new spectrometer data format, i.e. using Experiment class
def read_spectrometer_data(ts,transmission_correct=False,shift_spectrum="spherical"):
	#Currently untested replacement for previous version
	ex = Experiment(ts)
	ex.loadSpectrometerData(correct_transmission=transmission_correct, shift_spectrum=shift_spectrum)
	return ex.lamb,ex.spectrum

"""
def read_spectrometer_data(ts,transmission_correct=False,shift_spectrum="spherical",file_end="_spectrum.TXT"):
	data_file = timestamp_to_filename(ts,file_end=file_end,make_folder= False)
	fil = open(data_file)
	file_content = fil.read()
	fil.close()
	lines = file_content.split("\n") #might not work under linux. could be "\r\n"
	data_lines = lines[8:-2]
	xdata = array([float(dl.split(";")[0]) for dl in data_lines])
	ydata = array([float(dl.split(";")[1]) for dl in data_lines])
	bkg = array([float(dl.split(";")[2]) for dl in data_lines])
	ydata_no_bkg = ydata - bkg
	if transmission_correct:
		transmissions = UltrafastMirrorTransmission(xdata,shift_spectrum=shift_spectrum)
		ydata_no_bkg = ydata_no_bkg / transmissions
	return xdata, ydata_no_bkg
"""

def read_image_data(ts,transmission_correct=False,shift_spectrum="spherical"):
	#Currently untested replacement for previous version
	ex = Experiment(ts)
	ex.loadCameraData()
	return ex.im

"""
#point of this is to separate the data stuff from the matplotlib stuff
def read_image_data(ts,file_end=".png"):
	data_file = timestamp_to_filename(ts,file_end=file_end,make_folder= False)
	im = imread(data_file) #normalises data. Can we find out if the data is saturated???
	return im
"""

def slice_data(xdata, ydata, x_range):
	"""
	crops or slices the data in xdata,ydata in the range x_range on the x axis
	"""
	data = zip(xdata, ydata)
	sliced_data = [d for d in data if d[0] >= x_range[0] and d[0] <= x_range[1]]
	return array(zip(*sliced_data))

def smooth(x,window_len=10,window='hanning'):
	"""smooth the data using a window with requested size.
	
	This method is based on the convolution of a scaled window with the signal.
	The signal is prepared by introducing reflected copies of the signal 
	(with the window size) in both ends so that transient parts are minimized
	in the begining and end part of the output signal.
	
	input:
		x: the input signal 
		window_len: the dimension of the smoothing window
		window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
		flat window will produce a moving average smoothing.

	output:
		the smoothed signal

	example:

	t=linspace(-2,2,0.1)
	x=sin(t)+randn(len(t))*0.1

	see also: 

	numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
	scipy.signal.lfilter

	TODO: the window parameter could be the window itself if an array instead of a string   
 	"""

	#
	if x.ndim != 1:
		print("smooth only accepts 1 dimension arrays.")
		raise ValueError
	#
	if x.size < window_len:
		print("Input vector needs to be bigger than window size.")
		raise ValueError
	#
	if window_len<3:
		return x
	#
	if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
		print("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
		raise ValueError
	#
	s=r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
	#print(len(s))
	if window == 'flat': #moving average
		w=ones(window_len,'d')
	else:
		w=eval(window+'(window_len)')
	#
	y=convolve(w/w.sum(),s,mode='same')
	return y[window_len-1:-window_len+1]

def smooth_nD(x,window_len=10,window='hanning',axis=0):
	#smooths nD data along one axis only.
	from scipy.ndimage.filters import convolve
	#axis argument still in testing
	if x.ndim > 3: 
		print("smooth only accepts 1,2 or 3 dimensional arrays.")
		raise ValueError
	if x.size < window_len:
		print("Input vector needs to be bigger than window size.")
		raise ValueError
	if window_len<3: 
		return x
	if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
		print("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
		raise ValueError

	if window == 'flat': #moving average
		w=ones(window_len,'d')
	else:
		w=eval(window+'(window_len)')
    #
	#Now extrude the 1D window into nD, along the correct axis
	#if x.ndim==1: w_temp = ones()
	if x.ndim==2:
		if axis==0: 
			w = array([w]) #seems to work
		elif axis==1: 
			w.transpose()#seems to work
	elif x.ndim==3:
		w = array([[w]]) #seems to work
		if axis==1: 
			w = w.transpose((2,1,0)) #seems to work
		elif axis==0: 
			w = w.transpose((0,2,1)) #seems to work
	
	y=convolve(x, w/w.sum(),mode='reflect')
	return y

	
def UltrafastMirrorTransmission(interpolated_wavelengths,refractive_index = "144",shift_spectrum="planar",rescale_factor=5.2):
	"""
	Can be used for any wavelengths in the range 400 to 1000 (UNITS: nm)
	Interpolate over selected wavelengths: returns a function which takes wavelength (nm) as argument
	Shifts transmission spectrum as measured 2014/02/03: "planar", "spherical" or a number of nm
	"""
	reflectivity_folder = data_root_folder + folder_separator+ "calibration_data" + folder_separator
	reflectivity_filename = "UHR35_for_Rob_n"+refractive_index+".csv" #n=1.44 (solvent). Also available: n=1.00 (air)
	fname = reflectivity_folder+reflectivity_filename
	res = csv.reader(open(fname), delimiter=',')
	refl_text = [x for x in res][1:] #removes column headings
	original_wavelengths = array([float(l[0]) for l in refl_text])
	original_reflectivities = 0.01*array([float(l[1]) for l in refl_text])
	original_transmissions = 1-original_reflectivities
	#
	wavelength_shift = 0
	if shift_spectrum == "planar": #shift measured 7/2/14
		wavelength_shift = 13
	elif shift_spectrum == "spherical":
		wavelength_shift = 18
	elif isinstance(shift_spectrum,Number):
		wavelength_shift = shift_spectrum
	#
	interpolated_transmission_func = interp1d(original_wavelengths,original_transmissions)
	interpolated_transmissions = interpolated_transmission_func(interpolated_wavelengths + wavelength_shift)
	
	#Added 8/10/2014
	#Transmission calibrated on 13/2/2014 at 568 nm. UltrafastInnovation theory does not match data by factor of 5.2 at 568nm.
	#Assume transmission scales with this factor at all wavelengths [not well justified assumption]
	interpolated_transmissions = interpolated_transmissions / rescale_factor
	
	return interpolated_transmissions

def LaserOptikMirrorTransmission(interpolated_wavelengths,refractive_index = "100", shift_spectrum=7,rescale_factor=0.622222):
	"""
	Can be used for any wavelengths in the range 400 to 800 (UNITS: nm)
	Uses supplied calculation from LaserOptik
	Interpolate over selected wavelengths: returns a function which takes wavelength (nm) as argument
	Shifts transmission spectrum with calibration still to come, likewise for "rescale_factor"
	"refractive_index" argument is only for backwards compatibility
	"""
	reflectivity_folder = data_root_folder + folder_separator+ "calibration_data" + folder_separator
	#reflectivity_folder = "./"
	reflectivity_filename = "LaserOptik20160129_Theorie_T.DAT"

	fname = reflectivity_folder+reflectivity_filename
	res = csv.reader(open(fname), delimiter='\t')
	refl_text = [x for x in res][1:] #removes column headings

	original_wavelengths = array([float(l[0]) for l in refl_text])
	original_transmissions = array([float(l[1]) for l in refl_text])
	original_reflectivities = 1-original_transmissions 
	#
	wavelength_shift = 0
	if shift_spectrum == "planar": #shift to be measured
		wavelength_shift = 0
	elif shift_spectrum == "spherical":
		wavelength_shift = 0 # shift to be measured
	elif isinstance(shift_spectrum,Number):
		wavelength_shift = shift_spectrum
	#
	interpolated_transmission_func = interp1d(original_wavelengths,original_transmissions)
	interpolated_transmissions = interpolated_transmission_func(interpolated_wavelengths + wavelength_shift)
	
	#Transmission to be calibrated at at least one narrow wavelength
	#Assume transmission scales with this factor at all wavelengths [not well justified assumption]
	interpolated_transmissions = interpolated_transmissions / rescale_factor
	
	return interpolated_transmissions


def getLambdaRange(lamb, fromL, toL):
	lam = [(i,l) for (i,l) in enumerate(lamb) if (l>fromL) and (l<=toL)]
	return lam[0][0], lam[-1][0]

#EOF
