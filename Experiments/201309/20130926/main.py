#ipython --pylab
#execfile("main.py")
from pylab import *
sys.path.append("D:\Control\PythonPackages")
from SingleChannelAO import *

apd_characterisation_flag = False
ringdown_flag = True

if apd_characterisation_flag:
	Nruns = 4
	laser_power= 1
	nd_filter = 1000
	timebase=250e-9 #100e-9
	pulse_duration_ns = 1000 #10
	parameters_extra = {"pulse duration ns":pulse_duration_ns}
	comment_extra = "Analog Modules 712A-4 APD characterisation"
	saving=False
	exec(file("apd_characterisation.py").read())

#--------------------------
#RINGDOWN MEASUREMENT WITH APD
if ringdown_flag: 
	Nruns = 512
	laser_power= 1#2200
	nd_filter = 1
	timebase=100e-9
	pulse_duration_ns = 1000
	mirror_spacing_mm = "Second mirror"
	parameter_extra = {"pulse duration ns":pulse_duration_ns, "mirror spacing mm":mirror_spacing_mm}

	comment_extra = "Ringdown. Cavity length = "+str(mirror_spacing_mm)+"; Detector Analog Modules 712A-4 APD"
	saving=True
	exec(file("ringdown_measurement.py").read())

#EOF
