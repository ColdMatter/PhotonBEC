import sys
import socket

if socket.gethostname() == 'ph-photonbec3':
	sys.path.append("Y:\\Control\\CameraUSB3\\")
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\CavityLock_minisetup")
else:
	raise Exception("Unknown machine")


from hene_utils import *
import pbec_experiment
import pbec_analysis
from pi_controller import PI_control
import threading
import traceback
import matplotlib
import time
from sklearn.decomposition import PCA
from fringes_utils import compute_locking_signal
from CameraUSB3 import CameraUSB3

potential_divider = True
number_images_for_PCA = 10
led_lambda = 650 # in nm

def set_cavity_length_voltage(v):
	pass

from socket import gethostname

if gethostname()=="ph-photonbec3":
	camera_label = "blackfly_minisetup"
	hardwidth = 800
	hardheight = 800 #image size for flea
	import SingleChannelAO
	if potential_divider is False:
		default_P_gain = 0.01
		default_I_gain = 0.035
		default_I_const = 10
		default_II_gain = 400 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0,5)
	elif potential_divider is True:
		default_P_gain = 0.01
		default_I_gain = 0.035
		default_I_const = 10
		default_II_gain = 400 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (0, 4.5)
	else:
		raise Exception("Invalid option for potential divider")
	
	def set_cavity_length_voltage(v):
		SingleChannelAO.SetAO1(v, device="Dev2", minval=default_control_range[0],maxval=default_control_range[1])
		#Make sure DAQ board as well as the gui display knows about the min/max values to make best use of dynmaic range on output

else:
	raise Exception('Unknown machine')
	
# minisetup_chameleon_lockcamera for the mini-setup
#camera_config = {
#	'flea': {"auto_exposure": 0, "shutter": 0.1, "gain": 0, "frame_rate": 150},
#	'chameleon': {"auto_exposure": 0, "shutter": 0.03, "gain": 0, "frame_rate": 18},
#	'minisetup_chameleon': {"auto_exposure": 0, "shutter": 0.04, "gain": 0, "frame_rate": 18},
#	'minisetup_chameleon_lockcamera': {"auto_exposure": 0, "shutter": 5, "gain": 0.986, "frame_rate": 30}
#}

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
				time.sleep(0.1) #when paused, while loop not going mental

				while not self.paused:
					#insert the controller actions here
					parent.ts = pbec_analysis.make_timestamp(3)

					##### Calculates first PCA mode
					if parent.initial_analysis is False:
						# Gets the data
						print("Getting PCA Components")
						images = list()
						parent.trial_voltages = np.linspace(parent.control_range[0], parent.control_range[1], parent.number_images_for_PCA)
						for trial_voltage in parent.trial_voltages:
							parent.set_voltage(trial_voltage)
							time.sleep(0.5)
							image_raw = 1.0*parent.cam.get_image()
							image_raw = image_raw[::4,::4]
							images.append(image_raw)
							time.sleep(0.5)
						parent.set_voltage(mean(parent.control_range))
						images = np.array(images)
						images_shape = images.shape
						images_flattened = np.reshape(images, [images_shape[0], images_shape[1]*images_shape[2]])
						images_mean = np.squeeze(np.mean(images_flattened, 0))
						images_centered = list()
						for i in range(0, images_shape[0]):
							images_centered.append(images_flattened[i,:] - images_mean)
						images_centered = np.array(images_centered)
						# Calculates main pca component
						pca = PCA(n_components=1, tol=1e-3)
						print("Fitting PCA")
						pca.fit(images_centered)
						print("PCA successfully fitted")
						pca_explained_variance_ratio = pca.explained_variance_ratio_
						pca_components_flattened = pca.components_
						print("Squeezing variables")
						main_pca_component = np.squeeze(pca_components_flattened[0,:])
						pca_components_2D = np.reshape(pca_components_flattened, [pca_components_flattened.shape[0], images_shape[1], images_shape[2]])
						# Checks monotomy of the pca projections
						print("Renormalizing projections")
						projections = list()
						for i in range(0, images_centered.shape[0]):
							projections.append(np.dot(images_centered[i,:], main_pca_component))
						projections = np.array(projections)
						normalization_factor = np.max([np.abs([np.min(projections), np.max(projections)])]) / parent.error_signal_amplitude
						projections = projections / normalization_factor
						parent.projections = projections
						# Saves some useful plots
						print("Saving some images")
						matplotlib.image.imsave('lock_image_first_fringe.jpg', images[0,:,:])
						matplotlib.image.imsave('lock_image_last_fringe.jpg', images[-1,:,:])
						matplotlib.image.imsave('lock_image_mean.jpg', np.squeeze(np.mean(images[:,:,:], 0)))
						matplotlib.image.imsave('lock_image_main_PCA_component.jpg',  np.squeeze(pca_components_2D[0,:,:]))
						print('    Explained variance ratio of first 5 components:')
						print(pca_explained_variance_ratio)
						print("PCA Components successfully calculated")
						parent.initial_analysis = True
						input("Press Enter to continue...")

					try:
						time1 = 1000*time.time()
						parent.im_raw = parent.cam.get_image()[::4,::4]
						time2 = 1000*time.time()
						parent.ring_rad = compute_locking_signal(
							images_mean=images_mean,
							main_pca_component=main_pca_component,
							normalization_factor=normalization_factor,
							current_image=parent.im_raw)
						time3 = 1000*time.time()
						locking_rate = np.round((1000.0/(time3-time1)),0)
						print('Current projection value = {}'.format(parent.ring_rad))
						print('Frame time = {0} ms / Analysis time = {1} ms / Lock rate = {2} Hz'.format(int(time2-time1), int(time3-time2), locking_rate))


					except Exception as e:
						traceback.print_exc()
						self.parent.error_message = e
						print("Image acquisition error. Re-using previous image")
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
							print(r["ts"], r["Vout"], r["ring_rad"], r["pic value"])
					#Now output a voltage from PI_controller
					if len(parent.results)>5000:
						parent.results = parent.results[-5000:]
					parent.results.append(r)

		finally:
			cam.end_acquisition()
			cam.close()
		print("Finished\n")




