#ipython --pylab
#execfile("thermal_spot_size_vs_lam0.py")

import time
import sys
import os
sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("D:\Control\CavityLock")

from pbec_experiment import *
from random import shuffle,sample

#set_points = [145,155,165]
set_points = range(100,181,8)

#INSTRUCTIONS TO USER
#run cavity stabiliser: you'll have to manually set it working. 
#close both FlyCap and AvaSoft applications


saving=True
take_images=True
save_memory = True #do not retain a list of all experiments. Useful when taking many images.
base_comment = "Thermal spot size and spectrum; "

spectrometer_exposure_ms = 500
spectrometer_averages = 1
AOM_sleep_time = 1.5
AOM_on,AOM_off = 0.9,0

if take_images: c = getCameraByLabel("chameleon") #open camera at beginning: retain control throughout experiment

if not(save_memory): ex_list = []

if take_images: c.setup()

q = int(raw_input("Type longitudinal mode number, q, then press Return\n"))
spot_size_ts = int(raw_input("Type timestamp of image of pump spot size, then press Return\n"))
concn_uM = int(raw_input("Type concentration in micro-Moles/litre, then press Return\n"))
lq_power_mW = int(raw_input("Type pump power in mW, then press Return\n"))

#MAIN EXPERIMENTAL LOOP, IN A RANDOMISED ORDER
for sp in sample(set_points,len(set_points)):
	#Copy the required set point to the clipboard
	os.system("echo " + str(sp) + "| clip")
	print "\n"
	raw_input("Set the cavity lock set point to "+str(sp)+" and then press Return")
	#
	#-----TAKE DATA-----------
	for (AOM_V,extra_comment) in [(AOM_on,"signal"),(AOM_off,"background")]:
		ts = pbec_analysis.make_timestamp()
		#Set up the experiment as needed
		SingleChannelAO.SetAO0(AOM_V) #on voltage = 0.9
		print "Setting AOM...",
		time.sleep(AOM_sleep_time)
		print "AOM set...",

		print "\n"+"Taking data..."+ts,
		if take_images: 
			im = c.get_image()
			#if c.error !=None:
			max_number_of_tries = 5
			count=0
			#Alternative error handling: try again if error found.
			while (c.error != None) & (count < max_number_of_tries):
				count +=1
				print "Camera error: "+str(c.error)
				print "Trying again for the "+str(count)+"th time"
				im = c.get_image()
		lamb,spec = get_single_spectrum(spectrometer_exposure_ms,spectrometer_averages)
		#
		#-----SAVE DATA IF NEED BE-----------
		ex = pbec_analysis.Experiment(ts=ts)
		ex.setSpectrometerData(lamb,spec)
		ex.meta.comments = base_comment
		ex.meta.parameters={"spectrometer_exposure_ms":spectrometer_exposure_ms,\
			"AOM_voltage":AOM_V,\
			"spectrometer_averages":spectrometer_averages,\
			"set_point":sp,"longitudinal_mode_number":q,\
			"spot_size_ts":spot_size_ts, "concn_uM":concn_uM,\
			"lq_power_mW":lq_power_mW}
		if not(save_memory): ex_list.append(ex)
		if take_images:
			ex.setCameraData(im)
			ex.meta.parameters.update({"camera_errors":str(c.error)})
		if saving: 
			if take_images:
				if c.error==None:
					ex.saveCameraData() #If an error persistsed, don't even try to save the data.
				else:
					c.error = None #reset
			ex.meta.save()
			ex.saveSpectrometerData()
			print "...saved... "+"\t"+extra_comment
		else:
			print "...unsaved... "+"\t"+extra_comment
	#
if take_images: c.close()
SingleChannelAO.SetAO0(AOM_on)

#execfile("thermal_spot_size_vs_lam0.py")
#EoF
