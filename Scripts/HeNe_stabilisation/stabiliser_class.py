from hene_utils import *
from hene_utils import *
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
import pbec_experiment
import pbec_analysis
import SingleChannelAO
from pi_controller import PI_control
import threading

class _StabiliserThread(threading.Thread):
	def __init__(self,parent):
		threading.Thread.__init__(self)
		self.parent=parent
		self.daemon = False
		self.running = False
		self.paused =False
		self.parent.results=[]

	def run(self):
		self.running = True
		parent = self.parent
		cam = parent.cam #assumes cam is setup
		pic = parent.pic
		try:
			while self.running:
				#why the double loop?
				time.sleep(1e-2) #when paused, while loop not going mental
				while not self.paused:
					#insert the controller actions here
					parent.ts = pbec_analysis.make_timestamp(3)
					try:
						parent.im_raw = parent.cam.get_image()
					except Exception as e:
						print e
						self.parent.error_message = e
						print "Image acquisition error. Re-using previous image"
						#
					time.sleep(parent.bandwidth_throttle)
					parent.ring_rad = ring_radius(parent.im_raw, parent.centre,(parent.dx,parent.dy),\
						channel=parent.channel, window_len=parent.window_len,\
						min_acceptable_radius=parent.min_acceptable_radius)[0]
					#Now update the PI Controller
					pic.update(parent.ts, parent.ring_rad)
					if parent.control_gain != 0:
						parent.Vout = parent.control_gain * parent.pic.control_value() + parent.control_offset
					#
					SingleChannelAO.SetAO1(parent.Vout)
					#Gather the outputs
					r = {"ts":parent.ts, "ring_rad":parent.ring_rad, \
						"Vout":round(parent.Vout,3), "pic value":parent.pic.control_value()}
					if parent.print_frequency > 0:
						if len(parent.results) % parent.print_frequency == 0: 
							print r["ts"], r["Vout"], r["ring_rad"], r["pic value"]
					#Now output a voltage from PI_controller
					parent.results.append(r)
		finally:
			cam.close()
		print("Finished\n")




class Stabiliser():
	def __init__(self,set_point=100):
		#------------------
		#PARAMETERS WHICH EVENTUALLY NEED TO BE INPUT FROM GUI
		#------------------
		self.error_message = None
		self.channel=0 #red data only
		self.cam_label="flea"
		self.control_range = (0,1.0)
		self.control_offset=mean(self.control_range)
		self.control_gain = 0 #0-> no output voltage; 1-> full; -1-> negative
		self.bandwidth_throttle=0.01 #slows down acquisition so other devices can use USB
		self.print_frequency =0#for diagnostic purposes
		#
		self.x0_est,self.y0_est=419,416 #approximate centre of rings, in pixels
		#The centre assumes an on-CCD RoI of width w800 x h800, left 240, top 112 (centred)
		#go to FlyCapGUI -> Settings dialog box -> Custom Video Modes
		#Also, play with Packet size to try to eliminate image tearing problems
		self.dx,self.dy=250,250 #Image to be cut down to this size. Half-size in pixels
		self.dx_search,self.dy_search=10,10 #range over which centre can be adjusted automatically. Half-size in pixels
		self.window_len = 3 #window for smoothing radial profiles for peak finding
		self.peak_window=25 #annular width around peak to measure width
		self.min_acceptable_radius=10 #reject ring sizes less than this as being anomalies
		
		#--------------------
		self.im_raw = []
		self.ts = None
		self.centre=self.x0_est,self.y0_est
		self.ring_rad=0#unknown!!!!
		self.set_point = set_point
		#
		self.cam = pbec_experiment.getCameraByLabel(self.cam_label) #the camera object
		self.pic = PI_control(P_gain=-8e-3,I_gain=-5e-2/100,buffer_length=100,\
			control_range=array(self.control_range)-mean(self.control_range),\
			set_point = self.set_point)
		#
		self.initialise_thread()
		#
		self.Vout=mean(self.control_range)
		SingleChannelAO.SetAO1(self.Vout) #Set up feedback with an offset voltage
		
	def initialise_thread(self):
		self.thread = _StabiliserThread(self) #don't start the thread until you want to acquire
		self.thread.paused=True
		self.thread.start()
		
	def find_centre(self):
		self.ts = pbec_analysis.make_timestamp()
		self.im_raw = pbec_experiment.get_single_image(self.cam_label)
		self.centre = search_for_ring_centre(self.im_raw,(self.x0_est,self.y0_est),\
			(self.dx_search,self.dy_search), (self.dx,self.dy), \
			radial_profile_smooth_len=1,peak_radial_width_window=self.peak_window)
		#TODO: also infer ring radius, self.ring_rad = ring_radius(....)

	def start_acquisition(self):
		cam_info=self.cam.setup()
		self.thread.paused=False
		
	def stop_acquisition(self):
		self.thread.paused=True
		time.sleep(0)#avoid race condition. Should really use mutex
		self.cam.close()
		
	def close_acquisition(self):
		self.stop_acquisition()
		self.thread.running=False
		
	def start_lock(self):
		self.pic.reset() #forget history; reset the integrator etc.
		self.Vout=mean(self.control_range)
		self.control_gain=1.0

	def stop_lock(self):
		self.control_gain=0

#---------------------
#Testing
#--------------------
"""
import stabiliser_class
from stabiliser_class import Stabiliser
#reload(stabiliser_class) #if need be
s = Stabiliser()
s.find_centre()
#s.pic.set_point=180
#imshow(s.im_raw)
"""
