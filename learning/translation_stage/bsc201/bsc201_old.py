#Have played in Device manager, as it says on p54 of the operating manual. Port is COM8

import serial
import time
import struct
message_ID=0x0223
param1=0
param2=0
dest=0x21
dest=0x01
source=0x50
comport=8 #found in Device Manager
motor = serial.Serial(comport-1,baudrate=115200,timeout=3)
packed = struct.pack("HBBBB",message_ID,param1,param2,dest,source)
motor.close()

#according to the manual pg12, these are the only possible sources and destinations
srcdst = [0x01, 0x11] + [0x20 | i for i in range(1, 11)] + [0x50]

try:
	#Works only with source 0x50, but with any destination!
	for dest in srcdst:
		print source, dest
		packed = struct.pack("HBBBB",message_ID,param1,param2,dest,source)
		motor = serial.Serial(comport-1,baudrate=115200,timeout=3)
		motor.write(packed)
		motor.close()
		time.sleep(6)
		print "...done"
except Exception as e:
	print cp, dest, source
	raise e




#-----------------
#USB attempts
#-------------------
"""
import pylibftdi
serial_number = 40849478
dev = pylibftdi.Device(device_id=serial_number)
"""
#needs installation of libusb and libftdi
#Note that pyusb also needs libusb
#ADDED 16/6/2014 by RAN
#I think that I've got libusb working with a backend of libusb0
#The trick: don't install libusb. Copy the libusb_x86.dll file from the libusb download folder to the local folder and rename is as "libusb0.dll". 
#Running usb.core.find(find_all=True) doesn't find any USB devices, which is odd.
#See also http://www.pinguino.cc/download/doc/libusb-windows7.pdf
