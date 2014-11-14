#ipython --gui=qt4
#>>>cavity_lock.setSetPoint(<value>)
#>>>cavity_lock.s.start_acquisition()
#>>>ring_rad = cavity_lock.s.ring_rad

import time
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("D:\Control\CavityLock")

from pbec_experiment import *
from random import shuffle,sample


set_point = int(raw_input("Type set point of cavity lock, then press Enter\n"))
q = int(raw_input("Type longitudinal mode number, q, then press Enter\n"))

#INSTRUCTIONS TO USER
#run cavity stabiliser: you'll have to manually set it working. 
#close both FlyCap and AvaSoft applications
#Uncheck the "poll power" box in the LaserController GUI
sleep_time_s = 25 #time to wait for laser power to stabilise. Depends on power range...
	#There are COM port control issues when LaserController GUI is running...
power_check_time = 3#in seconds
AOM_sleep_time = 1.5#in seconds. Time for AOM to response. Probably also time for the camera to clear its image
powers = range(1000,1401,30)

saving=True
take_images=True
save_memory = True #do not retain a list of all experiments. Useful when taking many images.
base_comment = "Power variation;"

AOM_on, AOM_off = 1.3,0 #re-calibrated on 31/7/14
spectrometer_exposure_ms = 100 #Should saturate at highest power. Just.
spectrometer_averages = 3
#
lq = LaserQuantum.LaserQuantum()
if take_images: c = getCameraByLabel("chameleon") #open camera at beginning: retain control throughout experiment

if not(save_memory): ex_list = []
#MAIN LOOP, IN A RANDOMISED ORDER

for p in sample(powers,len(powers)):
	lq.setPower(p)
	print "Setting laser power to "+str(p)+" mW"
	#At this point, poll lq for power, and print: check power stability
	for i in arange(0,sleep_time_s,power_check_time):
		time.sleep(power_check_time)
		measured_p = lq.getPower()
		#print "\t\t"+str(measured_p)+" mW"
		print (str(measured_p)+" mW..."),
	#
	if take_images: c.setup()
	for (AOM_V,extra_comment) in [(AOM_on,"signal"),(AOM_off,"background")]:
		#Set up the experiment as needed
		SingleChannelAO.SetAO0(AOM_V) #on voltage = 0.9
		print "Setting AOM...",
		time.sleep(AOM_sleep_time)
		print "AOM set...",
		ts = pbec_analysis.make_timestamp()
		print "\n"+"Taking data..."+ts
		if take_images: 
			im = c.get_image()
			#if c.error !=None:
			max_number_of_tries = 5
			count=0
			while (c.error != None) & (count < max_number_of_tries):
				count +=1
				print "Camera error: "+str(c.error)
				print "Trying again for the "+str(count)+"th time"
				im = c.get_image()
				#Alternative error handling: try again if error found.
		lamb,spec = get_single_spectrum(spectrometer_exposure_ms,spectrometer_averages)
		#Having taken the data, leave the experiment in a default state
		SingleChannelAO.SetAO0(AOM_V) #on voltage = 0.9
		#Now save the data
		ex = pbec_analysis.Experiment(ts=ts)
		ex.setSpectrometerData(lamb,spec)
		ex.meta.comments = base_comment + extra_comment
		ex.meta.parameters={"AOM_voltage":AOM_V,\
			"spectrometer_exposure_ms":spectrometer_exposure_ms,\
			"spectrometer_averages":spectrometer_averages,\
			"laser_power_mW":p,"set_point":set_point,"longitudinal_mode_number":q}
		if not(save_memory): ex_list.append(ex)
		if saving: 
			if take_images:
				ex.setCameraData(im)
				ex.meta.parameters.update({"camera_errors":str(c.error)})
				if c.error==None:
					ex.saveCameraData() #If an error occured, don't even try to save the data.
				else:
					c.error = None #reset
			ex.meta.save()
			ex.saveSpectrometerData()
			print "Saved... "+ex.ts + "\t"+extra_comment
		else:
			print "Unsaved... "+ex.ts + "\t"+extra_comment
	#
	if take_images: c.close()
	SingleChannelAO.SetAO0(AOM_on)
lq.ser.close()

#EoF
