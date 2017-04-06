#exit()

#ipython --gui=qt
#exec(open("tektronix.py").read())
import visa

from pylab import *

#---------------------------------
#USB-BASED TEKTRONIX OSCILLOSCOPE CLASS
#---------------------------------
class Tektronix():
	def __init__(self,USB_name="USB0::0x0699::0x03AA::C013639", binary=False):
		USB_name = USB_name
		self.tek = visa.instrument(USB_name)
		s = self.tek.ask("SELECT?")
		select_list = s.split(";")
		self.Nchannels = len(select_list)/ 2 #NOT CHECKED FOR 4-CHAN SCOPE, but expected to work
		self.binary = binary
		if binary:
			self.tek.write("WFMPre:ENC BIN")
		else:
			self.tek.write("WFMPre:ENC ASC")
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
			#self.tek.write("DATA:SOURCE CH"+str(chan))
			#voltage_scales[chan-1]=float(self.tek.ask("WFMPRE:YMULT?"))
			#voltage_scales[chan-1]=float(self.tek.ask("CH1:VOLTS?"))
			voltage_scales[chan-1]=float(self.tek.ask("CH"+str(chan)+":VOLTS?"))
		return voltage_scales #zero values for inactive channels
	def setVoltageScale(self, chan, scale):
		self.tek.write("DATA:SOURCE CH"+str(chan))
		#self.tek.write("WFMPre:YMULT " + str(scale))
		self.tek.write("CH1:VOLTS " + str(scale))
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

	###faster routines for obtaining data
	def getTData(self, rawchanneldata):
		xincr=float(self.tek.ask("WFMPRE:XINCR?"))
		if self.binary:
			data_list = rawchanneldata
		else:
			data_list = rawchanneldata.split(",")
		t_data = xincr*array(range(len(data_list)))
		return t_data
	def setChannel(self, chan):
		self.tek.write("DATA:SOURCE CH "+str(chan))
	def setDataRange(self, start=0, stop=2500):
		''' start and stop are in the range [0, 2500] '''
		self.tek.write("DATa:STARt " + str(start))
		self.tek.write("DATa:STOP " + str(stop))
	def getRawChannelDataAsString(self):
		curve = self.tek.ask("CURVE?")
		return curve
		
	def close(self):
		self.tek.close()
	
	def get_voltage_conversion_values(self):
		yoff = float(self.tek.ask("WFMPre:YOFf?"))
		ymult = float(self.tek.ask("WFMPre:YMUlt?"))
		yzero = float(self.tek.ask("WFMPre:YZEro?"))
		return (yoff, ymult, yzero)
	
	def convert_raw_data_to_volts(self, curve_in_dl, conversion_values):
		yoff, ymult, yzero = conversion_values
		##see page 212 in manual Tektronix_TDS1001C_EDU_programmer_manual.pdf
		value_in_YUNits = ((curve_in_dl - yoff) * ymult) + yzero
		return value_in_YUNits
		
if 0:
	tek = Tektronix()

#EOF
