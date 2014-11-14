#execfile("bsc201.py")
#Have played in Device manager, as it says on p54 of the operating manual. Port is COM8

import serial
import time
import struct
from thorlabs_apt_messages import *
import thorlabs_apt_messages #yes, I know, there's a hack going on
#message_ID=0x0223
#param1=0
#param2=0
#dest=0x01
#source=0x50
#comport=8 #found in Device Manager
#motor = serial.Serial(comport-1,baudrate=115200,timeout=3)
#packed = struct.pack("HBBBB",message_ID,param1,param2,dest,source)
#motor.close()

#Motor calibration for DRV014
#encoder_unit_position = 25600 * 1e3 #converts steps to metres NOT mm
#encoder_unit_velocity= 25600 * 1e3 #converts steps to metres NOT mm
#encoder_unit_acceleration= 25600 * 1e3 #converts steps to metres NOT mm
encoder_unit_position = 409600*1e3 #converts steps to metres NOT mm
encoder_unit_velocity= 21987328*1e3 #converts steps to metres/s NOT mm/s
encoder_unit_acceleration= 4506*1e3 #converts steps to metres/s/s NOT mm/s/s



header_length=6 #length of header in bytes

def lookup_message(message_number):
    return thorlabs_apt_messages.__inverse_messages[message_number] #defined in thorlabs_apt_messages

class NoDataHeader():
	#Message header format for messages with no packet data
	def __init__(self,message_ID = "",param1=0,param2=0,dest=0x50,source=0x01):
                #destination 0x50 is Generic USB hardware unit (aka the BSC201)
                #source 0x01 is the PC (aka Host controller)
                self.message_ID = message_ID
                self.param1=param1		
                self.param2=param2
                self.dest=dest
                self.source=source
                self.message_format = "HBBBB" #Note: H means 2 bytes, B means 1 byte
	def packedHeader(self):
		return struct.pack(self.message_format,self.message_ID,self.param1,self.param2,self.dest,self.source)
	def unpackHeader(self,header):
		#Header is a string, as received from serial port
		header = struct.unpack(self.message_format,header) 
		self.message_ID,self.param1,self.param2,self.dest,self.source=header
	def dict(self):
		return {"message_ID":self.message_ID,"param1":self.param1,"param2":self.param2,"dest": self.dest,"source":self.source}
	def printMe(self):
            d = self.dict()
            print "Message: "+lookup_message(d["message_ID"])
            for k in ["param1","param2","dest","source"]:
                print k+"\t"+str(d[k])
		#Fix this to be more readable

class WithDataHeader():
	#Message header format for messages with packet data, and the data too
	#Message header format for messages with no packet data
	def __init__(self,message_ID = "",packet_length=0,dest=0x50,source=0x01):
                #destination 0x50 is Generic USB hardware unit (aka the BSC201)
                #source 0x01 is the PC (aka Host controller)
                self.message_ID = message_ID
                self.packet_length = packet_length
                self.dest=dest
                self.source=source
                self.message_format = "HHBB"
	def packedHeader(self):	       
	        logicked_dest = self.dest | 0x80 #Don't ask me why. Could use bitwise_or(). Ask Thorlabs
                return struct.pack(self.message_format,self.message_ID,self.packet_length,logicked_dest,self.source)
	def unpackHeader(self,header):
		#Header is a string, as received from serial port
		header = struct.unpack(self.message_format,header) 
		self.message_ID,self.packet_length,self.dest,self.source=header
	def dict(self):
		return {"message_ID":self.message_ID,"packet_length":self.packet_length,"dest": self.dest,"source":self.source}
	def printMe(self):
	       d = self.dict()
	       print "Message: "+lookup_message(d["message_ID"])
	       for k in ["packet_length","dest","source"]:
	           print k+"\t"+str(d[k])
		#Fix this to be more readable



class BSC201(channel_ident=1):
	def __init__(self,comport=8):
		self.ser = serial.Serial(comport-1,baudrate=115200,timeout=3)
		self.ser.close()
		self.channel_ident=channel_ident
	def sendBasicCommand(self,message):
		self.ser.open()
		self.ser.write(NoDataHeader(message).packedHeader())
		self.ser.close()
	def flashFrontPanel(self):
		self.sendBasicCommand(MGMSG_MOD_IDENTIFY) #flashes front panel LEDs
	def goHome(self):
            ndh = NoDataHeader(MGMSG_MOT_MOVE_HOME,param1=chan_ident)
            self.ser.open()
            self.ser.write(ndh.packedHeader()) #request home parameters
            homed_header = bsc.ser.read(header_length)
            self.ser.close()
            ndh_homed = NoDataHeader()
            ndh_homed.unpackHeader(homed_header)
            print lookup_message(ndh_homed.message_ID)
	    

bsc = BSC201()
bsc.flashFrontPanel() #check that communication is working

"""
bsc.ser.open()
#Send _REQ_uest, and the controller respont with _GET_
bsc.ser.write(NoDataHeader(MGMSG_MOT_REQ_HOMEPARAMS).packedHeader()) #request home parameters
packet_length=14
header = bsc.ser.read(header_length)
data = bsc.ser.read(packet_length)
bsc.ser.close()

wdh = WithDataHeader()
wdh.unpackHeader(header)
wdh.printMe()

data #why is data full of zeroes?
"""

"""
#Set move position
dest,source = 0x50|0x80, 0x1
packet_length=6 #6 bytes for move data
wdh = WithDataHeader(MGMSG_MOT_SET_MOVEABSPARAMS, packet_length,dest,source)
header = wdh.packedHeader()
format="HL" #word followed by long. All unsigned
chan_ident = 1
posn = int(25e-3 * encoder_unit)#in encoder units
data = struct.pack(format,chan_ident,posn)

bsc.ser.open()
bsc.ser.write(header) #request home parameters
bsc.ser.read(data) #request home parameters
bsc.ser.close()
"""
#Set move velocity

#Set move acceleration

#Start move!

#--------------------------------
#GO TO HOME
#--------------------------------
packet_length=14 #6 bytes for home data
chan_ident=1
ndh = NoDataHeader(MGMSG_MOT_REQ_HOMEPARAMS,param1=chan_ident)
req_header = ndh.packedHeader()

bsc.ser.open()
bsc.ser.write(req_header) #request home parameters
get_header = bsc.ser.read(header_length) #request home parameters
data = bsc.ser.read(packet_length) #request home parameters
bsc.ser.close()

wdh = WithDataHeader()
wdh.unpackHeader(get_header)

#Now, unpack the data
data_format = "HHHLH"#Weird. It outght to be "HHHLL", but that fails. Odd.
home_params = struct.unpack(data_format,data)
chan_ident,home_direction,limit_switch,home_vel,offset_distance=home_params

print "home velocity = "+str(home_vel/ encoder_unit_velocity)+" mm/s"

#Now, start the move to home
chan_ident=1
ndh = NoDataHeader(MGMSG_MOT_MOVE_HOME,param1=chan_ident)

bsc.ser.open()
bsc.ser.write(ndh.packedHeader()) #request home parameters
homed_header = bsc.ser.read(header_length)
bsc.ser.close()
ndh_homed = NoDataHeader()
ndh_homed.unpackHeader(homed_header)
#ndh_homed.printMe()


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
