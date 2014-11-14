import pyflycapture
from pbec_analysis import *
from scipy.misc import imsave

def grab_image(ts = None,name_extra="",numberOfColours=3):
	"""
	numberofColours is 3 for RGB, 1 for Black and white
	if ts is None, don't save, otherwise save in appropriate location
	"""
	dataLen, row, col, bitsPerPixel = pyflycapture.acquirecameraimage()
	im_flat = [0]*dataLen
	for i in range(dataLen):
		im_flat[i] = pyflycapture.getnextbyte()
	#pyflycapture.freeimage()
	#numberOfColours is always 3, no matter what you ask for.
	#TODO autodetect if the image is negative
	#im = 1-reshape(im_flat,(row,col,3))  #note: for some reason, we receive the negative image sometimes
	im = reshape(im_flat,(row,col,3))  #note: for some reason, we receive the negative image sometimes
	if ts!=None:
		extension=".png"
		fname = timestamp_to_filename(ts,file_end=name_extra+extension,make_folder=True)
		imsave(fname,im)
	return im


#EoF
