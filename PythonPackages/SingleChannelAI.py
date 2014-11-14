#exit()

#ipython --pylab
#exec(open("calibrate_AOM_amplitude.py").read())
from numpy import zeros,mean
from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxTypes import *

def ErrorHandler(error_number):
	#Needs improving: out-of-range errors break everything.
	if error_number not in [0,None]:
		print "Error number "+str(error_number)+" encountered"


def SingleChannelAI(Npts=1000,rate=1.0e4,device="Dev1",channel="ai0",minval=-10.0,maxval=10.0):
	#Cannot read just a single point. Minimum 2.
	analog_input = Task()
	data = zeros((Npts,), dtype=float64)

	#DAQmx Configure Code
	devchan=device+"/"+channel
	ErrorHandler(\
		analog_input.CreateAIVoltageChan(\
		devchan,"",DAQmx_Val_Cfg_Default,minval,maxval,DAQmx_Val_Volts,None\
			))
	ErrorHandler(\
		analog_input.CfgSampClkTiming(\
		"",rate,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,Npts\
			))

	#DAQmx Start Code
	ErrorHandler(analog_input.StartTask())

	#DAQmx Read Code
	ErrorHandler(\
		analog_input.ReadAnalogF64(\
		1000,10.0,DAQmx_Val_GroupByChannel,data,1000,byref(int32()),None\
		))
	#Data is now in "data" array
	return data

def GetAI0(Npts=2,avg=True):
	data= SingleChannelAI(Npts=Npts,rate=1.0e4,device="Dev1",channel="ai0",minval=-10.0,maxval=10.0)
	if avg:
		return mean(data)
	else:
		return data

#EOF
