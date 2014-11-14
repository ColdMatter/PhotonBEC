#ipython --pylab
#execfile("main.py")
from pylab import *
sys.path.append("D:\Control\PythonPackages")
from SingleChannelAO import *

amplifier_test_flag = False
amplifier_pulse_flag = False
photodetector_gain_settings_flag = False
amplified_photodetector_flag = True

#Accumulate data
if amplifier_test_flag:
	#Connect function generator to amplifier input. Measure function generator signal and amplifier output. AC couple both channels
	for suggested_amplitude in [1,3,5]:
		print " SET INPUT AMPLITUDE TO "+str(suggested_amplitude)+" mV"
		comment_extra = "amplifier test"
		exec(file("amplifier_characterisation.py").read())

if amplifier_pulse_flag:
	#Connect function generator to amplifier input. Measure function generator signal and amplifier output. AC couple both channels
	for suggested_duration in [20,200,500,1000]:
		print " SET PULSE DURATION TO "+str(suggested_duration)+" ns"
		comment_extra = "amplifier pulse test"
		exec(file("amplifier_pulse_characterisation.py").read())

#-----------------
if photodetector_gain_settings_flag:
	#Shine laser onto detector. Set laser_power=1 mW
	#Use function generator to switch AOM TTL. Measure function generator and photodetector.
	#DC couple both channels
	#Use PDA36 amplified detector without post-amp
	Nruns = 8
	for suggested_PDgain_dB in range(0,41,10):
		comment_extra = "unamplified photodetector"
		exec(file("photodetector_characterisation.py").read())

if amplified_photodetector_flag:
	#Shine laser onto detector. Set laser_power=1 mW
	#AC couple photodetector to amplifier
	#Use function generator to switch AOM TTL. Measure function generator and amplifier output.
	#DC couple both channels.
	#Use PDA36 amplified detector without post-amp
	Nruns = 128
	for suggested_PDgain_dB in range(40,41,10):
		comment_extra = "amplified ac-coupled photodetector"
		if suggested_PDgain_dB ==40:
			print "-------Block beam, equivalent to 0 mW laser power for bkgd measurement"
		exec(file("photodetector_characterisation.py").read())


#photodetector_gain_settings_flag
#Analyse the data?

#EOF
