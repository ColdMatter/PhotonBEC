#ipython --pylab
#execfile("main.py")
from pylab import *
sys.path.append("D:\Control\PythonPackages")
from SingleChannelAO import *

Nruns = 64
laser_power= 70
nd_filter = 1
timebase=250e-9
micrometer_posn_mm = 3.0
parameter_extra = {"micrometer_posn_mm":micrometer_posn_mm}

comment_extra = "Ringdown. Cavity micrometer posn = "+str(micrometer_posn_mm)+"; Detector Analog Modules 712A-4 APD"
saving=False

#ACquisition and display parameters
Navg = 64
ch2_prefac=0.2 #for display only
background_flag = False
exec(file("ringdown_measurement.py").read())

#EOF
