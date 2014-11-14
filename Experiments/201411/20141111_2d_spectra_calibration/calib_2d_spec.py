import time
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("D:\Control\CavityLock")

from pbec_experiment import *
from pbec_analysis import *
from pbec_ipc import *
from random import shuffle,sample

cam_name="grasshopper"
saving=True
sleep_time=2 #pause before acquiring data after cavity lock point shifting

set_points = linspace(130,150,3)
spectrometer_exposure_ms = 10
spectrometer_averages =30
base_comment="Calibrating position-energy spectroscopy with 20 um slit"

def setCavityLockPoint(set_point,sleep_time=0.3):
	eval_str = "setSetPointGradual("+str(int(set_point))+", sleepTime= "+str(sleep_time)+")"
	#from pbec_ipc
	ipc_eval(eval_str) #call never returns when using setSetPointGradual!!!
	
	
#INSTRUCTIONS TO USER
#run cavity stabiliser: you'll have to manually set it working. 
#close both Grasshopper-FlyCap and AvaSoft applications

ex_list = []
rand_set_points = set_points#sample(set_points,len(set_points))

cam = getCameraByLabel(cam_name)

for sp in rand_set_points:
	print "Setting lock point to "+str(sp)+" ...",
	setCavityLockPoint(sp) #must be integer!!!
	print "set"
	time.sleep(sleep_time)
	print "Acquiring data...",
	#acquire one image from grasshopper and one spectrum
	ts= make_timestamp()
	print "cam...",
	im = get_single_image(cam_name)
	print "spectrometer...",
	lamb,spec = get_single_spectrum(spectrometer_exposure_ms,spectrometer_averages)
	print "done"
	#set up Experiment object.
	ex = pbec_analysis.Experiment(ts=ts)
	ex.setSpectrometerData(lamb,spec)
	ex.setCameraData(im)
	ex.meta.parameters={"lock_set_point":sp,"cam_name":cam_name}
	if saving: 
		print "Saving "+ts
		ex.saveAllData()
	ex_list.append(ex)	
		
#EoF