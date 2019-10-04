
import sys
#sys.path.append("Y:\\Control\\PythonPackages\\")
sys.path.append("D:\\Control\\PythonPackages\\")

import time

import pbec_analysis
import pbec_experiment
import ThorlabsMDT69xA
import hene_utils

#centery and slit_halfheight dont matter
cam_label = "flea"
volts_startstopstep = (60, 70, 0.1) #goes into arange()
sleeptime = 0.1

def cam_get_image(cam, max_attempts=5):
	im = None
	for i in range(max_attempts):
		im = cam.get_image()
		if im != None:
			break
	return im

volts = []
images = []

ts = pbec_analysis.make_timestamp()
experiment = pbec_analysis.ExperimentalDataSet(ts=ts)
experiment.meta.parameters['volts_startstopstep'] = volts_startstopstep
experiment.meta.parameters['image_count'] = len(arange(*volts_startstopstep))

pzt_class = ThorlabsMDT69xA.ThorlabsMDT69xA(1)
cam = pbec_experiment.getCameraByLabel(cam_label)
try:
	for i, v in enumerate(arange(*volts_startstopstep)):
		pzt_class.setXvolts(v)
		print 'setting to ' + str(v) + 'V'
		time.sleep(sleeptime)
		im = cam_get_image(cam)
		if im == None:
			print 'image null!'
		volts.append(v)
		images.append(im.copy())

		
finally:
	cam.close()

experiment.dataset['imagelist'] = pbec_analysis.InterferometerFringeData(experiment.ts, '_imagelist.zip')
experiment.dataset['imagelist'].setData(images)
experiment.meta.parameters['volts'] = volts
print 'saving to ' + ts
experiment.saveAllData()