#ipython --pylab
import time
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_experiment import *
from random import shuffle,sample


#INSTRUCTIONS TO USER
#run cavity stabiliser: you'll have to manually set it working. 
#close both FlyCap and AvaSoft applications
#Uncheck the "poll power" box in the LaserController GUI
sleep_time_s = 25 #time to wait for laser power to stabilise. Depends on power range...
	#There are COM port control issues when LaserController GUI is running...
power_check_time = 3#in seconds
powers = range(600,2201,100) #not too many points to avoid drifts.

saving=True
images=False
base_comment = "Power variation"

AOM_on, AOM_off = 1.3,0 #re-calibrated on 31/7/14
spectrometer_exposure_ms = 20 #Should saturate at highest power. Just.
spectrometer_averages = 10
#
lq = LaserQuantum.LaserQuantum()
if images: c = getCameraByLabel("chameleon") #open camera at beginning: retain control throughout experiment

ex_list = []
#MAIN LOOP, IN A RANDOMISED ORDER
for p in sample(powers,len(powers)):
	lq.setPower(p)
	print "Setting laser power to "+str(p)+" mW"
	#At this point, poll lq for power, and print: check power stability
	for i in range(0,sleep_time_s,power_check_time):
		time.sleep(power_check_time)
		measured_p = lq.getPower()
		#print "\t\t"+str(measured_p)+" mW"
		print (str(measured_p)+" mW..."),
	#
	if images: c.setup()
	for (AOM_V,extra_comment) in [(AOM_on,"signal"),(AOM_off,"background")]:
		SingleChannelAO.SetAO0(AOM_V) #on voltage = 0.9
		ts = pbec_analysis.make_timestamp()
		print "\n"+"Taking data..."+ts
		if images: im = c.get_image()
		lamb,spec = get_single_spectrum(spectrometer_exposure_ms,spectrometer_averages)
		ex = pbec_analysis.Experiment(ts=ts)
		if images: ex.setCameraData(im)
		ex.setSpectrometerData(lamb,spec)
		ex.meta.comments = base_comment + extra_comment
		ex.meta.parameters={"AOM_voltage":AOM_V,\
			"spectrometer_exposure_ms":spectrometer_exposure_ms,\
			"spectrometer_averages":spectrometer_averages,\
			"laser_power_mW":p}
		ex_list.append(ex)
		if saving: 
			ex.meta.save()
			ex.saveSpectrometerData()
			if images: ex.saveCameraData()
			print "Saved... "+ex.ts + "\t"+extra_comment
		else:
			print "Unsaved... "+ex.ts + "\t"+extra_comment
	#
	if images: c.close()
	SingleChannelAO.SetAO0(AOM_on)
lq.ser.close()

#EoF
