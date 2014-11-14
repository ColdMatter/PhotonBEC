#ipython
#exec(open("testing_PyDAQmx.py").read())
import numpy

from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxTypes import *

analog_input = Task()
read = int32()
data = numpy.zeros((1000,), dtype=numpy.float64)

#DAQmx Configure Code
analog_input.CreateAIVoltageChan("Dev1/ai0","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,None)
analog_input.CfgSampClkTiming("",10000.0,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,1000)

#DAQmx Start Code
analog_input.StartTask()

#DAQmx Read Code
analog_input.ReadAnalogF64(1000,10.0,DAQmx_Val_GroupByChannel,data,1000,byref(read),None)

print "Acquired %d points\n"%read.value
clf()
plot(data)
show()

#-----------------------
from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import *

analog_output = Task()
err = analog_output.CreateAOVoltageChan("Dev1/ao0","Dev1_ao0",0,5.0,DAQmx_Val_Volts,None)
timeout=1#seconds
value=2.567
err = analog_output.WriteAnalogScalarF64(True,timeout,value,None)
analog_input.StartTask()
