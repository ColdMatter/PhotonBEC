#exec(open("fianium.py").read())
import serial
import socket
#NOTE: the visa package seems to timeout when reading,so stick with serial.

fianium_comport = 17
line_end="\r\n"
#ser = serial.Serial(comport-1,baudrate=19200,timeout=1)
#ser.write("T?"+line_end) #"T?" chassis temperature
#ser.readall()

#---------------------------------
#USB-BASED AGILENT FUNCTION GENERATOR CLASS
#---------------------------------
class FianiumLaser():
	"""
	Connects to our Fianium pulsed laser over USB. 
	This class implements a few of the possible commands listed 
	in the operating manual. The rest are left as an exercise for 
	the reader.
	
	Note that the parsing of results is very poorly tested, and likely
	to cause errors. Caveat emptor!
	"""
	def __init__(self,comport = fianium_comport):
		self.ser = serial.Serial(comport-1,baudrate=19200,timeout=0.3)
		self.lastAmplifierControlValue =0
	def close(self):
		self.ser.close()
	def open(self):
		self.ser.open()
	def writeCommand(self,s):
		self.ser.write(s+line_end)
	def read(self,size=None):
		if size!=None:
			res = self.ser.read(size)
		else:
			res = self.ser.readall()
		return res
	def ask(self,s,size=None):
		'''Please do not include the "?" in the asked command'''
		self.writeCommand(s+"?")
		return self.read(size)
	def enable(self):
		'''
		This command must be run each time the physical key is switched on.
		'''
		self.writeCommand("key=1")
	def disable(self):
		self.writeCommand("key=0")
	def getPreamplifierMonitorValue(self):
		return self.ask("P")
		#TODO: convert result to integer
	def getAmplifierControlValue(self):
		return self.ask("Q")
	def __getAmplifierControlValueMax__(self):
		return self.ask("S")
		#Gives back "Puma current limit for divide by 40 is 0800"
		#What does that mean????
	def setAmplifierControlValue(self,value):
		'''
		Range should be 0000 to 0800
		'''
		self.writeCommand("Q="+str(value))
		self.lastAmplifierControlValue=value
	def amplifierOff(self):	
		self.writeCommand("Q=0") #doesn't seem to work!
	def amplifierBackOn(self):	
		self.setAmplifierControlValue(self.lastAmplifierControlValue)
	def __getRepetitionRate__(self):
		return self.ask("R")
	def __setRepetitionRate__(self,rep_rate_MHz):
		self.writeCommand("R="+str(rep_rate_MHz))#I don't yet know why this doesn't work
	def getOutputRepetitionRate(self):
		#TODO: parse the text to extract the numerical value
		res = self.ask("Z")
		try:
			parse1 = res.split("Frequency = ")
			parse2 = parse1[1].split(" MHz")[0]
			rep_rate = float(parse2)
		except:
			rep_rate = None
		return rep_rate
	def setOutputRepetitionRate(self,rep_rate_MHz):
		'''
		Rep rate should be in range 0.0101 to 0.5 (Units: MHz).
		i.e. 10 kHz will be "out of range", as will 510 kHz
		NOTE: result isn't always what you expect. 
		It's only possible to sub-divide the (0.5 MHz) amplifier rep rate!
		It's only possible to sub-divide the (0.5 MHz) amplifier rep rate!
		'''
		self.writeCommand("Z="+str(rep_rate_MHz))
		return self.getOutputRepetitionRate()
	def getOutputAmplitude(self,address=0):
		#The result needs some serious parsing
		#Currently only reads address zero, or all at once
		res = self.ask("U") 
		if address==0:
			parse1 = res.split("Amplitude")[1].split("\n\r")[0]
			parse2 = parse1.split(" ")[1]
			amp = int(parse2) #integer from 0 to 255
		else:
			amp = res
		return amp
	def setOutputAmplitude(self,amp,address=0):
		'''amp is integer in range 0 to 255
		address is integer 0-9, referring to which member of a pulse train.'''
		self.writeCommand("U="+str(address)+" "+str(amp))
	def getAlarms(self):
		self.ask("A")
		
#Note: there is no "on/off" or power control, but we can set the current control value with "Q"
#NOTE: after switching the physical keyswitch, please write "key=1"	
fia = FianiumLaser()
fia.enable()
fia.setOutputRepetitionRate(0.5)
fia.setOutputAmplitude(25) #low power here: doesn't seem to be linear. Threshold?
fia.setAmplifierControlValue(1) #minimum power please
#The last two commands still don't really make it safe to work without goggles. Probably.

#exec(open("fianium.py").read())
#EoF