
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import pbec_experiment as pbece
import pbec_analysis as pbeca
from interferometer_utils import bin_image
from numpy import array, unravel_index

from time import sleep

def cam_get_image(cam, max_attempts=5, verbose=False):
	im = None
	extra_wait = 0.05 #arbitrarily chosen
	shutter = 1e-3*cam.get_all_properties()["shutter"]["absValue"]
	if verbose: print (shutter_extra_wait)
	for i in range(max_attempts):
		if verbose: 
			print "cam_get_image: attempt #"+str(i+1)+"...",
		#im = cam.get_image_now(verbose=verbose) #software triggered
		sleep(2*shutter + extra_wait) #manually added wait to be used with un-triggered acquisition
		im = cam.get_image(verbose=verbose) #untriggered
		if im != None:
			break
	return im

def get_single_autoexposed_image(cameraLabel, shutter=64., gain=0, min_shutter= 2, max_shutter=2000, \
	min_gain=0, max_gain=24., interesting_colours = [0,1], binning = [4,4], max_iter = 14, \
	min_acceptable_value = 100, max_acceptable_value=220, shutter_factor = 2.0, gain_increment = 6.0,\
	verbose = False):
	"""
	To use this, first turn all "auto" settings on the camera OFF, and also turn 'frame rate' OFF
	except for the Grasshopper cameras, which have an intermittent bug, so leave the 'frame rate' ON
	if you're experiencing problems
	"""

	#Set up the loop
	count = 0
	maxval = 0
	c = pbece.getCameraByLabel(cameraLabel)
	c.setup()
	while (count<max_iter) & ((maxval < min_acceptable_value) or (maxval > max_acceptable_value)):
		count +=1
		if verbose: 
			print "setting shutter and gain to "+str((shutter,gain)),
		c.set_property('shutter', shutter)
		c.set_property('gain', gain)
		dump = c.get_image() #clear the camera sensor
		im = cam_get_image(c)

		#Find if image is saturated, accounting for a couple of hot pixels
		subim = array([bin_image(im[:,:,i],binning) for i in interesting_colours])
		subim = subim.transpose((1,2,0))
		subim_maxloc = unravel_index(subim.argmax(), subim.shape)
		maxval= subim[subim_maxloc]

		res = {"shutter": shutter, "gain": gain, "maxval": maxval, "Niter":count}
		if verbose: print "maxval = "+str(maxval)#+"\t Binned-image location "+str(subim_maxloc)
		#Logic: it's better to have long shutter than high gain, because that's the lowest noise option
		if maxval>max_acceptable_value:
			#first try reducing the gain
			gain = gain - gain_increment
			if gain < min_gain:
				gain = min_gain
				shutter = shutter / shutter_factor
				if shutter < min_shutter:
					shutter = min_shutter
					if verbose: print "Can't go lower!"
					break
		elif maxval<min_acceptable_value:
			#first try increasing the shutter
			shutter = shutter * shutter_factor
			if shutter > max_shutter:
				shutter = max_shutter			
				gain = gain + gain_increment
				if gain > max_gain:
					gain = max_gain
					if verbose: print "Can't go higher!"
					break
		#
	c.close()
	return im, res

if __name__=="__main__":
	#im, res = get_single_autoexposed_image("chameleon", shutter=2, gain=24, binning = [4,4], verbose=True)
	im, res = get_single_autoexposed_image("grasshopper_2d", shutter=64, gain=0, binning = [4,4], verbose = True)
	figure(1); clf(); imshow(im)



#EoF