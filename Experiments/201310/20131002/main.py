#ipython --pylab
#execfile("main.py")
from pylab import *
sys.path.append("D:\Control\PythonPackages")
from SingleChannelAO import *

Nruns = 64
laser_power= 1000#2200
nd_filter = 1
timebase=100e-9
mirror_spacing_mm = 1.5
parameter_extra = {"mirror spacing mm":mirror_spacing_mm}

comment_extra = "Ringdown. Cavity length = "+str(mirror_spacing_mm)+"; Detector Analog Modules 712A-4 APD"
saving=True
exec(file("ringdown_measurement.py").read())

#EOF
