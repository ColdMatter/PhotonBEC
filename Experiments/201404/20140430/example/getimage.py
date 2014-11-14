import pyflycapture


print("acquiring image from the camera")
ret = pyflycapture.acquirecameraimage()
dataLen, row, col, bitsPerPixel = ret


print("passing over image data into python")
im = [0]*dataLen
for i in range(dataLen):
	im[i] = pyflycapture.getnextbyte()

#freeing memory allocated inside pyflycapture
pyflycapture.freeimage()

print("datalen=%d row=%d col=%d bpp=%d" % ret)
'''
print("printing out the first 10 pixels")
bytesPerPixel = bitsPerPixel / 8
for p in range(10):
	l = "pixel[%d]" % p
	for b in range(bytesPerPixel):
		l += " %2d" % im[p*bytesPerPixel + b]
	print(l)
'''

#the camera pixels are laid out line by line from left to right going from up to down
# i.e. the same way westerners read text

print("outputting image to PPM format (GIMP can open it)")
fd = open("camera.ppm", "w")
fd.write("P3\n" + str(col) + " " + str(row) + "\n255\n")

line = ""
for p in range(dataLen):
	line += str(im[p]) + " "
	if len(line) >= 70:
		line += "\n"
		fd.write(line)
		line = ""
fd.close()


print("cleaning up")
#free FlyCapture2Test.dll
pyflycapture.freelibrary()