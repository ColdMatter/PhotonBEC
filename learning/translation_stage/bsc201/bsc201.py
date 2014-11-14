#execfile("bsc201.py")
#Have played in Device manager, as it says on p54 of the operating manual. Port is COM8

import serial
import time
import struct
import textwrap

from thorlabs_apt_messages import *
import thorlabs_apt_messages #yes, I know, there's a hack going on

#Motor calibration for DRV014
#encoder_unit_position = 25600 * 1e3 #converts steps to metres NOT mm
#encoder_unit_velocity= 25600 * 1e3 #converts steps to metres NOT mm
#encoder_unit_acceleration= 25600 * 1e3 #converts steps to metres NOT mm
encoder_unit_position = 409600*1e3 #converts steps to metres NOT mm
encoder_unit_velocity= 21987328*1e3 #converts steps to metres/s NOT mm/s
encoder_unit_acceleration= 4506*1e3 #converts steps to metres/s/s NOT mm/s/s



header_length=6 #length of header in bytes

def lookup_message(message_number):
	try:
		msg= thorlabs_apt_messages.__inverse_messages[message_number] #defined in thorlabs_apt_messages
	except:
		msg="Message not found; "+str(message_number)
	return msg

class Header():
	#Message header format for messages with no packet data
	def __init__(self, message_ID = 0, param1=0, param2=0, dest=0x50, source=0x01):
                #destination 0x50 is Generic USB hardware unit (aka the BSC201)
                #source 0x01 is the PC (aka Host controller)
                self.message_ID = message_ID
                self.param1=param1		
                self.param2=param2
                self.dest=dest
                self.source=source
                self.message_format = "HBBBB" #Note: H means 2 bytes, B means 1 byte
	def packedHeader(self):
		data = struct.pack(self.message_format,self.message_ID,self.param1,self.param2,self.dest,self.source)
		#print("sending:\n" + make_hex(data))
		return data
	#TODO unpackHeader() should actually be a constructor
	# and then maybe use it instead of struct.unpack() in all those methods in BSC
	'''
	def unpackHeader(self,header):
		#Header is a string, as received from serial port
		#occasionally breaks. Why???
		header = struct.unpack(self.message_format,header) 
		self.message_ID,self.param1,self.param2,self.dest,self.source=header
	'''
	def dict(self):
		return {"message_ID":self.message_ID,"param1":self.param1,"param2":self.param2,"dest": self.dest,"source":self.source}
	def printMe(self):
            d = self.dict()
            print "Message: "+lookup_message(d["message_ID"])
            for k in ["param1","param2","dest","source"]:
                print k+"\t"+str(d[k])
		#Fix this to be more readable

class HeaderWithData(Header):
	#Message header format for messages with packet data, and the data too
	#Message header format for messages with no packet data
	def __init__(self, message_ID = 0, extra_format = "", extra_fields = (),
			param1 = 0, param2 = 0, dest=0x50, source=0x01):
		Header.__init__(self, message_ID, param1, param2, dest, source)
		self.extra_format = extra_format
		self.extra_fields = extra_fields
	def packedHeader(self):	       
	        logicked_dest = self.dest | 0x80 #means there is data
                return struct.pack(self.message_format + self.extra_format, self.message_ID,
			self.param1, self.param2, logicked_dest, self.source, *self.extra_fields)
	def dict(self):
		ret = Header.dict(self)
		ret["extra_format"] = self.extra_format
		ret["extra_fields"] = self.extra_fields
		return ret

