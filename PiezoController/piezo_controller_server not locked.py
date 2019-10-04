
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

from serial import SerialException

import threading
import pbec_ipc
from ThorlabsMDT69xA import ThorlabsMDT69xA

class PiezoControllerServer(object):
	def __init__(self, glob=None):
		self.piezo_driver = None
		try:
			self.setEnabled(True)
		except Exception as e:
			print 'setEnabled ' + repr(e)
		if not glob:
			glob = globals()
		ipc = pbec_ipc.IPCServer('localhost', pbec_ipc.PORT_NUMBERS['piezo_controller'], glob)
		ipc.start()

	def setXvolts(self, V):
		self.piezo_driver.setXvolts(V)
	def setYvolts(self, V):
		self.piezo_driver.setYvolts(V)
	def setZvolts(self, V):
		self.piezo_driver.setZvolts(V)
		
	setFineDelayPiezoVolts = setXvolts
	setCavityLengthPiezoVolts = setYvolts
	
	def getXvolts(self):
		return self.piezo_driver.getXvolts()
	def getYvolts(self):
		return self.piezo_driver.getYvolts()
	def getZvolts(self):
		return self.piezo_driver.getZvolts()

	def setEnabled(self, enabled):
		if enabled:
			try:
				self.piezo_driver = None
				self.piezo_driver = ThorlabsMDT69xA()
				self.piezo_driver.keep_open = True
			except (ValueError, SerialException) as e:
				print 'piezo driver not switched on'
				raise Exception(repr(e))
		else:
			if self.piezo_driver:
				self.piezo_driver.ser.close()
			self.piezo_driver = None
			
	def isEnabled(self):
		return self.piezo_driver != None
		
if __name__ == "__main__":
	running = True
	pzt_server = None
	pzt_server = PiezoControllerServer()
	import time
	while running:
		time.sleep(3)