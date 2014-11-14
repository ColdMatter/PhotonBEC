#exit()

#ipython --pylab
#execfile("hene_stabilisation.py")
from hene_utils import *
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
import pbec_experiment
import pbec_analysis
import SingleChannelAO
import threading
from pi_controller import PI_control

#----------------------
#PARAMETERS FOR ANALYSIS
#----------------------
cam_label="flea"
binning = -1
if binning == 1:
	x0_est,y0_est=544,751 #approximate centre of rings, in pixels
	dx,dy=250,250 #Image to be cut down to this size. Half-size in pixels
	dx_search,dy_search=10,10 #range over which centre can be adjusted automatically. Half-size in pixels
	window_len = 3 #window for smoothing radial profiles for peak finding
	peak_window=25 #annular width around peak to measure width
	min_acceptable_radius=10 #reject ring sizes less than this as being anomalies
elif binning == -1:
	#Smaller ROI, 800x800
	x0_est,y0_est=419,416 #approximate centre of rings, in pixels
	dx,dy=250,250 #Image to be cut down to this size. Half-size in pixels
	dx_search,dy_search=10,10 #range over which centre can be adjusted automatically. Half-size in pixels
	window_len = 3 #window for smoothing radial profiles for peak finding
	peak_window=25 #annular width around peak to measure width
	min_acceptable_radius=10 #reject ring sizes less than this as being anomalies


#Set up feedback with an offset voltage
control_range=(0,1)
SingleChannelAO.SetAO1(mean(control_range)) #middle of the range

	
#-----------------------
#DATA TO WORK WITH
#-----------------------
ts = pbec_analysis.make_timestamp()
im_raw = pbec_experiment.get_single_image(cam_label)
channel=0 #red data only

#-----------------------
#FIND THE CENTRE, CHECK THAT CENTRE IS CORRECT
#-----------------------
centre = search_for_ring_centre(im_raw,(x0_est,y0_est), (dx_search,dy_search), (dx,dy), radial_profile_smooth_len=1,peak_radial_width_window=peak_window)

#-----PLOT RESULTS OF FIRST IMAGE ANALYSIS
ring_rad = ring_radius(im_raw,centre,(dx,dy),channel=channel,window_len=window_len,min_acceptable_radius=min_acceptable_radius)[0]
figure(1),clf()
title(ts+"; ring radius "+str(ring_rad)+" px")
c = Circle((centre[1],centre[0]),ring_rad,facecolor="none",edgecolor="g",linewidth=2,linestyle="dashdot")
gca().add_artist(c)
b = Rectangle((centre[1]-dy,centre[0]-dx),2*dy,2*dx,facecolor="none",edgecolor="b",linestyle="dashed")
gca().add_artist(b)
imshow(im_raw[:,:,channel],cmap=cm.hot),colorbar()
draw()


#------------------------------
#PROPORTIONAL-INTEGRAL OUTPUT FROM ERROR SIGNAL
#------------------------------
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


#------TESTING------------
def stabilise(set_radius):
	res,pic = pic_control_radius(nImage=100,set_radius=set_radius,\
		P_gain=-8e-3,I_gain=-5e-2/100,buffer_length=100,\
		control_range=array(control_range)-mean(control_range),control_offset=mean(control_range),\
		control_gain=1,verbose=False,centre=centre)
	#
	SingleChannelAO.SetAO1(mean(control_range)) #re-set control voltage at end

global_set_radius=180
class StabiliseThread(threading.Thread):
	def __init__(self,set_radius=180):
		threading.Thread.__init__(self)
		self.daemon = False
		self.set_radius = set_radius
		self.running = False
		self.paused =False

	def run(self):
		self.running = True
		while self.running:
			#why the double loop?
			time.sleep(1e-2)
			while not self.paused:
				#insert the controller actions here
				#stabilise(self.set_radius)
				stabilise(global_set_radius)
		print("\nended\n")


#stable = StabiliseThread()
#stable.start()
#stabilise(180)


'''
	figure(2),clf()
	subplot(2,1,1)
	plot([time_number_from_timestamp(r["ts"]) for r in res],[1e3*float(r["Vout"]) for r in res])
	xlabel("time (s since midnight)")
	ylabel("Control voltage (mV)")
	subplot(2,1,2)
	plot([time_number_from_timestamp(r["ts"]) for r in res],[int(r["ring_rad"]) for r in res])
	xlabel("time (s since midnight)")
	ylabel("Ring radius (px)")
'''

#execfile("hene_stabilisation.py")
#EoF
