#ipython
#exec(open("SingleChannelAO.py").read())

#-----------------------
from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import *

def ErrorHandler(error_number):
	#Needs improving: out-of-range errors break everything.
	if error_number not in [0,None]:
		print "Error number "+str(error_number)+" encountered"

def SingleChannelAO(value,device="Dev1",channel="ao0",minval=0,maxval=5,timeout=1):
	analog_output = Task()
	ErrorHandler(\
		analog_output.CreateAOVoltageChan(\
			device+"/"+channel,device+"_"+channel,0,5.0,DAQmx_Val_Volts,None\
			))
	ErrorHandler(analog_output.WriteAnalogScalarF64(True,timeout,value,None))

#

def SetAO0(value):
	SingleChannelAO(value,device="Dev1",channel="ao0",minval=0,maxval=5,timeout=1)
	
def SetAO1(value):
	SingleChannelAO(value,device="Dev1",channel="ao1",minval=0,maxval=5,timeout=1)