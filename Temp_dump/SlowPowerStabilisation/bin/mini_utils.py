from scipy.signal import argrelextrema
from pbec_analysis import *

#peak_ratio = 100					#Minimum factor of peak above adjacent minimum
smooth_len = 4						#Smooth the data
gap =1							#Look for the minimum closest to (lam of max) + gap
data_lamb_range = (555,585)				#Only look at this range of the spectrum. Needs to go high enought that the ground state peak doesn't move out, but narrow enough so as not to include other peaks.

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


def FindPeak(lamb, spec, data_lamb_range = data_lamb_range, peak_ratio = 1.7, spacing=1.7,tolerance=2):

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
		ind = min(enumerate(lambmin), key=lambda x: abs(x[1]-(lambmax[j]+(spacing/2))))[0]
		minRight_loc = minima_loc[ind]
		if cutspec[maxima_loc[j]]/cutspec[minRight_loc] > peak_ratio:
			lambToFit = lambToFit+[lambmax[j]]
        
	really_BEC = True
	if really_BEC:
		try:
			lam_fit=lam_fit = lambToFit[-1]
		except IndexError:
			print 'Index Error'
			lam_fit = nan
	else:
		try:
			#if (abs(lambToFit[-1]-lambToFit[-2]-spacing)<tolerance)&(abs(lambToFit[-2]-lambToFit[-3]-spacing)<tolerance):
			if (abs(lambToFit[-1]-lambToFit[-2]-spacing)<tolerance):
				lam_fit = lambToFit[-1]
			else:
				print 'Not regular'
				lam_fit=nan
		except IndexError:
			print 'Index Error'
			lam_fit = nan
		
	return lam_fit