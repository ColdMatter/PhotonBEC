#exit()

#ipython --gui=qt
#exec(open("tektronix.py").read())
import visa
from pylab import *

#---------------------------------
#USB-BASED TEKTRONIX OSCILLOSCOPE CLASS
#---------------------------------

if 0:
	USB_name="USB0::0x0699::0x03AA::C013639"
	#Alternatively: USB_name = visa.get_instruments_list()[0]
	tek=visa.instrument(USB_name)
	tek.write("ACQ?\r\n")
	print(tek.read_raw())
	tek.ask("ACQ?")
	tek.ask("DIS?")
	tek.ask("WAVF?")
	#
	tek.write("DATA:ENC ASCII")
	#tek.write("CH1:VOLTS 2E-3")
	tek.write("DATA:SOURCE CH1")
	tek.write("HOR:MAIN:SCALE 20e-3")
	#
	#ymult=float(tek.ask("WFMPRE:YMULT?"))
	#xincr=float(tek.ask("WFMPRE:XINCR?"))
	#dump = tek.ask("CURVE?")
	#data = array(dump.split(","),dtype=int)
	#plot(ymult*data)

def get_data_crude():
	#A crude function to return some data from a TEKTRONIX oscilloscope.
	#BROKEN!!!
	ymult=float(tek.ask("WFMPRE:YMULT?"))
	xincr=float(tek.ask("WFMPRE:XINCR?"))
	dump = tek.ask("CURVE?")
	data = ymult*array(dump.split(","),dtype=int)
	t = xincr*array(range(len(data)))
	clf()
	plot(t,data)
	show
	return t,data

class Tektronix():
	def __init__(self,USB_name="USB0::0x0699::0x03AA::C013639"):
		USB_name = USB_name
		self.tek = visa.instrument(USB_name)
		s = self.tek.ask("SELECT?")
		select_list = s.split(";")
		self.Nchannels = len(select_list)/ 2 #NOT CHECKED FOR 4-CHAN SCOPE, but expected to work
	def stopAcquisition(self):
		self.tek.write("ACQ:STATE STOP")
	def startAcquisition(self, run_once=False):
		if run_once:
			self.tek.write("ACQ:STOPAFTER SEQUENCE")
		else:
			self.tek.write("ACQ:STOPAFTER RUNSTOP")
		self.tek.write("ACQ:STATE RUN")
	def setAverages(self,num_averages=1):
		if num_averages==1:
			self.tek.write("ACQ:MOD SAMPLE")
		else:
			avg_options = [4,16,64,128]
			if num_averages not in avg_options:
				print "Unacceptable number of averages. Choose from "+str(avg_options)
			else:
				self.tek.write("ACQ:MOD AVERAGE")
				self.tek.write("ACQ:NUMAVG "+str(num_averages))
		#
	def getTimeBase(self):
		s = self.tek.ask("HOR:MAIN:SCALE?")
		self.timebase=float(s)
		#TODO: Still needs to be converted into time-per-sample
		return self.timebase
	def setTimeBase(self,timebase):
		self.tek.write("HOR:MAIN:SCALE "+str(timebase))
	def getActiveChannels(self):
		s = self.tek.ask("SELECT?")
		select_list = s.split(";")
		active_channels = []
		for i in range(self.Nchannels):
			if int(select_list[i]):
				active_channels.append(i+1)
		return(active_channels)
	def setActiveChannels(self,channels=[1,2]):
		possible_channels=[1,2]
		for c in possible_channels:
			self.tek.write("SELECT:CH"+str(c)+" OFF")
		if isscalar(channels):
			self.tek.write("SELECT:CH"+str(channels)+" ON")
		else:
			for c in channels:
				self.tek.write("SELECT:CH"+str(c)+" ON")
		#
	def getVoltageScales(self):
		voltage_scales = zeros(self.Nchannels)
		for chan in self.getActiveChannels():
			self.tek.write("DATA:SOURCE CH"+str(chan))
			voltage_scales[chan-1]=float(self.tek.ask("WFMPRE:YMULT?"))
		return voltage_scales #zero values for inactive channels
	def setVoltageBase(self,channel):
		pass
	def getData(self):
		voltage_scales = self.getVoltageScales()
		channel_data = [[]]*self.Nchannels #empty lists for data
		t_data = []
		for chan in self.getActiveChannels():
			self.tek.write("DATA:SOURCE CH"+str(chan))
			curve=self.tek.ask("CURVE?")
			yoffset=voltage_scales[chan-1]*int(float(self.tek.ask("WFMPRE:YOFF?"))) #FIXME? Is there a problem here?
			channel_data[chan-1]=voltage_scales[chan-1]*array(curve.split(","),dtype=int) - yoffset
		xincr=float(self.tek.ask("WFMPRE:XINCR?"))
		t_data = xincr*array(range(len(channel_data[chan-1])))
		return t_data,channel_data #empty arrays for inactive channels
	

if 1:
	tek = Tektronix()

#EOF
