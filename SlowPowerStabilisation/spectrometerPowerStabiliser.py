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
import threading
import traceback
import pbec_ipc
from time import sleep

sys.path.append("D:\\Control\\FianiumController\\")
from fianium import FianiumLaser
#fia = FianiumLaser()

#----------------------------------
#COMPUTER SPECIFIC SETTINGS HERE
if gethostname()=="ph-photonbec3":
	import SingleChannelAO
	#This could be defined to use the PiezoController server program instead
		
	laser = "Fianium"
	fianium_port = pbec_ipc.PORT_NUMBERS["fianium_controller"]
	fianium_host = 'localhost'

	
	def set_AOM_voltage(v):
		try:
			SingleChannelAO.SetAO0(v,device='Dev1')
		except:
			print "PROBABLY A DAQ BOARD ERROR"
		finally:
			return
	def set_AOM_voltage_Fianium(v):
		try:
			SingleChannelAO.SetAO1(v,device="Dev2",channel="ao1")
		except:
			print "PROBABLY A DAQ BOARD ERROR"
		finally:
			return
	def set_pulse_energy(v):
		try:
		#sleep(1)
			#pbec_ipc.ipc_exec("fia.setPulseEnergy("+str(v)+")",port=fianium_port,host=fianium_host)
			#fia.setPulseEnergy(str(v))
			print "Not setting pulse energy at the moment"
		except:
			print "Error setting pulse energy"
		finally:
			return
			
	if laser=="Fianium":
		set_output = set_AOM_voltage_Fianium
	elif laser=="LaserQuantum":
		set_output = set_AOM_voltage
	
	def set_spec_int_time(t):
		pbec_ipc.ipc_exec('setSpectrometerIntegrationTime('+str(t)+'pause_lock=False)',port=47905,host='ph-photonbec2')
	if laser=="LaserQuantum":
		default_P_gain = -1e-6
		default_I_gain = -1e-6
		default_I_const = 10
		default_II_gain = +0.001 #note sign is always positive: square of sign of I gain
		default_II_const=50
		default_control_range = (0.5,1.0)
		default_spec_int_time = 20
		default_spec_nAverage = 1
		default_out_amp = 0
	elif laser=="Fianium":
		default_P_gain = 0
		default_I_gain = 0
		default_I_const = 100
		default_II_gain = 0 #note sign is always positive: square of sign of I gain
		default_II_const=1000
		default_control_range = (2.5,4.5)
		default_spec_int_time = 20
		default_spec_nAverage = 1
		default_out_amp	= 0
	default_lamb_range = (540,600) #Restrict range analysed, which might make acquisition faster
	default_lamb_bec_max = 575
	default_lamb_bec_min = 570
	default_lamb_cloud_min = 560
	start_pixel,stop_pixel = 608, 620
	default_output_metric = "BEC_population"
	
	spectrometer_server_port = pbec_ipc.PORT_NUMBERS["spectrometer_server"]
	spectrometer_server_host = 'localhost'
	spectrometer_name = "newbie"
	spectrometer_numbers = {'newbie':1}
	spectrometer_number = spectrometer_numbers[spectrometer_name]
	spectrum_int_time = pbec_ipc.ipc_eval("s.spec_int_times["+str(spectrometer_number)+"]",port=spectrometer_server_port,host=spectrometer_server_host)
	spectrum_n_averages = pbec_ipc.ipc_eval("s.spec_n_averages["+str(spectrometer_number)+"]",port=spectrometer_server_port,host=spectrometer_server_host)	

#----------------------------------

