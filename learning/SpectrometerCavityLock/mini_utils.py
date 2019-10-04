from scipy.signal import argrelextrema
from pbec_analysis import *

peak_ratio = 1.15					#Minimum factor of peak above adjacent minimum
smooth_len = 5						#Smooth the data
gap =2							#Look for the minimum closest to (lam of max) + gap
data_lamb_range=(550,580)				#Only look at this range of the spectrum. Needs to go high enought that the ground state peak doesn't move out, but narrow enough so as not to include other peaks.

#Dummy transitional package
def time_number_from_timestamp(ts):
	#Overrides version from hene_utils
	#assumes includes numbers after the decimal place
	#Only useful for plot purposes
	YYYYMMDD,hhmmss,d=ts.split("_")
	hh,mm,ss=int(hhmmss[:2]),int(hhmmss[2:4]),int(hhmmss[-2:])
	decimal_places = float("0."+d)
	seconds_today = 3600*hh + 60*mm + ss + decimal_places
	return seconds_today


def FindPeak(lamb, spec):

	#Cut the data down to look only at the region in data_lamb_range
	cut = slice_data(lamb,spec,data_lamb_range)
	cutlamb, cutspec = cut[0], cut[1]
	
	#Smooth the spectrum
	cutspec_smooth = smooth(cutspec,window_len=smooth_len)
	cutspec=cutspec_smooth
	
	#Reduce data down to the locations and heights of the peaks
	lambmax = cutlamb[argrelextrema(cutspec, np.greater)[0]]
	lambmin = cutlamb[argrelextrema(cutspec, np.less)[0]]
	maxima_loc = argrelextrema(cutspec, np.greater)[0]
	minima_loc = argrelextrema(cutspec, np.less)[0]

	specToFit = []
	lambToFit = []
	
	#Find the minimum to the right (by gap) of each peak, and keep only peaks above a certain height in log space
	for j in range(len(lambmax)):
		minRight_loc = minima_loc[min(enumerate(lambmin), key=lambda x: abs(x[1]-(lambmax[j]+gap)))[0]]
		if cutspec[maxima_loc[j]]/cutspec[minRight_loc] > peak_ratio:
			lambToFit = lambToFit+[lambmax[j]]
        
        lam_fit = max(lambToFit)
	
	return lam_fit