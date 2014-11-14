#Utilities for data analysis on Photon BEC experiment
from socket import gethostname
import time
import os
import csv
from pylab import *
from scipy.interpolate import interp1d
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

def TimeStamp():
	#Outputs time stamp in format YYYYMMDD_hhmmss
	t = time.localtime()
	YYYY = str(t.tm_year)
	MM= str(100+t.tm_mon)[-2:] #pre-pends zeroes where needed
	DD = str(100+t.tm_mday)[-2:]
	hh = str(100+t.tm_hour)[-2:]
	mm = str(100+t.tm_min)[-2:]
	ss = str(100+t.tm_sec)[-2:]
	l=[YYYY,MM,DD,"_",hh,mm,ss]
	return "".join(l)

def DataFolder(ts=TimeStamp(),make=False):
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

getDataFolderFromTimeStamp = DataFolder

def TimeStampToFileName(ts,file_end=".txt",make_folder= False):
	return DataFolder(ts,make=make_folder)+pbec_prefix+"_"+ts+file_end
	
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


def timeFromTimeStamp(ts):
    return ts.split("_")[1]

def timeStampFromFileName(filename):
    return filename.split(folder_separator)[-1].split(".")[0].split(pbec_prefix+"_")[-1]

def timeFromFileName(filename):
    return filename.split(".")[0].split("_")[2]

def data_files_in_range(first_ts,last_ts,extension=".json"):
    foldername = DataFolder(first_ts)
    first_time,last_time = timeFromTimeStamp(first_ts),timeFromTimeStamp(last_ts)
    ls = os.listdir(foldername)
    file_list = [s for s in ls if s[-(len(extension)):]==extension]
    selected = [s for s in file_list if ((timeFromFileName(s)>=first_time)&(timeFromFileName(s)<=last_time))]
    all_files = [foldername+s for s in selected]
    return all_files

def timeStampsInRange(first_ts,last_ts,extension = ".json"):
    return map(timeStampFromFileName,data_files_in_range(first_ts,last_ts,extension=extension))

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
