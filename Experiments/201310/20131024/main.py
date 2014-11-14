#ipython --pylab
#execfile("main.py")
from pylab import *
sys.path.append("D:\Control\PythonPackages")
from SingleChannelAO import *

Nruns = 128
laser_power= 1500#2200
nd_filter = 1
timebase=100e-9
mirror_spacing_mm = "2.2 mm, approx"
parameter_extra = {"mirror spacing mm":mirror_spacing_mm}

comment_extra = "Ringdown. Cavity length = "+str(mirror_spacing_mm)+"; Detector Analog Modules 712A-4 APD"
saving=True

#ACquisition and display parameters
Navg = 128
ch2_prefac=0.2 #for display only
background_flag = False
exec(file("ringdown_measurement.py").read())

#EOF
