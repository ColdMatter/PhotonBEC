#NOTE: Uses pi_controller class, which is currently based in "CavityLock" folder, but will be moved to PythonPackages
#This class re-uses a lot of code from /Control/CavityLock/stabiliser_class.py
import sys
from socket import gethostname
if gethostname()=="ph-rnyman-01":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")

from hene_utils import *
import pbec_experiment
import pbec_analysis
from pi_controller import PI_control
import mini_utils
import threading
import traceback


#----------------------------------
#COMPUTER SPECIFIC SETTINGS HERE
if gethostname()=="ph-photonbec":
	import SingleChannelAO
	#This could be defined to use the PiezoController server program instead
	def set_cavity_length_voltage(v):
		pass
		#SingleChannelAO.SetAO1(v)
	default_P_gain = -1.5e-3
	default_I_gain = -1e-3
	default_I_const = 20
	default_II_gain = +20 #note sign is always positive: square of sign of I gain
	default_II_const=200
	default_control_range = (0,1.0)
	default_spec_int_time = 20
	default_spec_nAverage = 1
	default_lamb_range = (540,610) #Restrict range analysed, which might make acquisition faster
	mini_utils.peak_ratio = 1.15#OVERRIDE. Minimum factor of peak above adjacent minimum
elif gethostname()=="ph-photonbec2":
	import SingleChannelAO
	#This could be defined to use the PiezoController server program instead
	def set_cavity_length_voltage(v):
		try:
			SingleChannelAO.SetAO1(v)
		except:
			print "PROBABLY A DAQ BOARD ERROR"
		finally:
			return
	
	def set_spec_int_time(t):
		pbec_ipc.ipc_exec('setSpectrometerIntegrationTime('+str(t)+'pause_lock=False)',port=47905,host='ph-photonbec2')
	fly_spec_int_time=60
	default_P_gain = 0
	default_I_gain = 0.8
	default_I_const = 200
	default_II_gain = +4 #note sign is always positive: square of sign of I gain
	default_II_const=200
	default_control_range = (0,5.0)
	default_spec_int_time = 40
	default_spec_nAverage = 1
	default_lamb_range = (555,585) #Restrict range analysed, which might make acquisition faster
	mini_utils.peak_ratio = 1.2#OVERRIDE. Minimum factor of peak above adjacent minimum
elif gethostname()=="ph-photonbec3":
	import SingleChannelAO
	#This could be defined to use the PiezoController server program instead
	def set_cavity_length_voltage(v):
		try:
			SingleChannelAO.SetAO1(v,device="Dev2")
		except:
			print "PROBABLY A DAQ BOARD ERROR"
		finally:
			return
	
	def set_spec_int_time(t):
		pbec_ipc.ipc_exec('setSpectrometerIntegrationTime('+str(t)+'pause_lock=False)',port=47905,host='ph-photonbec2')
	fly_spec_int_time=60
	default_P_gain = 0
	default_I_gain = 0.3
	default_I_const = 200
	default_II_gain = +5 #note sign is always positive: square of sign of I gain
	default_II_const=200
	default_control_range = (0,5.0)
	default_spec_int_time = 2000
	default_spec_nAverage = 1
	default_lamb_range = (540,580) #Restrict range analysed, which might make acquisition faster
	mini_utils.peak_ratio = 1.4#OVERRIDE. Minimum factor of peak above adjacent minimum

#----------------------------------

class _SpectrometerStabiliserThread(threading.Thread):
	def __init__(self,parent):
		threading.Thread.__init__(self)
		self.parent=parent
		self.daemon = True
		self.running = False
		self.paused =False
		self.lockpaused = False
		self.parent.results=[]

	def run(self):
		self.running = True
		parent = self.parent
		spectro = parent.spectro #assumes spectrometer is setup
		pic = parent.pic #PI controller
		try:
			while self.running:
				#why the double loop? so it can be paused and unpaused
				time.sleep(1e-2) #when paused, while loop not going mental
				while not self.paused:
					#insert the controller actions here
					try:
						temp_spectrum=[]
						temp_spectrum = parent.spectro.get_data()
						parent.spectrum = temp_spectrum #Split into two lines so parent.spectrum can be accessed by the graph
						if parent.spectrum == None:
							print('get_data() == None in spectrometer_stabiliser_class.py')
						#------------------
						#TODO: Implement find_cutoff_wavelength function
						parent.cutoff_wavelength = parent.find_cutoff_wavelength()
						parent.ts = pbec_analysis.make_timestamp(3) #Don't update the ts if acquisition fails!
					except Exception as e:
						traceback.print_exc()
						self.parent.error_message = e
						print "Spectrometer acquisition error. Re-using previous data"
						self.parent.stop_lock()
						self.parent.stop_acquisition()
						self.parent.start_acquisition()
						self.parent.start_lock()
						#
					time.sleep(parent.bandwidth_throttle)
					#Now update the PI Controller
					if not self.lockpaused: #Condition added by BTW 20170720 so the lock can be paused while data is taken, any restarts more seemlessly
						pic.update(parent.ts, parent.cutoff_wavelength)
						if parent.control_gain != 0:
							parent.Vout = parent.control_gain * parent.pic.control_value() + parent.control_offset
						set_cavity_length_voltage(parent.Vout)
						
					#Update spectrometer integration time if need be
					#HERE BE BUGS: TEST PROPERLY PLEASE
					'''
					if max(parent.spectrum)>50000:
						time.sleep(1)
						fly_spec_int_time=fly_spec_int_time/3
						set_spec_int_time(fly_spec_int_time)
						time.sleep(1)
						print 'Lowering spectrometer integration time'
					'''
					#elif max(parent.spectrum<2000):
					#	fly_spec_int_time=fly_spec_int_time*3
					#	set_spec_int_time(fly_spec_int_time)
					
					#Gather the outputs
					r = {"ts":parent.ts, "cutoff_wavelength":parent.cutoff_wavelength, \
						"Vout":round(parent.Vout,3), "pic value":parent.pic.control_value()}
					if parent.print_frequency > 0:
						if len(parent.results) % parent.print_frequency == 0: 
							print r["ts"], r["Vout"], r["cutoff_wavelength"], r["pic value"]
					#Now output a voltage from PI_controller
					parent.results.append(r)
					#Turn this into a reasonable-length buffer, rather than a dump
					buffer_len=2500 #minimum 2000 for GUI plot
					if len(parent.results)>buffer_len: 
						del parent.results[0]
		finally:
			spectro.close()
		print("Finished\n")

