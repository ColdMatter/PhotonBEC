#exit()

#sudo ipython
#WARNING: currently only works with root privileges on ph-rnyman2: sudo ipython
#WARNING: line return characters need modifying for ph-photonbec
#See agilent33521a package for compariso
#exec(open("gwinstekAFG2005.py").read())
#import time
import visa
import socket
from numpy import array

#TODO: implement computer-specific device naming, and pyvisa versioning
hostname = socket.gethostname()
if hostname.lower()=="ph-rnyman2":
    AFG_name=u'ASRL/dev/ttyACM1::INSTR' #This name seems to change from time to time. Why?
    backend = "@py"
else:
    AFG_name=u'COM16' #alternatively, "ARSL16" might work better
    backend = "@py"

#---------------------------------
#USB-BASED AGILENT FUNCTION GENERATOR CLASS
#---------------------------------
class GWInstekFunctionGenerator():
	"""
	Connects to our GWInstek function generator over USB. 
	This class implements a few of the possible commands listed 
	in the operating manual. The rest are left as an exercise for 
	the reader.
	
	NOTE: it might prefer being connected via USB2 not USB3.
	Also: does not have "pulse" function
	"""
	def __init__(self,AFG_name=AFG_name,backend = backend):
		AFG_name = AFG_name
		if hostname.lower() in ["ph-rnyman2"]:
                    #For installations with pyvisa version >=? 1.5
                    rm = visa.ResourceManager(backend) #Use pyvisa-py backend
                    self.afg = rm.open_resource(AFG_name)
                else:
                    #For installations with pyvisa versionn <1.5
                    self.afg = visa.instrument(AFG_name)
	def writeCommand(self,s):
                #Once in a while will throw a warning about line return characters, but mostly works.
		self.afg.write(s)
	def outputOn(self):
		self.writeCommand("SOURCE:OUTP ON")
	def outputOff(self):
		self.writeCommand("SOURCE:OUTP OFF")
	def setPulseWidth(self,pulse_width):
		print("Pulsed mode not available")
	def setFrequency(self,frequency):
		#Frequency in Hz
		self.writeCommand("SOURCE:FREQ "+str(frequency))
	def setPulseMode(self):
		print("Pulsed mode not available")
	def setOutputHighZ(self):
		print("Impedance 50R/HighZ cannot be switched or checked remotely")
        def setAmplitude(self,V):
                #Assumes that output is set to VPP not RMS
                self.writeCommand("SOUR:AMPL "+str(V))
        def setOffset(self,V):
                #Assumes that output is set to VPP not RMS
                self.writeCommand("SOUR:DCOffset "+str(V))
	def setHighV(self, V):
		print("High voltage cannot be directly set: please set Amplitude and Offset")
	def setLowV(self, V):
		print("Low voltage cannot be directly set: please set Amplitude and Offset")
	def setTTLOut(self):
                #TODO Check output voltages are correct
		self.setAmplitude(5)
		self.setOffset(2.5)
	def setDefaultParams(self):
		self.outputOn()
		self.setFrequency(500) #500 Hz repetition rate
		self.setTTLOut()
	def getPulseWidth(self):
		print("Pulsed mode not available")
	def getFrequency(self):
		return float(self.afg.ask("SOURCE1:FREQ?\r\n"))
        def setFunction(self,func="sin"):
                func_list = ["sin","squ","ramp","nois","arb"]
                if func.lower() in func_list:
                    FUNC = func.upper()
                    self.afg.write("SOURCE:FUNC "+FUNC) #Set square wave
                    if func.lower=="arb":
                        print "Warning: you will need to upload data to make the ARBITRARY waveforms work"
                else:
                    print "Function unknown, try one of "+str(func_list)
        def setWaveformUnscaledData(self,unscaled_data):
            #Doesn't fix amplitude. Scales all data so that peak is same as amplitude.
            data_arr = array(unscaled_data)
            data_peak = abs(data_arr).max()
            max_val = 511#sets the max scale, proportional to output voltage scale?
            data_normalised = max_val * data_arr / float(data_peak)
            data_int = array([int(dn) for dn in data_normalised])
            vec = ','.join("%.0f" % i for i in data_int)
            afg.afg.write("DATA:DAC VOLATILE,0,%s" % (vec,)) #To be verified
        def setWaveformScaledData(self,data):
            #Takes float data. Sets output to data values in Volts.
            data_arr = array(data)
            data_peak = abs(data_arr).max()
            self.setAmplitude(data_peak)
            self.setWaveformUnscaledData(data)
        def setArbitraryFunction(self,data):
            #Takes values in Volts and puts them into the AFG's data, then sets to the function to ARBITRARY.
            self.setWaveformScaledData(data)
            self.setFunction("arb")
            #Doesn't work directly like that.
            #Now what?
            
"""TESTING
import visa
rm = visa.ResourceManager("@py") #Use pyvisa-py backend
rm.list_resources('?*') #But it doesn't seem to find USB devices (does find ASRL)
#Needs root access: sudo ipython
afg = rm.open_resource(AFG_USB_NAME)
afg.query("*IDN?") #Finally, it works
"""

"""
#On ph-photonbec, pyvisa is an old version, so different commands are needed.
import visa
visa.get_instruments_list()
#It appears that at least one of the AFGs (we have two) is called "COM16"
"""

if __name__=="__main__":
    afg = GWInstekFunctionGenerator()
    #afg.setDefaultParams()
    pass

'''
#Testing arbitrary waveforms"
from numpy import sin
data=[2*sin((x/100.)**2) for x in range(1000)]
afg.setArbitraryFunction(data)
afg.setFrequency(1000)
'''

#exec(open("gwinstekAFG2005.py").read())
#EoF

#A block of code hacked from the web.
