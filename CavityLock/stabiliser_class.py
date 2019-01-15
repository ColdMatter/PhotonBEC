import sys
sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("Y:\\Control\\PythonPackages\\")

from hene_utils import *
import pbec_experiment
import pbec_analysis
from pi_controller import PI_control
import threading
import traceback

def set_cavity_length_voltage(v):
	pass

from socket import gethostname
if gethostname()=="ph-rnyman-01":
	#DEFUNCT: PLEASE REPLACE WITH ph-photonbec
	camera_label = "flea"
	hardwidth = 800
	hardheight = 800 #image size for flea
	import SingleChannelAO
	def set_cavity_length_voltage(v):
		SingleChannelAO.SetAO0(v)
	dxdy = (200, 200)
	min_acceptable_radius = 30
	default_P_gain = -1.5e-3
	default_I_gain = -1e-3
	default_I_const = 20
	default_II_gain = +150 #note sign is always positive: square of sign of I gain
	default_II_const=400
	default_control_range = (0,1.0)
elif gethostname()=="ph-photonbec2": #laptop
	camera_label = "flea"
	hardwidth = 800
	hardheight = 800 #image size for flea
	import SingleChannelAO
	dxdy = (250, 250) #Changed to make bigger BTW 20171215
	min_acceptable_radius = 30
	potential_divider = False
	if potential_divider:
		default_P_gain = -0.10
		default_I_gain = -0.05
		default_I_const = 5
		default_II_gain = +200 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,5)
		def set_cavity_length_voltage(v):
			SingleChannelAO.SetAO0(v, minval=default_control_range[0],maxval=default_control_range[1])
			#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output
	else:
		default_P_gain = -0.005
		default_I_gain = -0.01
		default_I_const = 20
		default_II_gain = +50 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,1)
		def set_cavity_length_voltage(v):
			SingleChannelAO.SetAO0(v, minval=default_control_range[0],maxval=default_control_range[1])
			#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output

elif gethostname()=="ph-photonbec3":
	camera_label = "flea"
	hardwidth = 800
	hardheight = 800 #image size for flea
	import SingleChannelAO
	dxdy = (250, 250) #Changed to make bigger BTW 20171215
	min_acceptable_radius = 30
	potential_divider = False
	if potential_divider:
		default_P_gain = -0.10
		default_I_gain = -0.05
		default_I_const = 5
		default_II_gain = +200 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,5)
		def set_cavity_length_voltage(v):
			SingleChannelAO.SetAO1(v, minval=default_control_range[0],maxval=default_control_range[1])
			#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output
	else:
		default_P_gain = -0.005
		default_I_gain = -0.01
		default_I_const = 20
		default_II_gain = +50 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,1)
		def set_cavity_length_voltage(v):
			SingleChannelAO.SetAO1(v, minval=default_control_range[0],maxval=default_control_range[1])
			#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output

elif gethostname()=="ph-photonbec":
	camera_label = "flea"
	hardwidth = 800
	hardheight = 800 #image size for flea
	import SingleChannelAO
	dxdy = (250, 250) #Changed to make bigger BTW 20171215
	min_acceptable_radius = 30
	potential_divider = False
	if potential_divider:
		default_P_gain = -0.10
		default_I_gain = -0.05
		default_I_const = 5
		default_II_gain = +200 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,5)
		def set_cavity_length_voltage(v):
			SingleChannelAO.SetAO0(v, minval=default_control_range[0],maxval=default_control_range[1],device="Dev2")
			#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output
	else:
		default_P_gain = -0.005
		default_I_gain = -0.01
		default_I_const = 20
		default_II_gain = +50 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,1)
		def set_cavity_length_voltage(v):
			SingleChannelAO.SetAO0(v, minval=default_control_range[0],maxval=default_control_range[1],device="Dev2")
			#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output			

elif gethostname()=="ph-photonbec4":
	camera_label = "flea"
	hardwidth = 800
	hardheight = 800 #image size for flea
	import SingleChannelAO
	dxdy = (250, 250) #Changed to make bigger BTW 20171215
	min_acceptable_radius = 30
	potential_divider = False
	if potential_divider:
		default_P_gain = -0.10
		default_I_gain = -0.05
		default_I_const = 5
		default_II_gain = +200 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,5)
		def set_cavity_length_voltage(v):
			SingleChannelAO.SetAO1(v, device="Dev1", minval=default_control_range[0],maxval=default_control_range[1])
			#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output
	else:
		default_P_gain = -0.005
		default_I_gain = -0.01
		default_I_const = 20
		default_II_gain = +50 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,1)
		def set_cavity_length_voltage(v):
			SingleChannelAO.SetAO1(v, device="Dev1", minval=default_control_range[0],maxval=default_control_range[1])
			#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output
	

			
#flea is for the main experiment
#chameleon for the mini-setup
camera_config = {
	'flea': {"auto_exposure": 0, "shutter": 0.1, "gain": 0, "frame_rate": 150},
	'chameleon': {"auto_exposure": 0, "shutter": 0.03, "gain": 0, "frame_rate": 18},
	'minisetup_chameleon': {"auto_exposure": 0, "shutter": 0.04, "gain": 0, "frame_rate": 18}
}

