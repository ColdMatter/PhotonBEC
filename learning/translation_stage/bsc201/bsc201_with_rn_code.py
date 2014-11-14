#execfile("bsc201.py")
#Have played in Device manager, as it says on p54 of the operating manual. Port is COM8

import serial
import time
import struct
import textwrap

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
	try:
		msg= thorlabs_apt_messages.__inverse_messages[message_number] #defined in thorlabs_apt_messages
	except:
		msg="Message not found; "+str(message_number)
	return msg

class NoDataHeader():
	#Message header format for messages with no packet data
	def __init__(self,message_ID = 0,param1=0,param2=0,dest=0x50,source=0x01):
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
		#occasionally breaks. Why???
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

class BSC201():
	def __init__(self,comport=12,channel_ident=1):
		self.ser = serial.Serial(comport-1,baudrate=115200,timeout=5)
		self.channel_ident=channel_ident
		dump = self.ser.read(512) #discard all the data already in the channel

	def sendBasicCommand(self,message):
		self.ser.write(NoDataHeader(message).packedHeader())
	def flashFrontPanel(self):
		self.sendBasicCommand(MGMSG_MOD_IDENTIFY) #flashes front panel LEDs
		
	def getMotorPosition(self):
		bsc.ser.write(NoDataHeader(MSMSG_MOT_REQ_STATUSUPDATE, self.channel_ident).packedHeader())
		reply = bsc.ser.read(header_length + 28)
		#the manual pg93 says the response is 14 bytes long
		# however we seem to always get 34 bytes in total coming back
		# dunno what to do with them so i just discard
		if len(reply) == 0:
			raise IOError("no reply from controller")
		fields = struct.unpack("HBBBBHIII", reply[:20])
		if fields[0] != MSMSG_MOT_GET_STATUSUPDATE:
			raise IOError("wrong reply: 0x%02x" % fields[0])
		return fields[6]
		
	def jogMotor(self, forward = True):
		"""returns new position of motor"""
		direction_byte = 0x01 if forward else 0x02 #see manual pg58
		bsc.ser.write(NoDataHeader(MGMSG_MOT_MOVE_JOG, self.channel_ident, direction_byte).packedHeader())
		reply = bsc.ser.read(header_length + 14)
		#the manual says the response is 14 bytes long
		if len(reply) == 0:
			raise IOError("no reply from controller")
		fields = struct.unpack("HBBBBHIII", reply)
		if fields[0] != MGMSG_MOT_MOVE_COMPLETED:
			raise IOError("wrong reply: 0x%02x" % fields[0])
		return fields[6] #position
		
	def goHome(self):
		bsc.ser.write(NoDataHeader(MGMSG_MOT_MOVE_HOME, self.channel_ident).packedHeader())
		reply = bsc.ser.read(header_length) #pg 52 of manual
		if len(reply) == 0:
			raise IOError("no reply from controller")
		fields = struct.unpack("HBBBB", reply)
		if fields[0] != MGMSG_MOT_MOVE_HOMED:
			raise IOError("wrong reply: 0x%02x" % fields[0])
			
	#def moveMotorRelative(self):
	
		
	#<JM> the below was coded by RN, im not touching it yet but writing my own
	def goHome_RobNyman(self,home_waiting_time=10):
            ndh = NoDataHeader(MGMSG_MOT_MOVE_HOME,param1=self.channel_ident)
            self.ser.open()
            print "homing"
            self.ser.write(ndh.packedHeader()) #request home parameters
            #At this point, we should wait until the home move has finished!!!
            #time.sleep(home_waiting_time)#HACK!
            homed_header = bsc.ser.read(header_length) #Controller sends back data to say that it has finished
            #Oddly, appears to be empty. not going home??
            self.ser.close()
            ndh_homed = NoDataHeader()
            ndh_homed.unpackHeader(homed_header)
            print lookup_message(ndh_homed.message_ID)
        def getHomeVelocity(self,safe_mode = False):
            ndh = NoDataHeader(MGMSG_MOT_REQ_HOMEPARAMS,param1=self.channel_ident)
            req_header = ndh.packedHeader()
            #
            self.ser.open()
            self.ser.write(req_header) #request home parameters
            get_header = self.ser.read(header_length) #request home parameters
            wdh = WithDataHeader()
            wdh.unpackHeader(get_header)
            packet_length = wdh.packet_length
            data = self.ser.read(packet_length) #request home parameters
            self.ser.close()
            #
            #Now, unpack the data
            data_format = "HHHLH"#Weird. It outght to be "HHHLL", but that fails. Odd.
            if not(safe_mode):
                home_params = struct.unpack(data_format,data)
                channel_ident,home_direction,limit_switch,home_vel,offset_distance=home_params
                #       
                home_velocity = home_vel/ encoder_unit_velocity     
            else: 
                home_velocity = data
            return home_velocity
	    