class SpectrometerStabiliser():
	def __init__(self,set_point=575):
		self.error_message = None
		self.control_range = default_control_range
		self.control_offset=mean(self.control_range)
		self.control_gain = 0 #0-> no output voltage; 1-> full; -1-> negative
		self.bandwidth_throttle=0.001 #slows down acquisition so other devices can use USB
		self.print_frequency =0#for diagnostic purposes
		self.spec_int_time = default_spec_int_time 
		self.spec_nAverage = default_spec_nAverage
		self.lamb_range	 = default_lamb_range
		#--------------------
		self.results = []
		self.lamb, self.spectrum = [],[]
		self.ts = None
		self.cutoff_wavelength=0#unknown!!!!
		self.set_point = set_point #Desired cutoff_wavelength in nm
		#
		self.spectro = pbec_experiment.Spectrometer(do_setup=False) #Spectrometer object
		#self.spectro = pbec_experiment.Spectrometer(do_setup=True) #Trial by BTW 20170330
		direct_gain_factor=1 #if the gain is too high, reduce this.
		buffer_length=10 #
		self.pic = PI_control(P_gain = direct_gain_factor*default_P_gain,\
			I_gain = direct_gain_factor*default_I_gain,I_const=default_I_const,\
			II_gain = direct_gain_factor*default_II_gain,II_const=default_II_const,\
			buffer_length=buffer_length,\
			control_range=array(self.control_range)-mean(self.control_range),\
			set_point = self.set_point)
		#
		self.initialise_thread()
		self.Vout=mean(self.control_range)
		set_cavity_length_voltage(self.Vout)
	
	def set_voltage(self,voltage):
		self.Vout = voltage
		set_cavity_length_voltage(self.Vout)
		
	def initialise_thread(self):
		self.thread = _SpectrometerStabiliserThread(self) #don't start the thread until you want to acquire
		self.thread.paused=True
		self.thread.start()
	
	def get_single_spectrum(self):
		if not(self.spectro.open):
			self.spectro.setup() #This step is really slow
		self.spectro.start_measure(self.spec_int_time, self.spec_nAverage)
		self.lamb = copy(self.spectro.lamb)
		self.spectrum = self.spectro.get_data()
		self.spectro.close()

	def find_cutoff_wavelength(self):
		cw = mini_utils.FindPeak(self.lamb, self.spectrum, data_lamb_range = default_lamb_range)
		print cw
		if cw ==nan:
			#If not-a-number, reject and use previous value
			cw = self.cutoff_wavelength
		if (cw < max(self.lamb_range)) and (cw > min(self.lamb_range)):
			self.cutoff_wavelength = cw
		return self.cutoff_wavelength
	
	def start_acquisition(self):
		#self.spectro.close() #WHY DO I HAVE TO DO THIS?
		#print "close done at "+pbec_analysis.make_timestamp(3)
		#print "Setting up spectrometer"
		#time.sleep(2)
		self.spectro.setup() #This step is really slow
		#print "setup done at "+pbec_analysis.make_timestamp(3)
		self.spectro.start_measure(self.spec_int_time, self.spec_nAverage)
		#print "start_measure done at "+pbec_analysis.make_timestamp(3)
		self.lamb = copy(self.spectro.lamb)
		#print "copy wavelengths done at "+pbec_analysis.make_timestamp(3)
		self.thread.paused=False
		
	def stop_acquisition(self):
		self.thread.paused=True
		time.sleep(0.5)#avoid race condition. Should really use mutex
		self.spectro.close()
		
	def close_acquisition(self):
		self.stop_acquisition()
		self.thread.running=False
		
	def start_lock(self):
		self.pic.reset() #forget history; reset the integrator etc.
		self.Vout=mean(self.control_range)
		self.control_gain=1.0

	def stop_lock(self):
		self.control_gain=0

"""
from pylab import *
from spectrometerStabiliser import SpectrometerStabiliser
#import spectrometerStabiliser #if need be
#reload(stabiliser_class) #if need be
s = SpectrometerStabiliser()
#s.get_single_spectrum()

s.initialise_thread()
s.start_acquisition() #Causes a slew of errors
len(s.results)
s.stop_acquisition() #Can go back to "start_acquisition" here
s.close_acquisition() #Can go back to "initialise_thread" here
s.results[-1]

#To change the spectrometer settings, e.g.
s.spec_int_time = 2
s.stop_acquisition()
s.start_acquisition()
#It seems like we can get 140 spectra/second with 5 ms int time
#Maybe 180 spectra/second is possible with 2 ms integration (including 1ms throttle/spectrum!)
"""
