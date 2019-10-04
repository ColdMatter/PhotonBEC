
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import pbec_experiment as pbece
import pbec_analysis as pbeca
from interferometer_utils import bin_image

from time import sleep

def cam_get_image(cam, max_attempts=5):
	im = None
	for i in range(max_attempts):
		im = cam.get_image()
		#im = cam.get_image_now() #software triggered
		if im != None:
			break
	return im


#
"""
cameraLabel="chameleon"
#cameraLabel="grasshopper_2d"
shutter = 2. #ms
gain=0 #dB
min_shutter, max_shutter = 2, 2000
min_gain, max_gain = 0, 24
interesting_colours = [0,1] #2 is blue, and we never care
binning = [2,2] #really has to be made more robust: should not break if non-factor of image size
	#binning really must not be [1,1] or else hot pixels will mess things up

max_iter = 16
max_acceptable, min_acceptable = 220, 100 #factor of slightly more than factor 2
shutter_factor = 2.0
gain_increment = 6.0 #6dB equivalent to factor 2.

#Set up the loop
count = 0
maxval = 0
c = pbece.getCameraByLabel(cameraLabel)
c.setup()

while (count<max_iter) & ((maxval < min_acceptable) or (maxval > max_acceptable)):
	count +=1
	print "setting shutter and gain to "+str((shutter,gain))
	c.set_property('shutter', shutter)
	c.set_property('gain', gain)
	im = cam_get_image(c)

	#Find if image is saturated, accounting for a couple of hot pixels
	subim = array([bin_image(im[:,:,i],binning) for i in interesting_colours])
	subim = subim.transpose((1,2,0))
	subim_maxloc = unravel_index(subim.argmax(), subim.shape)
	maxval= subim[subim_maxloc]

	print "maxval = "+str(maxval)+"\t Binned-image location "+str(subim_maxloc)
	#Logic: it's better to have long shutter than high gain, because that's the lowest noise option
	if maxval>max_acceptable:
		#first try reducing the gain
		gain = gain - gain_increment
		if gain < min_gain:
			gain = min_gain
			shutter = shutter / shutter_factor
			if shutter < min_shutter:
				shutter = min_shutter
				print "Can't go lower!"
				#TODO: should break here
	elif maxval<min_acceptable:
		#first try increasing the shutter
		shutter = shutter * shutter_factor
		if shutter > max_shutter:
			shutter = max_shutter			
			gain = gain + gain_increment
			if gain >= max_gain:
				gain = max_gain
				print "Can't go higher!"
				#TODO: should break here
	#
c.close()
"""

def get_single_autoexposed_image(cameraLabel, shutter=64., gain=0, min_shutter= 2, max_shutter=2000, \
	min_gain=0, max_gain=24, interesting_colours = [0,1], binning = [2,2], max_iter = 16, \
	min_acceptable_value = 100, max_acceptable_value=220, shutter_factor = 2.0, gain_increment = 6.0,\
	verbose = False):

	#Set up the loop
	count = 0
	maxval = 0
	c = pbece.getCameraByLabel(cameraLabel)
	c.setup()

	while (count<max_iter) & ((maxval < min_acceptable_value) or (maxval > max_acceptable_value)):
		count +=1
		if verbose: print "setting shutter and gain to "+str((shutter,gain))
		c.set_property('shutter', shutter)
		c.set_property('gain', gain)
		im = cam_get_image(c)

		#Find if image is saturated, accounting for a couple of hot pixels
		subim = array([bin_image(im[:,:,i],binning) for i in interesting_colours])
		subim = subim.transpose((1,2,0))
		subim_maxloc = unravel_index(subim.argmax(), subim.shape)
		maxval= subim[subim_maxloc]

		res = {"shutter": shutter, "gain": gain, "maxval": maxval, "Niter":count}
		if verbose: print "maxval = "+str(maxval)+"\t Binned-image location "+str(subim_maxloc)
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
					return im, res
		elif maxval<min_acceptable_value:
			#first try increasing the shutter
			shutter = shutter * shutter_factor
			if shutter > max_shutter:
				shutter = max_shutter			
				gain = gain + gain_increment
				if gain >= max_gain:
					gain = max_gain
					if verbose: print "Can't go higher!"
					return im, res
		#
	c.close()
	return im, res


#im, res = get_single_autoexposed_image("chameleon", shutter=64, gain=0, binning = [4,4])
#figure(1); clf(); imshow(im);colorbar()



#EoF