class Stabiliser():
	def __init__(self,set_point=0):
		#------------------
		#PARAMETERS WHICH EVENTUALLY NEED TO BE INPUT FROM GUI
		#------------------
		self.error_message = None
		self.channel=0 #red data only
		self.cam_label = camera_label
		self.led_lambda = led_lambda
		print("Cam label = ", self.cam_label)
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
		#self.x0_est,self.y0_est=300,300	#approximate centre of rings, in pixels
		####self.x0_est,self.y0_est=400,400	#approximate centre of rings, in pixels
		#The centre assumes an on-CCD RoI of width w800 x h800, left 240, top 112 (centred)
		#go to FlyCapGUI -> Settings dialog box -> Custom Video Modes
		#Also, play with Packet size to try to eliminate image tearing problems
		#self.dx,self.dy=200,200#180,180 #Image to be cut down to this size. Half-size in pixels
		#self.dx,self.dy = dxdy #Image to be cut down to this size. Half-size in pixels
		####self.dx_search,self.dy_search=8,8 #range over which centre can be adjusted automatically. Half-size in pixels
		#self.window_len = 2 #window for smoothing radial profiles for peak finding
		####self.window_len = 4 #window for smoothing radial profiles for peak finding
		####self.peak_window=25 #annular width around peak to measure width
		####self.min_acceptable_radius = min_acceptable_radius #reject ring sizes less than this as being anomalies
		#Maybe it will be necessary to implement a maximum acceptable radius too.
		
		#--------------------
		self.im_raw = []
		#NOTE: TODO Add pre-definition of "r" for hene_utils.radial_profile. Only needs x0,y0, dx and dy to calculate. These are hard-coded, so never change
		self.ts = None
		####self.centre=self.x0_est,self.y0_est
		self.ring_rad=0#unknown!!!!
		self.set_point = set_point
		self.initial_analysis = False
		self.number_images_for_PCA = number_images_for_PCA
		self.error_signal_amplitude = 10
		#
		#self.cam = pbec_experiment.getCameraByLabel(self.cam_label) #the camera object
		self.cam = CameraUSB3(verbose=True, camera_id=self.cam_label, timeout=1000, acquisition_mode='continuous')
		print("Have got the camera")
		#print self.cam.get_all_properties()
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
		
	'''
	def find_centre(self):
		self.ts = pbec_analysis.make_timestamp()
		self.im_raw = pbec_experiment.get_single_image(self.cam_label)
		#Prvious command almost certainly breaks the looped acquisition of images, inside the StabiliserThread.
		self.centre = search_for_ring_centre(self.im_raw,(self.x0_est,self.y0_est),\
			(self.dx_search,self.dy_search), (self.dx,self.dy), \
			radial_profile_smooth_len=1,peak_radial_width_window=self.peak_window)
		#TODO: also infer ring radius, self.ring_rad = ring_radius(....)
	'''
	
	''' Called for USB2 cameras
	def start_acquisition(self,width=hardwidth,height=hardheight):
		#Hard-coded image size "because reasons" [J. Marelic, 27/10/14]
		print "Calling setup from start acquisition"
		cam_info=self.cam.setup()
		#Default camera properties which need overriding
		set_dict = camera_config[camera_label]
		#NOTE: 17/11/14: why are exposure and frame_rate not being set correctly automatically?
		for key in set_dict:
			self.cam.set_property(key, set_dict[key], auto=False)
		#self.cam.set_centered_region_of_interest(width, height)
		self.thread.paused=False
	'''

	def start_acquisition(self):
		print("Startint camera aquisition")
		self.cam.begin_acquisition()
		self.thread.paused=False
	
	''' Called for USB2 cameras
	def stop_acquisition(self):
		self.thread.paused=True
		time.sleep(0)#avoid race condition. Should really use mutex
		self.cam.close()
	'''

	def stop_acquisition(self):
		self.thread.paused=True
		time.sleep(0)#avoid race condition. Should really use mutex
		self.cam.end_acquisition()
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