#by the way, param1 refers to the length of the packet
# i figured this out after coding pretty much all of this
class BSC201():
	def __init__(self,comport=12,channel_ident=1):
		self.ser = serial.Serial(comport-1,baudrate=115200,timeout=0)
		self.channel_ident=channel_ident
		#discard all the data already in the channel
		# will return immediately if no data since timeout=0
		self.ser.read(1024) 
		self.ser.setTimeout(15)
		#send setvelocity and stuff here
		self.setHomeVelocity()
		self.setVelocityParameters()
		self.setBacklashCorrection()
		self.setPowerParameters()
		
	def close(self):
		#once the class is closed, dont reopen it, make another instead
		self.ser.close()

	def sendBasicCommand(self,message):
		self.ser.write(Header(message).packedHeader())
	def flashFrontPanel(self):
		self.sendBasicCommand(MGMSG_MOD_IDENTIFY) #flashes front panel LEDs

	def __sendSimpleHeaderAndRead(self, header_args, body_length, struct_fmt, expt_reply):
		self.ser.write(Header(*header_args).packedHeader())
		reply = self.ser.read(header_length + body_length)
		if len(reply) == 0:
			raise IOError("no reply from controller")
		fields = struct.unpack(struct_fmt, reply)
		if fields[0] != expt_reply:
			#print(make_hex(reply))
			raise IOError("wrong reply: 0x%04x" % fields[0])
		return fields

	def getMotorPosition(self):
		return self.__sendSimpleHeaderAndRead(
			header_args = (MSMSG_MOT_REQ_STATUSUPDATE, self.channel_ident),
			body_length = 28,
		#the manual pg93 says the response is 14 bytes long
		# however we seem to always get 34 bytes in total coming back (and 28 + 6 = 34)
		# dunno what to do with them so i just discard by dumping in lots of longs in the struct
			struct_fmt = "HBBBBHIIIlllh",
			expt_reply = MSMSG_MOT_GET_STATUSUPDATE
		)[6] #position
	
	'''
	def jogMotor(self, forward = True):
		"""returns new position of motor"""
		direction_byte = 0x01 if forward else 0x02 #see manual pg58
		return self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_MOVE_JOG, self.channel_ident, direction_byte),
			body_length = 14, #the manual says the response is 14 bytes long
			struct_fmt = "HBBBBHIII",
			expt_reply = MGMSG_MOT_MOVE_COMPLETED
		)[6] #position
	'''
		
	def goHome(self):
		t = self.ser.timeout
		self.ser.setTimeout(15)
		self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_MOVE_HOME, self.channel_ident),
			body_length = 0, #pg 52 of manual
			struct_fmt = "HBBBB",
			expt_reply = MGMSG_MOT_MOVE_HOMED
		)
		self.ser.setTimeout(t)

	def getHomeVelocity(self):
		return self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_REQ_HOMEPARAMS, self.channel_ident),
			body_length = 14, #pg 48 of manual
			struct_fmt = "HBBBBHHHII",
			expt_reply = MGMSG_MOT_GET_HOMEPARAMS
		)[8] #velocity

	def setHomeVelocity(self, velocity=21986044):
		#default taken from the Thorlabs APT software
	
		#the manual says those other parameters are ignored, but that doesnt actually work so
		# i had to use reverse engineering to find the values it accepts
		head = HeaderWithData(MGMSG_MOT_SET_HOMEPARAMS, "HHHII",
			(chan_ident, 2, 1, velocity, 40960), param1=0x0e)
		self.ser.write(head.packedHeader())
		#no reply
		
	def getVelocityParameters(self):
		return self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_REQ_VELPARAMS, self.channel_ident),
			body_length = 14, #pg 39 of manual
			struct_fmt = "HBBBBHIII",
			expt_reply = MGMSG_MOT_GET_VELPARAMS
		)[6:9]
		
	def setVelocityParameters(self, maxVel=43972088, acc=4503, minVel=0):
		#defaults taken from the Thorlabs APT software
		head = HeaderWithData(MGMSG_MOT_SET_VELPARAMS, "HIII",
			(self.channel_ident, minVel, acc, maxVel), param1=0x0e)
		self.ser.write(head.packedHeader())
		
	def getBacklashCorrection(self):
		return self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_REQ_GENMOVEPARAMS, self.channel_ident),
			body_length = 6, #pg 45 of manual
			struct_fmt = "HBBBBHI",
			expt_reply = MGMSG_MOT_GET_GENMOVEPARAMS
		)[6]
		
	def setBacklashCorrection(self, backlash=4096):
		head = HeaderWithData(MGMSG_MOT_SET_GENMOVEPARAMS, "Hi",
			(chan_ident, backlash), param1=0x06)
		self.ser.write(head.packedHeader())
		
	def getPowerParameters(self):
		return self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_REQ_POWERPARAMS, self.channel_ident),
			body_length = 6, #pg 43 of manual
			struct_fmt = "HBBBBHHH",
			expt_reply = MGMSG_MOT_GET_POWERPARAMS
		)[6:8]
		
	def setPowerParameters(self, restFactor=131, moveFactor=6):
		#defaults taken from the Thorlabs APT software
		head = HeaderWithData(MGMSG_MOT_SET_POWERPARAMS, "HHH",
			(self.channel_ident, restFactor, moveFactor), param1=0x06)
		self.ser.write(head.packedHeader())
		
	def __moveMotor(self, message_ID, argument):
		#see manual pg53
		request_header = HeaderWithData(message_ID, "Hi", (0x0001, argument), param1=0x06)
		self.ser.write(request_header.packedHeader())
		reply = self.ser.read(header_length + 14)
		if len(reply) == 0:
			raise IOError("no reply from controller")
		fields = struct.unpack("HBBBBHIII", reply)
		if fields[0] != MGMSG_MOT_MOVE_COMPLETED:
			raise IOError("wrong reply: 0x%02x" % fields[0])
		return fields[6] #position
		
	def moveMotorRelative(self, rel_distance):
		"""
		Returns new position of motor.
		rel_distance is a signed integer, i.e. you go backwards too
		20000counts = 1mm
		"""
		return self.__moveMotor(MGMSG_MOT_MOVE_RELATIVE, rel_distance)
		
	def moveMotorAbsolute(self, position):
		"""
		Returns new position of motor.
		20000counts = 1mm
		"""
		return self.__moveMotor(MGMSG_MOT_MOVE_ABSOLUTE, position)

