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
sleep_time_s = 40 #time to wait for laser power to stabilise. Depends on power range...
	#There are COM port control issues when LaserController GUI is running...
power_check_time = 3#in seconds
ex_list = []

saving=True
base_comment = "Power variation; "
colour_weights=(1,1,0,0) #4-channel images

AOM_on, AOM_off = 0.9,0
spectrometer_exposure_ms = 1000
powers = [1,5,15] #mW, nominal laser power values
#
lq = LaserQuantum.LaserQuantum()
c = getCameraByLabel("chameleon") #open camera at beginning: retain control throughout experiment
c.setup()

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
	for (AOM_V,extra_comment) in [(AOM_on,"signal"),(AOM_off,"background")]:
		SingleChannelAO.SetAO0(AOM_V) #on voltage = 0.9
		ts = pbec_analysis.make_timestamp()
		print "Taking data..."+ts
		#res = get_single_image_and_spectrum("chameleon", spectrometer_exposure_ms)
		im = c.get_image()
		lamb,spec = get_single_spectrum(spectrometer_exposure_ms)
		ex = pbec_analysis.Experiment(ts=ts)
		ex.setCameraData(im)
		ex.setSpectrometerData(lamb,spec)
		ex.meta.comments = base_comment + extra_comment
		ex.meta.parameters={"AOM_voltage":AOM_V,\
			"spectrometer_exposure_ms":spectrometer_exposure_ms,\
			"laser_power_mW":p}
		ex_list.append(ex)
		if saving: 
			ex.saveAllData()
			print "Saved... "+ex.ts + "\t"+extra_comment
		else:
			print "Unsaved"+ex.ts + "\t"+extra_comment
	SingleChannelAO.SetAO0(AOM_on)
c.close()
lq.ser.close()

#EoF
