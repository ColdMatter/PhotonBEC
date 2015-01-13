#execfile("bsc201.py")
#Have played in Device manager, as it says on p54 of the operating manual. Port is COM8

import serial
import time
import struct

from apt_messages import *
import apt_messages #yes, I know, there's a hack going on





header_length=6 #length of header in bytes

def lookup_message(message_number):
	try:
		msg= apt_messages.__inverse_messages[message_number] #defined in apt_messages
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
class ThorlabsAPT(object):
	def __init__(self, comport, channel_ident=1):
		self.ser = serial.Serial(comport-1,baudrate=115200,timeout=0)
		self.channel_ident = channel_ident
		#discard all the data already in the channel
		# will return immediately if no data since timeout=0
		self.ser.read(1024) 
		self.ser.setTimeout(60)
		#send setvelocity and stuff here
		
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
		#t = self.ser.timeout
		#self.ser.setTimeout(15)
		self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_MOVE_HOME, self.channel_ident),
			body_length = 0, #pg 52 of manual
			struct_fmt = "HBBBB",
			expt_reply = MGMSG_MOT_MOVE_HOMED
		)
		#self.ser.setTimeout(t)

	def getHomeVelocity(self):
		return self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_REQ_HOMEPARAMS, self.channel_ident),
			body_length = 14, #pg 49 of manual
			struct_fmt = "HBBBBHHHII",
			expt_reply = MGMSG_MOT_GET_HOMEPARAMS
		)[8] #velocity

	def getHomeOffset(self):
		return self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_REQ_HOMEPARAMS, self.channel_ident),
			body_length = 14, #pg 49 of manual
			struct_fmt = "HBBBBHHHII",
			expt_reply = MGMSG_MOT_GET_HOMEPARAMS
		)[9] #offset

	def setHomeParameters(self, velocity,offset):
		#the manual says those other parameters are ignored, but that doesnt actually work so
		# i had to use reverse engineering to find the values it accepts
		head = HeaderWithData(MGMSG_MOT_SET_HOMEPARAMS, "HHHII",
			(self.channel_ident, 2, 1, velocity, offset), param1=0x0e)
		self.ser.write(head.packedHeader())
		#no reply
	
	def setHomeVelocity(self,velocity,offset=40960):
		self.setHomeParameters(velocity,offset=offset)

	def getVelocityParameters(self):
		return self.__sendSimpleHeaderAndRead(
			header_args = (MGMSG_MOT_REQ_VELPARAMS, self.channel_ident),
			body_length = 14, #pg 39 of manual
			struct_fmt = "HBBBBHIII",
			expt_reply = MGMSG_MOT_GET_VELPARAMS
		)[6:9]
		
	def setVelocityParameters(self, maxVel, acc, minVel):
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
		
	def setBacklashCorrection(self, backlash):
		head = HeaderWithData(MGMSG_MOT_SET_GENMOVEPARAMS, "Hi",
			(self.channel_ident, backlash), param1=0x06)
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
		
	def stepMotorRelative(self, rel_distance):
		"""
		Returns new position of motor.
		rel_distance is a signed integer, i.e. you go backwards too
		20000counts = 1mm for BSC201
		"""
		return self.__moveMotor(MGMSG_MOT_MOVE_RELATIVE, rel_distance)
		
	def stepMotorAbsolute(self, position):
		"""
		Returns new position of motor.
		20000counts = 1mm for BSC201
		"""
		return self.__moveMotor(MGMSG_MOT_MOVE_ABSOLUTE, position)

#Motor calibration for DRV014
drv014_encoder_unit_position = 409600*1e3 #converts steps to metres NOT mm
drv014_encoder_unit_velocity= 21987328*1e3 #converts steps to metres/s NOT mm/s
drv014_encoder_unit_acceleration= 4506*1e3 #converts steps to metres/s/s NOT mm/s/s

#zst213_encoder_unit_position = 20086236*1e3
#see the manual we have in the drawer
zst213_encoder_unit_position = int(24*2048 * (29791./729))*1e3
		
