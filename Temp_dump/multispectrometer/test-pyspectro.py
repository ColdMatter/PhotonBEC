#written by Jakov Marelic 6/2014, modified by LZ to pass dll directory to setupavs1

import numpy
import pyspectro

'''
doublearr = numpy.array([f / 10.0 for f in range(10)])
intarr = numpy.arange(10, dtype=numpy.uint8)
print(doublearr)
print(intarr)
pyspectro.helloworld(doublearr, intarr)
print(doublearr)
print(intarr)
'''

def getLambdaRange(lamb, fromL, toL):
	assert(fromL < toL)
	assert(fromL > lamb[0])
	assert(toL < lamb[-1])
	hi = 0 #this is a crap way of doing it but this function
	lo = 0 # isnt a bottleneck so the speed hit doesnt matter
	for i, v in enumerate(lamb):
		if v > fromL:
			lo = i
			break
	for i, v in enumerate(lamb):
		if v > toL:
			hi = i
			break
	return (hi, low)
	#return (
	#	int( (fromL - lamb[0]) * len(lamb) / (lamb[-1] - lamb[0]) ),
	#	int( (toL - lamb[0]) * len(lamb) / (lamb[-1] - lamb[0]) )
	#	)

dllDirectory = "D:\\Control\\spectrometer"
import socket
if socket.gethostname().lower()=="ph-photonbec2":
	dllDirectory="C:\\photonbec\\Control\\spectrometer"

#always put these in try: finally: because if closeavs() doesnt get called you
# will have to pull out and replace the spectrometer usb cable
#all these functions have error checking inside and will raise python exceptions
# in exceptions an error code might be displayed, read the source of avs-spectro.cpp to understand
try:
	#setupavs1() returns the number of pixels in the CCD array
	pixelNum = pyspectro.setupavs1(dllDirectory)
	print("pixelNum = " + str(pixelNum))

	#getlambda() gives an array which is a mapping between pixel number and wavelength
	# must get a numpy double array passed to it of length pixelNum
	lamb = numpy.array([0.1] * pixelNum)
	pyspectro.getlambda(lamb)
	
	#setupavs2(pixelRange, intTime, nAverages, nMeasure) gives the signal to start measuring
	# pixelRange - a two-tuple of start- and end-pixel which will be read
	#              it defines the length of the array you must pass to readavsspectrum()
	# intTime - integration time as a float in milliseconds
	# nAverages - number of averages
	# nMeasure - number of measurements after which no more data will be taken and
	#          readavsspectrum() will block if called, use -1 for infinite data taking
	pyspectro.setupavs2((0, pixelNum - 1), 30.0, 1, -1)
	spectrum = numpy.array([0.1] * pixelNum)
	for j in range(10):
		#readavsspectrum(spectrumArray, timeout)
		# blocks until data is available and then puts it in specturmArray
		# spectrumArray - a numpy double array of length (endPixel - startPixel) passed tosetupavs2()
		# timeout - a timeout in milliseconds, after which the function raises exception
		#           this is mostly as insurance in case you've called it more times than#
		#           nMeasure. set to a couple of second to prevent ugly killing of the app
		# returns: the timestamp is stored in timestamp by the spectrometer down to
		#          10 microsecond precision, read the manual for GetScopeData()
		timestamp = pyspectro.readavsspectrum(spectrum, 10000)
		for i in range(0, pixelNum, 128):
			print("spectrum[lambda = " + str(lamb[i]) + " ] = " + str(spectrum[i]))
		print(". " + str(j))
finally:
	print("called this hopefully")
	pyspectro.closeavs()
