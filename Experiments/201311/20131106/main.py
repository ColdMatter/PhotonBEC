#ipython --pylab
#execfile("main.py")
from pylab import *
sys.path.append("D:\Control\PythonPackages")
from SingleChannelAO import *

Nruns = 15
nd_filter = 1
timebase=250e-9
micrometer_posn_mm = 9.0
parameter_extra = {"micrometer_posn_mm":micrometer_posn_mm}

comment_extra = "Ringdown. Cavity micrometer posn = "+str(micrometer_posn_mm)+"; Detector Analog Modules 712A-4 APD; RoC 0.25 m and planar (fully assembled)"
saving=True

#ACquisition and display parameters
Navg = 64
ch2_prefac=0.2 #for display only
background_flag = False
exec(file("ringdown_measurement.py").read())

#EOF