class _SpectrometerPowerStabiliserThread(threading.Thread):
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
		#spectro = parent.spectro #assumes spectrometer is setup
		pic = parent.pic #PI controller
		try:
			while self.running:
				#why the double loop? so it can be paused and unpaused
				time.sleep(1e-2) #when paused, while loop not going mental
				while not self.paused:
					#insert the controller actions here
					try:
						temp_spectrum=[]
						#temp_spectrum = parent.spectro.get_data()
						temp_spectrum = pbec_ipc.ipc_get_array("s.spectros["+str(spectrometer_number)+"].spectrum",port=spectrometer_server_port,host=spectrometer_server_host)
						parent.spectrum = temp_spectrum #Split into two lines so parent.spectrum can be accessed by the graph
						if parent.spectrum == None:
							print('get_data() == None in spectrometer_stabiliser_class.py')
						#------------------
						#TODO: Implement find_output_power function
						parent.output_power = parent.find_output_power()
						print parent.output_power
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
						pic.update(parent.ts, parent.output_power)
						if parent.control_gain != 0:
							parent.Vout = parent.control_gain * parent.pic.control_value() + parent.control_offset
						set_output(parent.Vout)
						
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
					r = {"ts":parent.ts, "output_power":parent.output_power, \
						"Vout":round(parent.Vout,3), "pic value":parent.pic.control_value()}
					if parent.print_frequency > 0:
						if len(parent.results) % parent.print_frequency == 0: 
							print r["ts"], r["Vout"], r["output_power"], r["pic value"]
					#Now output a voltage from PI_controller
					parent.results.append(r)
					#Turn this into a reasonable-length buffer, rather than a dump
					buffer_len=2500 #minimum 2000 for GUI plot
					if len(parent.results)>buffer_len: 
						del parent.results[0]
		finally:
			#spectro.close()
			print "In the finally"
		print("Finished\n")

