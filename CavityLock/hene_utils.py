from __future__ import division
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_analysis import *
import pbec_analysis
import pbec_experiment 
from scipy import optimize
import operator

#Grabbed from http://stackoverflow.com/questions/21242011/most-efficient-way-to-calculate-radial-profile
def radial_profile(data, (x0,y0),window_len=1):
	y, x = indices((data.shape)) #make a meshgrid of y and x indices
	r = sqrt((x - x0)**2 + (y - y0)**2) #find distance from centre for all pixels
	r = r.astype(int) #convert to integers
	tbin = bincount(r.ravel(), data.ravel()) #make histogram of radii, weighted by data. One bin for each integer radius
	nr = bincount(r.ravel()) #used for normalisation: otherwise larger radii are overcounted
	radialprofile = tbin / nr
	if window_len==1:
	    rp_smoothed = radialprofile
	else:
	    rp_smoothed = smooth(radialprofile,window_len=window_len)
	return rp_smoothed

#Ring radius is at maximum of smoothed radial profile
def ring_radius(im,(x0,y0),(dx,dy),channel=0,window_len=1,min_acceptable_radius=11, mean_window=40):
	#Large "mean_window" helps overcome discreteness.
	subim = im[x0-dx:x0+dx,y0-dy:y0+dy,channel]
	rp = radial_profile(subim,(dx,dy),window_len=window_len)
	ring_rad_uncorrected, peak_value = max(enumerate(list(rp[min_acceptable_radius:])), key=operator.itemgetter(1))
	ring_rad = ring_rad_uncorrected + min_acceptable_radius
	#Change 13/01/2015: use floating point values. Find weighted mean NOT max position within a window
	posns=arange(-mean_window,mean_window+1,1) + ring_rad
	windowed_values = rp[posns] #KNOWN BUG: fails when ring size near size of image, but doesn't seem to fail catastrophically.
	#Value 0.98 or whatever is empirically determined
	windowed_values = windowed_values - 0.98*mean(windowed_values[-5:-1]) #bkg to offset [helps remove discreteness]
	mean_posn = float( sum(posns*windowed_values) ) / float( sum(windowed_values) ) #causes 
	mean_posn = max(0,min(mean_posn,len(rp)))
	#Can move in <<1 steps, but is strongly influenced by integer-estimated ring rad: window moves one at a time.
	#return ring_rad,peak_value,rp
	return mean_posn,peak_value,rp

def ring_width(im,(x0,y0),(dx,dy),channel=0,window_len=1,peak_window=20):
	ring_rad,peak_value,rp = ring_radius(im,(x0,y0),(dx,dy),channel=0,window_len=window_len)
	max_rad = int(sqrt(dx**2 + dy**2))-1 - peak_window
	min_rad = peak_window+1
	window_max = min(ring_rad+peak_window ,max_rad)
	window_min = max(ring_rad-peak_window ,min_rad)
	window_indices = range(int(floor(window_min)) , int(ceil(window_max)))
	#FIXME: fails when ring is really near the outside of the image
	rp_windowed = rp[window_indices]
	width = sum((array(window_indices)-ring_rad)**2 * rp_windowed ) / (len(window_indices)*sum(rp_windowed))
	return width

def search_for_ring_centre(im,(x0_estimated,y0_estimated), (dx_search,dy_search), (dx_im,dy_im), radial_profile_smooth_len=1,peak_radial_width_window=20):
	"""
	Requires a reasonable guess for centre, and a window (2D) in which it is allowed to search
	"""
	def cost_function((x0,y0)):
		val= ring_width(im,(x0,y0),(dx_im,dy_im),channel=0,window_len=radial_profile_smooth_len,peak_window=peak_radial_width_window)
		#print x0,y0,val
		return val
	#
	x01,x02=x0_estimated-dx_search, x0_estimated+dx_search
	y01,y02=y0_estimated-dy_search, y0_estimated+dy_search
	lower_range=(x01,y01)
	upper_range=(x02,y02)
	xs = range(x01,x02+1)
	ys = range(y01,y02+1)
	#Implement a brute-force search and optimize function
	width_vals = array([[cost_function((x0,y0)) for y0 in ys] for x0 in xs])
	#Return value is location of minimum width
	width_min_index = unravel_index(width_vals.argmin(),width_vals.shape)
	return width_min_index[0]+(x0_estimated-dx_search),width_min_index[1]+(y0_estimated-dy_search)

def time_number_from_timestamp(ts):
	#assumes includes numbers after the decimal place
	#Only useful for plot purposes
	YYYYMMDD,hhmmss,d=ts.split("_")
	hh,mm,ss=int(hhmmss[:2]),int(hhmmss[2:4]),int(hhmmss[-2:])
	decimal_places = float("0."+d)
	seconds_today = 3600*hh + 60*mm + ss + decimal_places
	return seconds_today
