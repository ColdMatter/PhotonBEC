from __future__ import division
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_analysis import *
import pbec_analysis
import pbec_experiment 
from scipy import optimize
import operator
from pi_controller import PI_control

cam_label = "flea"

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
def ring_radius(im,(x0,y0),(dx,dy),channel=0,window_len=1,min_acceptable_radius=4):
	subim = im[x0-dx:x0+dx,y0-dy:y0+dy,channel]
	rp = radial_profile(subim,(dx,dy),window_len=window_len)
	#Ignores the very first point, to avoid not-so-rare cases where zero-radius causes divergence
	#Change has not fully been tested
	ring_rad, peak_value = max(enumerate(list(rp[min_acceptable_radius:])), key=operator.itemgetter(1))
	return ring_rad+min_acceptable_radius,peak_value,rp

def ring_width(im,(x0,y0),(dx,dy),channel=0,window_len=1,peak_window=20):
	ring_rad,peak_value,rp = ring_radius(im,(x0,y0),(dx,dy),channel=0,window_len=window_len)
	max_rad = int(sqrt(dx**2 + dy**2))-1 - peak_window
	min_rad = peak_window+1
	window_max = min(ring_rad+peak_window ,max_rad)
	window_min = max(ring_rad-peak_window ,min_rad)
	window_indices = range(window_min , window_max)
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
"""
def pic_control_radius(nImage=10,set_radius=100,\
	P_gain=-3e-4,I_gain=-1e-4,buffer_length=10,\
	control_range=(-0.5,0.5),control_offset=0.5,control_gain=1.0,\
	bandwidth_throttle=0.01,verbose=False,centre=()):
	c = pbec_experiment.getCameraByLabel(cam_label)
	pic = PI_control(P_gain=P_gain,I_gain=I_gain,buffer_length=buffer_length,set_point=set_radius,control_range=control_range) #note: negative gains
	cam_info=c.setup()
	results=[]
	for i in range(nImage):
		ts = pbec_analysis.make_timestamp(3)
		#Next line gets image and analyses it in one go
		try:
			im_raw = c.get_image()
			#eats all the bandwidth!
		except:
			print "Image acquisition error. Re-using previous image"
		time.sleep(bandwidth_throttle)
		ring_rad = ring_radius(im_raw,centre,(dx,dy),channel=channel,window_len=window_len,min_acceptable_radius=min_acceptable_radius)[0]
		#Now update the PI Controller
		pic.update(ts,ring_rad)
		Vout = control_gain*pic.control_value()+control_offset
		SingleChannelAO.SetAO1(Vout)
		#Gather the outputs
		r = {"i":i,"ts":ts, "ring_rad":ring_rad,"Vout":round(Vout,3),"pic value":pic.control_value()}
		if verbose: print r["i"],r["ts"],r["Vout"],r["ring_rad"],r["pic value"]
		#Now output a voltage from PI_controller
		results.append(r)
	c.close()
	return results,pic
"""

def time_number_from_timestamp(ts):
	#assumes includes numbers after the decimal place
	#Only useful for plot purposes
	YYYYMMDD,hhmmss,d=ts.split("_")
	hh,mm,ss=int(hhmmss[:2]),int(hhmmss[2:4]),int(hhmmss[-2:])
	decimal_places = float("0."+d)
	seconds_today = 3600*hh + 60*mm + ss + decimal_places
	return seconds_today
