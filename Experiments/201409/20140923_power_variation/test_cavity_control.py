#ipython --gui=qt4
import time
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("D:\Control\CavityLock")

from pbec_experiment import *
from random import shuffle,sample

"""
import threading
class CavityLocker(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = False #python keeps running even if only the cavity lock is running
		self.running = False
		import cavity_lock #starts cavity lock softward
		self.cavity_lock = cavity_lock
	def setSetPoint(self,newValue):
		self.cavity_lock.setSetPoint(newValue)

try:
	ring_rad = cl.cavity_lock.s.ring_rad
	print "Cavity lock software already running"
except:
	print "Starting Cavity lock software"
	cl = CavityLocker()
	cl.start()

#Pause for the user to set up the lock.
nonsense = raw_input("Lock the cavity, then press Enter to continue...")

print "Now the experiment runs...a blocking call..."
from scipy import linalg,random
ev = linalg.eig(random.rand(2000,2000)) #2000 x 2000 blocks for an appropriate duration
"""

import multiprocessing
from multiprocessing import Process
from scipy import linalg,random
#clObject=[] #something that's passed as a pointer, not a value. Will be overwritten
def hardWorkFunction(n=500)
	ev = linalg.eig(random.rand(n,n)) #2000 x 2000 blocks for an appropriate duration
	print "...done",
	#return ev

proc = Process(target=hardWorkFunction,args=(500,))
proc.start(); print "Waiting...",

#proc.join()

from multiprocessing import Process

def f(name):
    print 'hello', name

if __name__ == '__main__':
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()

#EoF
