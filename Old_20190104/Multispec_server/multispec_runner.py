#NOTE: Uses pi_controller class, which is currently based in "CavityLock" folder, but will be moved to PythonPackages
#This class re-uses a lot of code from /Control/CavityLock/stabiliser_class.py
import sys
from socket import gethostname
if gethostname()=="ph-rnyman-01":
	sys.path.append("D:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec2":
	sys.path.append("Y:\\Control\\PythonPackages\\")
elif gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")

from hene_utils import *
from pbec_experiment_multispec import *
import pbec_experiment_multispec
import pbec_analysis_multispec
from pi_controller import PI_control
import threading
import traceback


#----------------------------------
#COMPUTER SPECIFIC SETTINGS HERE
if gethostname()=="ph-photonbec":
	default_spec_int_time = 20
	default_spec_nAverage = 1
	default_lamb_range = (540,610) #Restrict range analysed, which might make acquisition faster
elif gethostname()=="ph-photonbec2":
	default_spec_int_time = 40
	default_spec_nAverage = 1
	default_lamb_range = (555,585) #Restrict range analysed, which might make acquisition faster
elif gethostname()=="ph-photonbec3":
	default_lamb_range = (540,600) #Restrict range analysed, which might make acquisition faster
	only_one_spec = True
	if only_one_spec:
		default_spec_n_averages = [1]
		default_no_spectrometers = 1
		spectrometer_list = ['newbie'] #These have to be correct and in the order that avs_spectro deems fit to open them.
		default_spec_int_times = [2]
	else:	
		default_spec_n_averages = [1,1,1]
		default_no_spectrometers = 3
		spectrometer_list = ['grey','newbie','black'] #These have to be correct and in the order that avs_spectro deems fit to open them.
		default_spec_int_times = [3,10,3]
	
#----------------------------------

class _MultiSpectrometerThread(threading.Thread):
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
		spectros = parent.spectros #assumes spectrometer is setup
		fail_num = 0
		#try:
		while self.running:
			#why the double loop? so it can be paused and unpaused
			time.sleep(1e-3) #when paused, while loop not going mental
			while not self.paused:
				#insert the controller actions here
				try:
					temp_spectum=[]
					for spectro in parent.spectros:
						spectro.get_data()
						spectro.ts = pbec_analysis.make_timestamp(3)
					#parent.spectrum = temp_spectrum #Split into two lines so parent.spectrum can be accessed by the graph
					if parent.spectrum == None:
						print('get_data() == None in spectrometer_stabiliser_class.py')
					#------------------
					parent.ts = pbec_analysis.make_timestamp(3) #Don't update the ts if acquisition fails!
					fail_num = 0
				except IOError:
					if fail_num < 4:
						time.sleep(1)
						fail_num+=1
					else:
						self.parent.start_acquisition()
						fail_num=0
				except Exception as e:
					traceback.print_exc()
					self.parent.error_message = e
					print "Spectrometer acquisition error. Re-using previous data"
					#self.parent.stop_acquisition()
					#self.parent.start_acquisition()
					#
				time.sleep(parent.bandwidth_throttle)
					
				#Update spectrometer integration time if need be
				#HERE BE BUGS: TEST PROPERLY PLEASE
				
				#Gather the outputs
				r = {"ts":parent.ts}
				if parent.print_frequency > 0:
					if len(parent.results) % parent.print_frequency == 0: 
						print r["ts"]
				#Now output a voltage from PI_controller
				parent.results.append(r)
				#Turn this into a reasonable-length buffer, rather than a dump
				buffer_len=2500 #minimum 2000 for GUI plot
				if len(parent.results)>buffer_len: 
					del parent.results[0]
		#finally:
		#	spectro.close()
		print("Finished\n")

class MultiSpectrometers():
	def __init__(self):
		self.error_message = None
		self.bandwidth_throttle=0.001 #slows down acquisition so other devices can use USB
		self.print_frequency =0#for diagnostic purposes
		self.spec_int_times = default_spec_int_times
		self.spec_n_averages = default_spec_n_averages
		self.lamb_range	 = default_lamb_range
		self.num_spectrometers = default_no_spectrometers
		self.min_spec_int_times = [min_int_time_spectrometerLabel_map[name] for name in spectrometer_list]
		#--------------------
		self.results = []
		self.lambs, self.spectra = [[] for i in range(self.num_spectrometers)],[[] for i in range(self.num_spectrometers)]
		#self.lamb, self.spectrum = [],[]
		self.ts = None
		self.spectros = []
		self.spectros.append(pbec_experiment_multispec.Spectrometer(name=spectrometer_list[0])) #Spectrometer object
		for i in range(self.num_spectrometers-1):
			try:
				name = spectrometer_list[i+1]
				self.spectros.append(pbec_experiment_multispec.Spectrometer(do_setupavs=False,name=name,handle=i+2)) #Spectrometer object
			except KeyError:
				print "You're trying to open more spectrometers than you have (I think)."
		self.lamb = self.spectros[0].lamb
		buffer_length=10 #
		print "Initialising thred"
		self.initialise_thread()
			
	def initialise_thread(self):
		self.thread = _MultiSpectrometerThread(self) #don't start the thread until you want to acquire
		print "Initial"
		self.thread.paused=True
		print "Paused"
		self.thread.start()
		print "Started"
		
	def start_acquisition(self):
		#self.spectro.setup() #This step is really slow
		try:
			for i,spectro in enumerate(self.spectros):
				spectro.start_measure(self.spec_int_times[i], self.spec_n_averages[i])
		except IOError:
			self.stop_acquisition()
			self.start_acquisition()
		self.lamb = copy(self.spectros[0].lamb)
		self.thread.paused=False
		
	def stop_acquisition(self):
		self.thread.paused=True
		time.sleep(0.5)#avoid race condition. Should really use mutex
		print "Stopping measure"
		for spectro in self.spectros:
			spectro.stop_measure()
		#spectros[-1].closedll()
		
	def close_acquisition(self):
		self.stop_acquisition()
		self.thread.running=False