prm1_mz8e_encoder_unit_position = 1919.64

#---Modifications made 12/1/15 by RAN
#New method of ThorlabsAPT superclass: setHomeParameters
#Intention: update BSC201 and TST101 classes to make use of the "HomeOffset" calibration correctly.

class BSC201(ThorlabsAPT):
	def __init__(self, comport=13, channel_ident=1):
		super(BSC201, self).__init__(comport, channel_ident)
		self.setHomeVelocity()
		self.setVelocityParameters()
		self.setBacklashCorrection()
		self.setPowerParameters()
		
	#default taken from the Thorlabs APT software
	#relates to motor drv014
	#ran thorlabs APT software then ran getXXX() methods
	def setHomeVelocity(self, velocity=21986044):
		super(BSC201, self).setHomeVelocity(velocity)
	def setVelocityParameters(self, maxVel=43972088, acc=4503, minVel=0):
		super(BSC201, self).setVelocityParameters(maxVel, acc, minVel)
	def setBacklashCorrection(self, backlash=4096):
		super(BSC201, self).setBacklashCorrection(backlash)
	def setPowerParameters(self, restFactor=131, moveFactor=6):
		super(BSC201, self).setPowerParameters(restFactor, moveFactor)

	#units in meters
	def moveRelative(self, rel_distance):
		return self.stepMotorRelative(int(rel_distance * drv014_encoder_unit_position))
	def moveAbsolute(self, distance):
		return self.stepMotorAbsolute(int(distance * drv014_encoder_unit_position))
		
#getMotorPosition() and 
class TST101(ThorlabsAPT):
	def __init__(self, comport=8, channel_ident=1):
		super(TST101, self).__init__(comport, channel_ident)
		self.setHomeVelocity()
		self.setVelocityParameters()
		self.setBacklashCorrection()

	#default taken from the Thorlabs APT software
	#relates to motor zst213
	#ran thorlabs APT software then ran getXXX() methods
	def setHomeVelocity(self, velocity=26954160):
		super(TST101, self).setHomeVelocity(velocity)
	def setVelocityParameters(self, maxVel=107816640, acc=22085, minVel=0):
		super(TST101, self).setVelocityParameters(maxVel, acc, minVel)
	def setBacklashCorrection(self, backlash=40172):
		super(TST101, self).setBacklashCorrection(backlash)
		
	#units in meters
	def moveRelative(self, rel_distance):
		return self.stepMotorRelative(int(rel_distance * zst213_encoder_unit_position))
	def moveAbsolute(self, distance):
		return self.stepMotorAbsolute(int(distance * zst213_encoder_unit_position))

class TDC001(ThorlabsAPT):
	def __init__(self, comport=14, channel_ident=1):
		super(TDC001, self).__init__(comport, channel_ident)
		self.setHomeParameters()
		self.setVelocityParameters()
		self.setBacklashCorrection()

	#default taken from the Thorlabs APT software
	#relates to motor PRM1/MZ8E
	#ran thorlabs APT software then ran getXXX() methods
	def setHomeParameters(self, velocity=42941.66,offset = 7679):
		super(TDC001, self).setHomeParameters(velocity,offset)
	def setVelocityParameters(self, maxVel=5*42941.66, acc=14.66, minVel=0):
		super(TDC001, self).setVelocityParameters(maxVel, acc, minVel)
	def setBacklashCorrection(self, backlash=1919.64):
		super(TDC001, self).setBacklashCorrection(backlash)
	
	#units in meters
	def moveRelative(self, rel_distance):
		#NOTE:angles are in degrees
		return self.stepMotorRelative(int(rel_distance * prm1_mz8e_encoder_unit_position))
	def moveAbsolute(self, distance):
		#NOTE:angles are in degrees
		return self.stepMotorAbsolute(int(distance * prm1_mz8e_encoder_unit_position))
		
#EoF
