#ipython --pylab
#execfile("main.py")
from pylab import *
amplifier_test_flag = False
amplifier_pulse_flag = True
unamplified_photodetector_flag = False
photodetector_gain_settings_flag = False

#Accumulate data
if amplifier_test_flag:
	for suggested_amplitude in [1,3,10]:
		print " SET INPUT AMPLITUDE TO "+str(suggested_amplitude)+" mV"
		comment_extra = "amplifier test"
		exec(file("amplifier_characterisation.py").read())

if amplifier_pulse_flag:
	for suggested_duration in [20,200,500,1000]:
		print " SET PULSE DURATION TO "+str(suggested_duration)+" ns"
		comment_extra = "amplifier pulse test"
		exec(file("amplifier_pulse_characterisation.py").read())

#








if unamplified_photodetector_flag:
	for laser_power in [1,3,10,30,100]:
		print " SET LASER POWER TO "+str(laser_power)+" mW"
		comment_extra = "unamplified photodetector"
		exec(file("amplifier_characterisation.py").read())

#photodetector_gain_settings_flag
#Analyse the data?

#EOF
