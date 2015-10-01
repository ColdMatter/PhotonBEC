
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import pbec_ipc
from ThorlabsMDT69xA import ThorlabsMDT69xA

class PiezoControllerServer(object):
	def __init__(self):
		self.piezo_driver = ThorlabsMDT69xA()
		self.piezo_driver.keep_open = True
		ipc = pbec_ipc.IPCServer('localhost', pbec_ipc.PORT_NUMBERS['piezo_controller'], globals())
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

if __name__ == "__main__":
	running = True
	pzt_server = None
	pzt_server = PiezoControllerServer()
	import time
	while running:
		time.sleep(3)