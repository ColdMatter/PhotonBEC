#written by Jakov Marelic 6/2014 and modified by LZ to pass dll location to setupflycap

import pyflycap
import numpy
from scipy.misc import imsave
import sys, pprint, threading, time


CHAMELEON = 15299245
FLEA = 14080462
GRASSHOPPER = 14110879
GRASSHOPPER_2 = 14435619
MINISETUP_CHAMELEON = 12350594
serialNumbers = {"chameleon": CHAMELEON, "flea": FLEA, "grasshopper": GRASSHOPPER, "grasshopper2": GRASSHOPPER_2, "minisetup_chameleon": MINISETUP_CHAMELEON}

#dllLocation = "D:\\Control\\camera"
dllLocation = "C:\photonbec\Control\camera" #Altered by Walker
serialNumber = 0 #any camera
if len(sys.argv) > 1:
	serialNumber = serialNumbers[sys.argv[1].lower()]

PROPERTY_TYPE_MAPPING = {"brightness": 0, "auto_exposure": 1, "sharpness": 2, "white_balance": 3,
	"hue": 4, "saturation": 5, "gamma": 6, "iris": 7, "focus": 8, "zoom": 9, "pan": 10, "tilt": 11,
	"shutter": 12, "gain": 13, "trigger_mode": 14, "trigger_delay": 15, "frame_rate": 16, "temperature": 17}
	
format7_info_struct_names = ("maxWidth", "maxHeight", "offsetHStepSize", "offsetVStepSize",
	"imageHStepSize", "imageVStepSize", "packetSize", "minPacketSize", "maxPacketSize")
format7_conf_struct_names = ("offsetX", "offsetY", "width", "height", "pixelFormat")

#always use these in try: finally: because the python extention function
# check for errors and raise exceptions, and its good to close stuff still
handle = -1
try:
	meta = pyflycap.setupflycap(serialNumber, dllLocation)
	print("setup flycap\nmeta=" + str(meta))
	handle = meta[0]
	data = None
	
	test = 0
	if test == 0:
		prop = pyflycap.getproperty(handle, PROPERTY_TYPE_MAPPING["shutter"])
		print("shutter property = " + str(prop))
		for name, type in PROPERTY_TYPE_MAPPING.iteritems():
			info = pyflycap.getpropertyinfo(handle, type)
			print("\t" + name + " " + str(info))
			
		format7info = pyflycap.getformat7info(handle)
		print("format7 info = " + pprint.pformat(zip(format7_info_struct_names, format7info)))
		format7config = pyflycap.getformat7config(handle)
		print("format7 conf = " + pprint.pformat(zip(format7_conf_struct_names, format7config)))
		format7config[2] = 320
		format7config[3] = 400

		for i in range(3):
			pyflycap.setproperty(handle, prop)
			
			format7config[0] = (i + 1)*32
			format7config[1] = (i + 1)*64
			pyflycap.setformat7config(handle, format7config)
		
			dataTuple = pyflycap.getflycapimage(handle)
			(dataLen, row, col, bitsPerPixel) = dataTuple
			
			if data == None:
				data = numpy.arange(dataLen, dtype=numpy.uint8)
				print("dataLen, row, col, BPP = " + str(dataTuple))
			pyflycap.getflycapdata(handle, data)
			'''
			print("printing out the first 10 pixels i=" + str(i))
			bytesPerPixel = bitsPerPixel / 8
			for p in range(10):
				line = "pixel[%d] " % p
				for b in range(bytesPerPixel):
					line += "% 2d" % data[p*bytesPerPixel + b]
				print(line)
			'''	
			print("saving")
			im = numpy.reshape(data,(row,col,3)) 
			imsave("image-" + str(i) + ".png", im)
	elif test == 1:
		software = True
		print 'setting trigger mode true, handle' + str(handle)
		pyflycap.settriggermode(handle, True, software)
		print 'waiting for availability'
		pyflycap.waitfortriggerready(handle)
		print 'woken'
		if software:
			print 'firing software trigger'
			pyflycap.firesoftwaretrigger(handle)
		print 'attempting to get image'
		dataTuple = pyflycap.getflycapimage(handle)
		print 'got image'
		(dataLen, row, col, bitsPerPixel) = dataTuple
		if data == None:
			data = numpy.arange(dataLen, dtype=numpy.uint8)
			print("dataLen, row, col, BPP = " + str(dataTuple))
		pyflycap.getflycapdata(handle, data)
		print("saving")
		im = numpy.reshape(data,(row,col,3)) 
		imsave("trigger-im.png", im)
		
		print 'setting trigger back to normal'
		pyflycap.settriggermode(handle, False, software)

finally:
	print("closing everything")
	if handle != -1:
		pyflycap.closeflycap(handle)
	pyflycap.freelibrary()
