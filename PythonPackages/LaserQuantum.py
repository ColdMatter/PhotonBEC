#A class for controlling the LaserQuantum laser via serial port
#Created earlier than 20/09/2013 by Rob Nyman
from serial import *

from time import sleep

class LaserQuantum():
	def __init__(self,port=4,timeout=1):
		self.ser = Serial(port=port,timeout=timeout) #port=0 means COM1, I think
		self.ser.close()
	def writeCommand(self,s,dont_close=False):
		if not(self.ser.isOpen()):self.ser.open()
		self.ser.write(s+"\r\n")
		if not(dont_close):self.ser.close()
	def readSerial(self,bytes=None,dont_close=False):
		if not(self.ser.isOpen()):self.ser.open()
		if bytes==None:
			s=self.ser.readall()
		else:
			s=self.ser.read(bytes)
		#
		if not(dont_close):self.ser.close()
		return s
	def setPower(self,p):
		self.writeCommand("POWER="+str(p))
	def getPower(self):
		self.writeCommand("POWER?",dont_close=1)
		s=self.readSerial(12)
		try:
			p = int(s.split("mW")[-2].split(" ")[-1]) #still needs testing
		except:
			p = None
		return p
	def isEnabled(self):
		self.writeCommand("STATUS?",dont_close=1)
		s = self.readSerial()
		ssplit = s.split("\r\n")
		if len(ssplit)==1:
			val=False
			print "Laser controller probably switched off"
		else:
			s2=s.split("\r\n")[-2]
			if s2=="ENABLED":
				val=True
			elif s2=="DISABLED":
				val=False
			else:
				val=None
		return val
	def LaserOn(self):
		self.writeCommand("ON")
	def LaserOff(self):
		self.writeCommand("OFF")
		
	def setPowerAndWait(self, pmw, tolerance=0.005):
		pl = [] 
		self.setPower(pmw)
		window_len = 3
		#tolerance = 0.5%
		p_tol = pmw * tolerance

		while True:
			sleep(0.5)
			po = self.getPower()
			pl.append(po)
			if len(pl) >= window_len:
				mae = 1.0 * sum([abs(pmw - p) for p in pl]) / window_len
				if mae <= p_tol:
					break
				del pl[0]
				