class _StabiliserThread(threading.Thread):
	def __init__(self,parent):
		threading.Thread.__init__(self)
		self.parent=parent
		self.daemon = True
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
				#why the double loop? so it can be paused and unpaused
				time.sleep(1e-2) #when paused, while loop not going mental
				while not self.paused:
					#insert the controller actions here
					parent.ts = pbec_analysis.make_timestamp(3)
					try:
						parent.im_raw = parent.cam.get_image()
						if parent.im_raw == None:
							print('get_image() == None in stabiliser_class.py')
						parent.ring_rad = ring_radius(parent.im_raw, parent.centre,(parent.dx,parent.dy),\
							channel=parent.channel, window_len=parent.window_len,\
							min_acceptable_radius=parent.min_acceptable_radius)[0]
					except Exception as e:
						traceback.print_exc()
						self.parent.error_message = e
						print "Image acquisition error. Re-using previous image"
						#
					time.sleep(parent.bandwidth_throttle)
					#Now update the PI Controller
					pic.update(parent.ts, parent.ring_rad)
					if parent.control_gain != 0:
						parent.Vout = parent.control_gain * parent.pic.control_value() + parent.control_offset
					#
					#SingleChannelAO.SetAO1(parent.Vout)
					set_cavity_length_voltage(parent.Vout)
					#Gather the outputs
					r = {"ts":parent.ts, "ring_rad":parent.ring_rad, \
						"Vout":round(parent.Vout,6), "pic value":parent.pic.control_value()}
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
		self.cam_label = camera_label
		#if gethostname()=="ph-rnyman-01": #altered by Walker 6/5/16 to include mini_setup
		#	self.control_range = (0,1.0)
		#elif gethostname()=="ph-photonbec2": #laptop
		#	self.control_range = (0,1.0)
		self.control_range = default_control_range
		self.control_offset=mean(self.control_range)
		self.control_gain = 0 #0-> no output voltage; 1-> full; -1-> negative
		#self.bandwidth_throttle=0.15 #slows down acquisition so other devices can use USB
		self.bandwidth_throttle=0.001 #slows down acquisition so other devices can use USB
		self.print_frequency =0#for diagnostic purposes
		#
		self.x0_est,self.y0_est=400,400	#approximate centre of rings, in pixels
		#The centre assumes an on-CCD RoI of width w800 x h800, left 240, top 112 (centred)
		#go to FlyCapGUI -> Settings dialog box -> Custom Video Modes
		#Also, play with Packet size to try to eliminate image tearing problems
		#self.dx,self.dy=200,200#180,180 #Image to be cut down to this size. Half-size in pixels
		self.dx,self.dy = dxdy #Image to be cut down to this size. Half-size in pixels
		self.dx_search,self.dy_search=8,8 #range over which centre can be adjusted automatically. Half-size in pixels
		#self.window_len = 2 #window for smoothing radial profiles for peak finding
		self.window_len = 4 #window for smoothing radial profiles for peak finding
		self.peak_window=25 #annular width around peak to measure width
		self.min_acceptable_radius = min_acceptable_radius #reject ring sizes less than this as being anomalies
		#Maybe it will be necessary to implement a maximum acceptable radius too.
		
		#--------------------
		self.im_raw = []
		#NOTE: TODO Add pre-definition of "r" for hene_utils.radial_profile. Only needs x0,y0, dx and dy to calculate. These are hard-coded, so never change
		self.ts = None
		self.centre=self.x0_est,self.y0_est
		self.ring_rad=0#unknown!!!!
		self.set_point = set_point
		#
		self.cam = pbec_experiment.getCameraByLabel(self.cam_label) #the camera object
		direct_gain_factor=1 #if the gain is too high, reduce this.
		buffer_length=10 #was 200 a while ago...now mostly irrelevant
		self.pic = PI_control(P_gain = direct_gain_factor*default_P_gain,\
			I_gain = direct_gain_factor*default_I_gain,I_const=default_I_const,\
			II_gain = direct_gain_factor*default_II_gain,II_const=default_II_const,\
			buffer_length=buffer_length,\
			control_range=array(self.control_range)-mean(self.control_range),\
			set_point = self.set_point)
		#
		self.initialise_thread()
		#
		self.Vout=mean(self.control_range)
		#SingleChannelAO.SetAO1(self.Vout) #Set up feedback with an offset voltage
		set_cavity_length_voltage(self.Vout)
	
	def set_voltage(self,voltage):
		self.Vout = voltage
		#SingleChannelAO.SetAO1(self.Vout)
		set_cavity_length_voltage(self.Vout)
		
	def initialise_thread(self):
		self.thread = _StabiliserThread(self) #don't start the thread until you want to acquire
		self.thread.paused=True
		self.thread.start()
		
	def find_centre(self):
		self.ts = pbec_analysis.make_timestamp()
		self.im_raw = pbec_experiment.get_single_image(self.cam_label)
		#Prvious command almost certainly breaks the looped acquisition of images, inside the StabiliserThread.
		self.centre = search_for_ring_centre(self.im_raw,(self.x0_est,self.y0_est),\
			(self.dx_search,self.dy_search), (self.dx,self.dy), \
			radial_profile_smooth_len=1,peak_radial_width_window=self.peak_window)
		#TODO: also infer ring radius, self.ring_rad = ring_radius(....)

	def start_acquisition(self,width=hardwidth,height=hardheight):
		#Hard-coded image size "because reasons" [J. Marelic, 27/10/14]
		cam_info=self.cam.setup()
		#Default camera properties which need overriding
		set_dict = camera_config[camera_label]
		#NOTE: 17/11/14: why are exposure and frame_rate not being set correctly automatically?
		for key in set_dict:
			self.cam.set_property(key, set_dict[key], auto=False)
		#self.cam.set_centered_region_of_interest(width, height)
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
