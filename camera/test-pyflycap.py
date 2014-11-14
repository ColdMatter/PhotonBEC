#written by Jakov Marelic 6/2014 and modified by LZ to pass dll location to setupflycap

import pyflycap
import numpy
from scipy.misc import imsave
import sys


CHAMELEON = 12350594
FLEA = 14080462
GRASSHOPPER = 14110879
serialNumbers = {"chameleon": CHAMELEON, "flea": FLEA, "grasshopper": GRASSHOPPER}

dllLocation = "D:\\Control\\camera"
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
try:
	meta = pyflycap.setupflycap(serialNumber, dllLocation)
	print("setup flycap\nmeta=" + str(meta))
	data = None
	
	prop = pyflycap.getproperty(PROPERTY_TYPE_MAPPING["shutter"])
	print("shutter property = " + str(prop))
	for name, type in PROPERTY_TYPE_MAPPING.iteritems():
		info = pyflycap.getpropertyinfo(type)
		print("\t" + name + " " + str(info))
	
	print("format7 info = " + str(zip(format7_info_struct_names, pyflycap.getformat7info())))
	format7config = pyflycap.getformat7config()
	print("format7 conf = " + str(zip(format7_conf_struct_names, format7config)))
	format7config[2] = 320
	format7config[3] = 400

	for i in range(3):
		pyflycap.setproperty(prop)
		
		format7config[0] = (i + 1)*50
		format7config[1] = (i + 1)*80
		pyflycap.setformat7config(format7config)
	
		dataTuple = pyflycap.getflycapimage()
		(dataLen, row, col, bitsPerPixel) = dataTuple
		
		if data == None:
			data = numpy.arange(dataLen, dtype=numpy.uint8)
			print("dataLen, row, col, BPP = " + str(dataTuple))
		pyflycap.getflycapdata(data)
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

finally:
	print("closing everything")
	pyflycap.closeflycap()
	pyflycap.freelibrary()