class SpectrometerPowerStabiliser():
	def __init__(self,set_point=50000):
		self.error_message = None
		self.control_range = default_control_range
		self.control_offset=mean(self.control_range)
		self.control_gain = 0 #0-> no output voltage; 1-> full; -1-> negative
		self.bandwidth_throttle=0.001 #slows down acquisition so other devices can use USB
		self.print_frequency =0#for diagnostic purposes
		self.spec_int_time = spectrum_int_time 
		self.spec_nAverage = spectrum_n_averages
		self.lamb_range	 = default_lamb_range
		#--------------------
		self.results = []
		self.lamb = pbec_ipc.ipc_get_array("s.spectros["+str(spectrometer_number)+"].lamb",port=spectrometer_server_port,host=spectrometer_server_host)
		self.spectrum = []
		self.ts = None
		self.output_power=0#unknown!!!!
		self.set_point = set_point #Desired output_power in nm
		#
		#self.spectro = pbec_experiment.Spectrometer(do_setup=False) #Spectrometer object
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
		#self.Vout=mean(self.control_range) * 1.5 #Hard coding by Ben 20171129 to allow more power through AOM as standard
		set_output(self.Vout)
		self.lamb_bec_max = default_lamb_bec_max
		self.lamb_bec_min = default_lamb_bec_min
		self.lamb_cloud_min = default_lamb_cloud_min
		self.pixel_bec_max = min(enumerate(self.lamb), key=lambda x: abs(x[1]-self.lamb_bec_max))[0]
		self.pixel_bec_min = min(enumerate(self.lamb), key=lambda x: abs(x[1]-self.lamb_bec_min))[0]
		self.pixel_cloud_min = min(enumerate(self.lamb), key=lambda x: abs(x[1]-self.lamb_cloud_min))[0]
		self.output_metric = default_output_metric
		self.laser = laser
		self.fianium_output_amplitude = default_out_amp
		#self.laser_object = fia
		
		#Set the Fianium laser up to take voltages by serial
	
	def set_voltage(self,voltage):
		self.Vout = voltage
		set_output(self.Vout)
		
	def initialise_thread(self):
		self.thread = _SpectrometerPowerStabiliserThread(self) #don't start the thread until you want to acquire
		self.thread.paused=True
		self.thread.start()
	
	def get_single_spectrum(self):
		self.spectrum = pbec_ipc.ipc_get_array("s.spectros["+str(spectrometer_number)+"].spectrum",port=spectrometer_server_port,host=spectrometer_server_host)
		
	def find_output_power(self):
		if self.output_metric == "BEC_population":
			power_out = sum(self.spectrum[self.pixel_bec_min:self.pixel_bec_max])
		elif self.output_metric == "BEC_fraction":
			power_out = sum(self.spectrum[self.pixel_bec_min:self.pixel_bec_max])/sum(self.spectrum[self.pixel_cloud_min:self.pixel_bec_max])
		elif self.output_metric == "Total_population":
			power_out = sum(self.spectrum[self.pixel_cloud_min:self.pixel_bec_max])
		print power_out
		if power_out ==nan:
			#If not-a-number, reject and use previous value
			power_out = self.output_power
		self.output_power = power_out
		return self.output_power
	
	def start_acquisition(self):
		#self.spectro.close() #WHY DO I HAVE TO DO THIS?
		#print "close done at "+pbec_analysis.make_timestamp(3)
		#print "Setting up spectrometer"
		#time.sleep(2)
		#self.spectro.setup() #This step is really slow
		#print "setup done at "+pbec_analysis.make_timestamp(3)
		#self.spectro.start_measure(self.spec_int_time, self.spec_nAverage)
		#print "start_measure done at "+pbec_analysis.make_timestamp(3)
		#self.lamb = copy(self.spectro.lamb)
		#print "copy wavelengths done at "+pbec_analysis.make_timestamp(3)
		if self.laser == "Fianium":
			
			sleep_time_fia = 0.1
			pbec_ipc.ipc_exec("ui.power_timer_checkBox.setCheckState(0)",port=fianium_port,host=fianium_host)
			sleep(sleep_time_fia)
			pbec_ipc.ipc_exec("fia.disable()",port=fianium_port,host=fianium_host)
			sleep(sleep_time_fia)
			pbec_ipc.ipc_exec("fia.setU("+str(int(default_out_amp))+")",port=fianium_port,host=fianium_host)
			sleep(sleep_time_fia)
			pbec_ipc.ipc_exec("fia.setQ(0)",port=fianium_port,host=fianium_host)
			sleep(sleep_time_fia)
			pbec_ipc.ipc_exec('fia.setMode(2)',port=fianium_port,host=fianium_host)
			sleep(sleep_time_fia)
			pbec_ipc.ipc_exec('fia.ask("M")',port=fianium_port,host=fianium_host)
			sleep(sleep_time_fia+2)
			pbec_ipc.ipc_exec('fia.ask("M")',port=fianium_port,host=fianium_host)
			sleep(sleep_time_fia)
			pbec_ipc.ipc_exec("fia.enable()",port=fianium_port,host=fianium_host)
			sleep(sleep_time_fia)
			pbec_ipc.ipc_exec("ui.power_timer_checkBox.setCheckState(2)",port=fianium_port,host=fianium_host)

			'''
			self.laser_object.disable()
			self.laser_object.writeCommand("M=2")
			self.laser_object.ask("M")
			self.laser_object.ask("M")
			self.laser_object.writeCommand("U=0 "+str(int(default_out_amp)))
			self.laser_object.enable()
			'''
		self.thread.paused=False
		
	def stop_acquisition(self):
		self.thread.paused=True
		time.sleep(0.5)#avoid race condition. Should really use mutex
		#self.spectro.close()
		
	def close_acquisition(self):
		self.stop_acquisition()
		self.thread.running=False
		
	def start_lock(self):
		self.pic.reset() #forget history; reset the integrator etc.
		self.Vout=mean(self.control_range)
		self.control_gain=1.0

	def stop_lock(self):
		self.control_gain=0
		
	def change_fianium_output_amplitude(self, out_amp):
		#print 'fia.writeCommand("U=0 ' +str(int(out_amp))+'")'
		pbec_ipc.ipc_exec("ui.power_timer_checkBox.setCheckState(0)",port=fianium_port,host=fianium_host)
		pbec_ipc.ipc_exec("fia.setU("+str(int(out_amp))+")",port=fianium_port,host=fianium_host)
		pbec_ipc.ipc_exec("ui.power_timer_checkBox.setCheckState(2)",port=fianium_port,host=fianium_host)
		#self.laser_object.writeCommand("U=0 " +str(int(out_amp)))
		self.fianium_output_amplitude = out_amp

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
