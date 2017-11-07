#execfile("ThorlabsMDT69xA.py")
import serial
from socket import gethostname
#noisy line added 19/4/16
hostname = gethostname()
if gethostname()=="ph-photonbec":
	comports={"3chan":3,"1chan":4}
	default_Nchannels=3
elif gethostname()=="ph-photonbec2":
	default_Nchannels=1
	comports={"3chan":4,"1chan":4}
elif gethostname()=="ph-photonbec3":
	comports={"3chan":2,"1chan":4}
	default_Nchannels=3
else:
	print "This is not a control computer! Why do you want to control piezos?\n"

baud_rates={"3chan":115200,"1chan":115200} #Don't know why they're different
model_numbers={"3chan":"MDT693B","1chan":"MDT694A"}

class ThorlabsMDT69xA():
    def __init__(self, Nchannels=default_Nchannels, keep_open=False):
        self.Nchannels=Nchannels
        if Nchannels not in [1, 3]:
                print "Unknown number of channels. Try again with either 3 or 1"
        chan_name = str(Nchannels)+"chan"
        self.comport = comports[chan_name]#for COM<x> set comport = <x>-1
        self.model_number = model_numbers[chan_name]
        baud_rate = baud_rates[chan_name]
	self.keep_open = keep_open
        self.ser = serial.Serial(port=self.comport-1, timeout=5, baudrate=baud_rate)
	if not self.keep_open:
		self.ser.close()
    def writeCommand(self,s):
        if not(self.ser.isOpen()):
		self.ser.open()
        self.ser.write(s+"\r\n")
        if not self.keep_open:
		self.ser.close()
    def readSerial(self,bytes=None):
        if not self.ser.isOpen():
		self.ser.open()
        if bytes==None:
            s=self.ser.readall()
        else:
            s=self.ser.read(bytes)
        if not self.keep_open:
		self.ser.close()
        return s
    def setChanVolts(self,chan,chanV):
        channel_conversion = dict(zip(range(1, self.Nchannels+1), ["X","Y","Z"]))
        if chan in channel_conversion.keys():
            chan = channel_conversion[chan]
        elif type(chan)==str and chan.upper() not in channel_conversion.values():
            print "Channel number too large. How many outputs do you think the "+self.model_number+" has?"
        self.writeCommand(chan + "V" + str(chanV))
    def getChanVolts(self,chan):
        channel_conversion = dict(zip(range(1, self.Nchannels+1), ["X","Y","Z"]))
        if chan in channel_conversion.keys():
            chan = channel_conversion[chan]
        elif type(chan) == str and chan.upper() not in channel_conversion.values():
            print "Channel number too large. How many outputs do you think the "+self.model_number+" has?"
        self.writeCommand(chan.upper()+"R?")
        s = self.readSerial()
        #now parse the result: can be unreliable
        try: 
            chanV = float(s.split("[")[-1].split("]")[0])
        except:
            print "Failed to interpret the results. Try again, it might work next time. Really."
            chanV="Not a number"
        return chanV
    def setXvolts(self,V): self.setChanVolts("X",V)
    def getXvolts(self): return self.getChanVolts("X")
    def setYvolts(self,V): self.setChanVolts("Y",V)
    def getYvolts(self): return self.getChanVolts("Y")
    def setZvolts(self,V): self.setChanVolts("Z",V)
    def getZvolts(self): return self.getChanVolts("Z")


if __name__=="__main__":
    interferometer_pzt = ThorlabsMDT69xA(Nchannels=3)
    cavity_pzt= ThorlabsMDT69xA(Nchannels=1) #seems not to be working for now...
"""
To instantiate you could try closing down any other PZT control sofware and then:
>>>from ThorlabsMDT69xA import *
>>>interferometer_pzt = ThorlabsMDT69xA(Nchannels=3)
>>>cavity_pzt= ThorlabsMDT69xA(Nchannels=1) #seems not to be working for now...

"""
#EoF