#exec(open("fianium.py").read())
import serial
import socket
import numpy as np
import time
import numpy.polynomial.polynomial as poly
#NOTE: the visa package seems to timeout when reading,so stick with serial.

if socket.gethostname().lower()=="ph-rnyman2":
    fianium_comport="/dev/ttyUSB0"
elif socket.gethostname().lower()=="ph-photonbec":
    fianium_comport=4
elif socket.gethostname().lower()=="ph-photonbec3":
    fianium_comport=6

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
                if type(comport)==int:
                    self.ser = serial.Serial(comport-1,baudrate=19200,timeout=0.3)    
		else:
                    self.ser = serial.Serial(comport,baudrate=19200,timeout=0.3)

		self.ser.readall()
		self.ser.close()
		self.lastAmplifierControlValue =0
	def close(self):
		self.ser.close()
	def open(self):
		if not(self.ser.isOpen()):
			self.ser.open()
	def writeCommand(self,s,wait_time=10e-2,do_not_close=False):
		self.isInUse = True
		if not(do_not_close): self.open()
		self.ser.write(s+line_end)
		time.sleep(wait_time) #Needed because serial bus is a bit slow. 1ms is unreliabls to leave at 10ms.
		if not(do_not_close): self.close()
		#self.isInUse = False
	def read(self,size=None,do_not_close=False):
		if not(do_not_close): self.open()
		if size!=None:
			res = self.ser.read(size)
		else:
			res = self.ser.readall()
		if not(do_not_close): self.close()
		return res
	def ask(self,s,size=None):
		'''Please do not include the "?" in the asked command'''
		self.open()
		self.writeCommand(s+"?",do_not_close=True)
		return self.read(size,do_not_close=True)
		self.close()
	def enable(self):
		'''
		This command must be run each time the physical key is switched on.
		'''
		self.writeCommand("key=1")
		#self.amplifierBackOn()
	def disable(self):
		self.writeCommand("key=0")
	def getPreamplifierMonitorValue(self):
		return self.ask("P")
		#TODO: convert result to integer
	def getAmplifierControlValue(self):
		return self.ask("Q?")
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
		res = self.ask("Z?")
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
		res = self.ask("U?") 
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
		if type(amp)!=int:
			amp = int(amp)
			if amp > 255 or amp <0: 
				amp = min(255,max(amp,0))
				print "FianiumLaser warning: automatically converting ampliude to an integer value between 0 and 255"
		self.writeCommand("U="+str(address)+" "+str(amp))
	def getAlarms(self):
		self.ask("A")
	def getNumberRepetitionsOutputModulator(self):
		#TODO: parse the text to extract the numerical value
		res = self.ask("K?")
		try:
			parse1 = res.split("Frequency = ")
			parse2 = parse1[1].split(" MHz")[0]
			rep_rate = float(parse2)
		except:
			rep_rate = None
		return rep_rate
	def setNumberRepetitionsOutputModulator(self,numb_rep_out_mod):
		self.writeCommand("K="+str(numb_rep_out_mod))
		return self.getNumberRepetitionsOutputModulator()
		
	def getPulseEnergy(self):
		#WARNING: this function only works for very specific AmpliferControlValues
		#ALSO: what are the units?
		a=self.getAmplifierControlValue()
		cv=a[11:14]
		out_amp=self.getOutputAmplitude()
		if cv=='0\n\r':
			coeffs=[1.94459015e-12,-1.81483740e-09,5.17304397e-07,-4.00311154e-05,8.31747187e-04,-1.65116819e-03]
			pulse_energy=np.polyval(coeffs,out_amp)
		elif cv=='150':
			coeffs=[1.41450562e-11,-1.56935466e-08,4.84624652e-06,-4.02332700e-04,1.05627054e-02,-4.51490621e-02]
			pulse_energy=np.polyval(coeffs,out_amp)
		elif cv=='200':
			coeffs=[1.04214979e-10,-1.37340226e-07,4.41423797e-05,-3.46540682e-03,8.62171737e-02,-3.39443464e-01]
			pulse_energy=np.polyval(coeffs,out_amp)
		elif cv=='300':
			coeffs=[2.61473188e-09,-2.04138516e-06,5.04291260e-04,-3.57951343e-02,8.25651766e-01,-2.91489951e+00]
			pulse_energy=np.polyval(coeffs,out_amp)
		elif cv=='400':
			coeffs=[6.45286337e-09,-4.74508305e-06,1.09800111e-03,-6.98114957e-02,1.43770885e+00,-4.39976880e+00]
			pulse_energy=np.polyval(coeffs,out_amp)
		elif cv=='600':
			coeffs=[1.72181502e-08,-1.13030471e-05,2.27310235e-03,-1.06494515e-01,1.33015298e+00,-1.59100539e-01]
			pulse_energy=np.polyval(coeffs,out_amp)
		elif cv=='800':
			coeffs=[1.23034922e-08,-7.88456449e-06,1.35484993e-03,1.53123638e-02,-2.60172649e+00,1.78468265e+01]
			pulse_energy=np.polyval(coeffs,out_amp)
		else:
			print  'Error: Pulse Energy cannot be read.'
			return None
		return pulse_energy
	def setPulseEnergy(self,pulse_energy):
		cv,out_amp=self.findPulseEnergyParameters2(pulse_energy)
		self.setAmplifierControlValue(int(cv))
		self.setOutputAmplitude(int(out_amp))
	def findPulseEnergyParameters2(self,pulse_energy):
		if 0.1<=pulse_energy<0.6:
			cv = 0
			coeffs=[1.94459015e-12,-1.81483740e-09,5.17304397e-07,-4.00311154e-05,8.31747187e-04,-1.65116819e-03-pulse_energy]
			roots=poly.polyroots(list(reversed(coeffs)))
			out_amp=max([i.real for i in roots if 0<=i<=255])
		elif 0.6<=pulse_energy<6:
			cv = 150
			coeffs=[1.41450562e-11,-1.56935466e-08,4.84624652e-06,-4.02332700e-04,1.05627054e-02,-4.51490621e-02-pulse_energy]
			roots=poly.polyroots(list(reversed(coeffs)))
			out_amp=max([i.real for i in roots if 0<=i<=255])
		elif 6<=pulse_energy<50:
			cv = 200
			coeffs=[1.04214979e-10,-1.37340226e-07,4.41423797e-05,-3.46540682e-03,8.62171737e-02,-3.39443464e-01-pulse_energy]
			roots=poly.polyroots(list(reversed(coeffs)))
			out_amp=max([i.real for i in roots if 0<=i<=255])
		elif 50<=pulse_energy<300:
			cv = 300
			coeffs=[2.61473188e-09,-2.04138516e-06,5.04291260e-04,-3.57951343e-02,8.25651766e-01,-2.91489951e+00-pulse_energy]
			roots=poly.polyroots(list(reversed(coeffs)))
			out_amp=max([i.real for i in roots if 0<=i<=255])
		elif 300<=pulse_energy<800:
			cv = 400
			coeffs=[6.45286337e-09,-4.74508305e-06,1.09800111e-03,-6.98114957e-02,1.43770885e+00,-4.39976880e+00-pulse_energy]
			roots=poly.polyroots(list(reversed(coeffs)))
			out_amp=max([i.real for i in roots if 0<=i<=255])
		elif 800<=pulse_energy<1500:
			cv = 600
			coeffs=[1.72181502e-08,-1.13030471e-05,2.27310235e-03,-1.06494515e-01,1.33015298e+00,-1.59100539e-01-pulse_energy]
			roots=poly.polyroots(list(reversed(coeffs)))
			out_amp=max([i.real for i in roots if 0<=i<=255])
		elif 1500<=pulse_energy<=2500:
			cv = 800
			coeffs=[1.23034922e-08,-7.88456449e-06,1.35484993e-03,1.53123638e-02,-2.60172649e+00,1.78468265e+01-pulse_energy]
			roots=poly.polyroots(list(reversed(coeffs)))
			out_amp=max([i.real for i in roots if 0<=i<=255])
		else:
			print  'Error: Pulse Energy cannot be read.'
			return None
		return cv,out_amp
	def getRepetitionRate(self):
		return self.getOutputRepetitionRate()
	def setRepetitionRate(self,value):
		return self.setOutputRepetitionRate(value)
	def isEnabled(self):
		a=self.ask("key")
		key = a.split("\n\r")
		print key
		if key[0]=='':
			val = None
		else:
			if key[0][12]=='0':
				val=False
				print "Fianium Laser is DISABLED"
			elif key[0][12]=='1':
				val=True
				print "Fianium Laser is ENABLED"
		return val
	def getPower(self):
		rr=self.getOutputRepetitionRate()
		pe=self.getPulseEnergy()
		return float(pe)*float(rr)
	
#Note: there is no "on/off" or power control, but we can set the current control value with "Q"
#NOTE: after switching the physical keyswitch, please write "key=1"	
if 0:
    fia = FianiumLaser()
    fia.enable()
    fia.ask("O") #find out if it's ready to run yet.
    fia.setOutputRepetitionRate(0.01)
    fia.setOutputAmplitude(25) #low power here: doesn't seem to be linear. Threshold?
    fia.setAmplifierControlValue(1) #minimum power please
#The last two commands still don't really make it safe to work without goggles. Probably.

#exec(open("fianium.py").read())
#EoF