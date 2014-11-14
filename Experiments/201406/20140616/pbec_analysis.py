#Utilities for data analysis on Photon BEC experiment
#heavily added to and some names changed by JM 1/4/2014
from socket import gethostname
import time
import os
import csv
from pylab import *
from scipy.interpolate import interp1d
from scipy import constants
from numbers import Number
#from numpy import ones

pbec_prefix = "pbec"
point_grey_chameleon_pixel_size = 3.75e-6

if gethostname()=="ph-rnyman-01":
	#ph-photonbec is also carries the name "ph-rnyman-01". Bah.
	data_root_folder = "D:\\Data"
	folder_separator="\\"
elif gethostname()=="ph-rnyman":
	#only works for data that has been backed up to the local d_drive
	data_root_folder = "/home/d_drive/Experiment/photonbec/Data"
	#data_root_folder = "./Data"
	folder_separator="/"
elif gethostname()=="potato":
	#only works for data that copied to correct part of Temp folder
	data_root_folder = "D:\\Temp\\Imperial\\photon_bec\\Data"
	folder_separator="\\"
else:
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
	Calculation of expected number vs wavelength for thermalised photons
	uses bose-einstine distribution, or boltzmann distribution if mu=0
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
		print "For backwards compatibility, the timestamp will include seconds anyway"
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


"""
def timestamps_in_range(first_ts, last_ts, extension=".json"):
    if date_from_timestamp(first_ts)==date_from_timestamp(last_ts):
    	ts_list= timestamps_in_range_single_day(first_ts, last_ts, extension=extension)
    else:
	pass
	#detect all dates, find all possible data files for each date, within range, etc...
    return ts_list


"""
def timestamps_in_range(first_ts, last_ts, extension=".json"):
    df_list = data_files_in_range(first_ts,last_ts,extension=extension)
    ts_list = map(timestamp_from_filename,df_list)
    return ts_list
#
# file format functions
#
#def read_spectrometer_data(data_file, transmission_correct=False, shift_spectrum="planar"):
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

#point of this is to separate the data stuff from the matplotlib stuff
def read_image_data(ts,file_end=".png"):
	data_file = timestamp_to_filename(ts,file_end=file_end,make_folder= False)
	im = imread(data_file) #normalises data. Can we find out if the data is saturated???
	return im

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
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """
    #
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."
    #
    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."
    #
    if window_len<3:
        return x
    #
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
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

def UltrafastMirrorTransmission(interpolated_wavelengths,refractive_index = "144",shift_spectrum="planar"):
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
	if shift_spectrum == "planar":
		wavelength_shift = 13
	elif shift_spectrum == "spherical":
		wavelength_shift = 18
	elif isinstance(shift_spectrum,Number):
		wavelength_shift = shift_spectrum
	#
	interpolated_transmission_func = interp1d(original_wavelengths,original_transmissions)
	interpolated_transmissions = interpolated_transmission_func(interpolated_wavelengths + wavelength_shift)
	return interpolated_transmissions


#EOF