def giveSimpleCommand(bsc,command,param1=0,param2=0,dest=0x50,source=0x01):
	#Should work for request commands, but not for commands with data attached
	ndh_params = NoDataHeader(MGMSG_MOT_SET_HOMEPARAMS,param1=param1,param2=param2,dest=dest,source=source)
	params_header=ndh_params.packedHeader()
	bsc.ser.open()
	bsc.ser.write(params_header) #request home parameters
	bsc.ser.close()

def readBasicData(bsc,packet_length=6):
	#read after a "request" command
	bsc.ser.open()
	#bsc.ser.write(req_header) #request home parameters
	data = bsc.ser.read(packet_length) #request home parameters
	bsc.ser.close()
	return data
    
def header_to_NoDataHeader(header,printMe=True):
	ndh=NoDataHeader()
	ndh.unpackHeader(header)
	if printMe: ndh.printMe()
	return ndh

def make_hex(data):
	format_str = " ".join(["%02x"] * len(data))
	t = tuple([ord(i) for i in data])
	return textwrap.fill(format_str, 80) % t
#make_hex(NoDataHeader(MGMSG_MOD_IDENTIFY).packedHeader())

#--------------------------------
#START TALKING TO THE CONTROLLER

bsc = BSC201()

#bsc.flashFrontPanel() #check that communication is working
print("position = " + str(bsc.getMotorPosition()))
'''
for i in range(8):
	print("now at " + str(bsc.jogMotor(i % 2 == 0)))
	time.sleep(2)
'''
'''
for i in range(8):
	bsc.jogMotor()
print("finished moving away")	
bsc.goHome()
'''

#data = NoDataHeader(MGMSG_MOT_MOVE_RELATIVE, 0x01).packedHeader()

rel_distance = 204800 #got this by jogMotor() once and then getMotorPosition()
data = struct.pack("HBBBBHI", MGMSG_MOT_MOVE_RELATIVE, 0x06, 0x00, 0x50 | 0x80, 0x01, 0x0001, rel_distance)
print("sending: ")
print(make_hex(data))
bsc.ser.write(data)
print("reading..")
reply = bsc.ser.read(64)
print("end read")
print("len = " + str(len(reply)))
print(make_hex(reply))
print(struct.unpack("HBBBBHIII", reply))

print("position = " + str(bsc.getMotorPosition()))
#--------------------------------
#GO TO HOME



'''
#Probably, we need to set the home velocity to something reasonable like 0.1 mm/s

packet_length=14
channel_ident = 1
ndh_params = NoDataHeader(MGMSG_MOT_SET_HOMEPARAMS,param1=channel_ident)
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
#--------------------------------
#SET UP A MOVE TO AN ABSOLUTE POSITION
#Can be done in one step, but clearer in two steps (set param; then move)
#--------------------------------
#packet_length=6
#channel_ident = 1
#ndh_params = NoDataHeader(MGMSG_MOT_SET_MOVEABSPARAMS,param1=channel_ident)
#params_header=ndh_params.packedHeader()

#data_format = "HL"
#absolute_distance = int(17e-3 * encoder_unit_position) #17 mm position
#data=struct.pack(data_format,channel_ident,absolute_distance)

#Check the move parameters first of all
#XXXXXXXXXXXXX
#giveSimpleCommand(bsc,MGMSG_MOT_REQ_MOVEABSPARAMS,param1=channel_ident)
#header = readBasicData(bsc,packet_length=header_length)
#data = readBasicData(bsc,packet_length=14)
#data_format="HHHLH" #HHHLH?
#ud = struct.unpack("HHH",data)
#ndh = header_to_NoDataHeader(header)

"""
#Set the parameters
bsc.ser.open()
bsc.ser.write(params_header) #request home parameters
bsc.ser.write(data) #request home parameters
bsc.ser.close()


#Do the move
ndh_move= NoDataHeader(MGMSG_MOT_MOVE_ABSOLUTE ,param1=channel_ident)
ndh_move_header = ndh_move.packedHeader()
bsc.ser.open()
bsc.ser.write(ndh_move_header) #request home parameters
bsc.ser.close()

#Stop the move!!
ndh_move= NoDataHeader(MGMSG_MOT_MOVE_STOP ,param1=channel_ident)
ndh_move_header = ndh_move.packedHeader()
bsc.ser.open()
bsc.ser.write(ndh_move_header) 
bsc.ser.close()

#

#Read absolute move parameters
####wdh = WithDataHeader(MGMSG_MOT_SET_MOVEABSPARAMS,param1=channel_ident)
"""



#EoF
