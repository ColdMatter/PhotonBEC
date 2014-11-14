#ipython --pylab
#execfile("main.py")
from pylab import *
sys.path.append("D:\Control\PythonPackages")
from SingleChannelAO import *

#AC couple photodetector to amplifier
#Use function generator to switch AOM TTL. Measure function generator and amplifier output.
#DC couple both channels.
#Use PDA36 amplified detector without post-amp
Nruns = 1024
suggested_laser_power = 2200
timebase=1000e-9#500e-9. Changes...
comment_extra = "Rindown. Mirror spacing approx 59 mm"
parameter_extra = {"mirror spacing mm":59}
print "Set laser power to "+str(suggested_laser_power)+" mW"
exec(file("ringdown_measurement.py").read())


#photodetector_gain_settings_flag
#Analyse the data?

#EOF
