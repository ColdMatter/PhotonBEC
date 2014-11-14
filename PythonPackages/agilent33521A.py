#exit()

#ipython
#exec(open("agilent33521A.py").read())
import visa

#---------------------------------
#USB-BASED AGILENT FUNCTION GENERATOR CLASS
#---------------------------------
class AgilentFunctionGenerator():
	"""
	Connects to our Agilent 33521A function generator over USB. 
	This class implements a few of the possible commands listed 
	in the operating manual. The rest are left as an exercise for 
	the reader.
	
	NOTE: it seems to prefer being connected via USB2 not USB3.
	"""
	def __init__(self,USB_name="USB0::0x0957::0x1607::MY50003870"):
		USB_name = USB_name
		self.agilent = visa.instrument(USB_name)
	def writeCommand(self,s):
		self.agilent.write(s+"\r\n")
	def outputOn(self):
		self.writeCommand("OUTP ON")
	def outputOff(self):
		self.writeCommand("OUTP OFF")
	def setPulseWidth(self,pulse_width):
		#Pulse width in seconds
		self.writeCommand("FUNC:PULS:WIDT "+str(pulse_width))
	def setFrequency(self,frequency):
		#Frequency in Hz
		self.writeCommand("FREQ "+str(frequency))
	def setPulseMode(self):
		self.writeCommand("SOUR:FUNC PULS")
	def setOutputHighZ(self):
		self.writeCommand("OUTP:LOAD INF")
	def setTTLOut(self):
		self.writeCommand("SOUR:VOLT:HIGH 5")
		self.writeCommand("SOUR:VOLT:LOW 0")
	def setDefaultParams(self):
		self.outputOn()
		self.setOutputHighZ()
		self.setPulseMode()
		self.setPulseWidth(500e-9) #500 ns pulses
		self.setFrequency(500) #500 Hz repetition rate
		self.setTTLOut()
	def getPulseWidth(self):
		return self.agilent.ask("FUNC:PULS:WIDT?\r\n")

#TESTING
"""
#USB_function_generator_name = visa.get_instruments_list()[1] #not sure about the index here. [0] is for tektronix. Robustness?

USB_function_generator_name= "USB0::0x0957::0x1607::MY50003870"

agilent=visa.instrument(USB_function_generator_name)
agilent.write("FUNC:PULS:WIDT 3E-7\r\n") #set pulse width to 0.3 microseconds
agilent.write("FREQ 2E5\r\n") #set pulse rate to 200 kHz
agilent.write("OUTP ON\r\n") #output on
#pulse_width_text = agilent.ask("FUNC:PULS:WIDT?")
"""
#
#agilent = AgilentFunctionGenerator()
#agilent.getPulseWidth()

#EoF