def header_to_Header(header,printMe=True):
	ndh=Header()
	ndh.unpackHeader(header)
	if printMe: ndh.printMe()
	return ndh

def make_hex(data):
	format_str = " ".join(["%02x"] * len(data))
	t = tuple([ord(i) for i in data])
	return textwrap.fill(format_str, 80) % t
#make_hex(Header(MGMSG_MOD_IDENTIFY).packedHeader())

#--------------------------------
#START TALKING TO THE CONTROLLER

bsc = BSC201()
chan_ident = 1
'''
there is a system log

Ben
techsupport.uk@thorlabs.com
'''

bsc.setHomeVelocity()
bsc.setVelocityParameters()
bsc.setBacklashCorrection()
bsc.setPowerParameters()
try:
	#bsc.flashFrontPanel() #check that communication is working
	#print("position = " + str(bsc.getMotorPosition()))
	'''
	#jog motor test
	for i in range(8):
		print("now at " + str(bsc.jogMotor(i % 2 == 0)))
		time.sleep(2)
	'''

	'''
	#going home test
	print('going home test')
	for i in range(8):
		bsc.moveMotorRelative(100000)
	print("finished moving away")	
	bsc.goHome()
	'''

	'''
	#moveMotorRelative() test
	print('move motor relative test')
	for i in range(10):
		bsc.moveMotorRelative(20000)
		time.sleep(0.3)
	print("finished one way moving")
	for i in range(10):
		bsc.moveMotorRelative(-20000)
		time.sleep(0.3)
	print("finished the other way")
	

	
	#moveMotorAbsolute test
	print('move motor absolute test')
	for i in range(0, 11, 2):
		bsc.moveMotorAbsolute(i * 50000)
		time.sleep(1)
	print("finished moved")
	bsc.goHome()
	

	
	#set home velocity test
	print('set home velocity test')
	for f in [1, 2, 3, 4]:
		print('moving')
		bsc.moveMotorRelative(1500000)
		bsc.setHomeVelocity(10993022 * f)
		print("gethomevelocity = " + str(bsc.getHomeVelocity()))
		bsc.goHome()
	

	#bsc.setHomeVelocity(21986044)
	#bsc.goHome()
	
	
	#set velocity parameters test
	print('set velocity parameters test')
	minvel = 0
	acc = 4503
	maxvel = 43972088
	for f in [1, 2, 3, 4]:
		print('moving')
		bsc.setVelocityParameters(maxvel, acc / f) #also try modifying acceleration
		print(bsc.getVelocityParameters())
		bsc.moveMotorRelative(1000000 * (-1)**f)
		time.sleep(1)
	'''
	'''
	#going home test
	print('going home test')
	for i in range(8):
		bsc.moveMotorRelative(100000)
	print("finished moving away")	
	bsc.goHome()
	
	bsc.setPowerParameters()

	data = HeaderWithData(0x0426, "HHH", (chan_ident, 131, 6), param1=0x06).packedHeader()
	print("sending: ")
	print(make_hex(data))
	bsc.ser.write(data)
	'''
	'''
	data = Header(0x0427, chan_ident).packedHeader()
	print("sending: ")
	print(make_hex(data))
	bsc.ser.write(data)
	print("reading..")
	reply = bsc.ser.read(64)
	print("end read")
	print("len = " + str(len(reply)))
	if len(reply) > 0:
		print(make_hex(reply))
		print(struct.unpack("HBBBBHHH", reply))
	'''
	'''
	#going home test
	print('going home test')
	for i in range(8):
		bsc.moveMotorRelative(100000)
	print("finished moving away")	
	bsc.goHome()
	'''
finally:
	bsc.close()
#--------------------------------
#GO TO HOME



'''
#Probably, we need to set the home velocity to something reasonable like 0.1 mm/s

packet_length=14
channel_ident = 1
ndh_params = Header(MGMSG_MOT_SET_HOMEPARAMS,param1=channel_ident)
params_header=ndh_params.packedHeader()

home_vel = int(1e-3 * encoder_unit_velocity)
home_direction,limit_switch,offset_distance =1,1,0

data_format = "HHHLL"
home_params = channel_ident,home_direction,limit_switch,home_vel,offset_distance
data=struct.pack(data_format,channel_ident,home_direction,limit_switch,home_vel,offset_distance)

#Set the parameters: these lines seem to break everything!!!
if 0:
	bsc.ser.open()
	bsc.ser.write(params_header) #request home parameters
	bsc.ser.write(data) #request home parameters
	bsc.ser.close()

print "home velocity = "+str(1e3*bsc.getHomeVelocity())+" mm/s"

#Now do the move
bsc.goHome(2)
'''

#EoF
