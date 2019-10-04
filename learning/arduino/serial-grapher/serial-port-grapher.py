
'''
import serial
ser = serial.Serial("COM15", 9600)
try:
	ser.readline()
finally:
	ser.close()
'''

from PyQt4 import QtGui, QtCore

from pylab import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import threading, time, struct
import serial
		
label_fontsize=9

test_data = False

def chunks(d, n):
	return [d[x:x + n] for x in xrange(0, len(d), n)]
	
def decode_single_byte(d):
	#in binary each byte is
	#00HH HLLL
	#L - low, H - high
	d = struct.unpack(">H", d)[0]
	return d

class ReadSerialPortThread(threading.Thread):
	def __init__(self, canvas):
		threading.Thread.__init__(self)
		self.canvas = canvas
		
	def run(self):
		time.sleep(1) ##make sure the window is made by the time we call isVisible()
		ser = serial.Serial("COM15", 9600)
		ser.readline()
		while self.canvas.isVisible():
			line = ser.readline().rstrip()
			print('got line, length = ' + str(len(line)))
			#print([c for c in line])
			cc = [c for c in chunks(line, 3)]
			print(cc)
			self.canvas.data[0] = [decode_single_byte(('0' + c).decode('hex')) for c in cc]
		ser.close()
		print('not visible anymore')

class UpdatingGraphCanvas(FigureCanvas):
	def __init__(self, parent, width=4, height=4.5, dpi=100):
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes211 = fig.add_subplot(1, 1, 1)
		fig.subplots_adjust(bottom=0.15, left=0.15, top=0.95, right=0.95)
		# We want the axes cleared every time plot() is called
		self.axes211.hold(False)
		
		###compute initial figure
		#self.axes211.set_xlabel("time (s since midnight)",fontsize=label_fontsize)
		#self.axes211.set_ylabel("Control voltage (mV)",fontsize=label_fontsize)
		self.axes211.set_ylim(0, 1 << 14)
		
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		
		if test_data:
			self.i = 0
		timer = QtCore.QTimer(self)
		QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
		timer.start(50) #in ms
		self.data = [[0]]
		ReadSerialPortThread(self).start()
		
	def update_figure(self):
		if test_data:
			self.i += 1
			t = linspace(0, 720, 500)
			amp = sin(0.02*t + self.i)
		else:
			amp = self.data[0]
			t = arange(len(amp))
		
		#subplot(2,1,1)
		self.axes211.plot(t, amp, "*", markersize=3)
		self.axes211.set_xlabel("time")
		self.axes211.set_ylabel("amplitude")
		#self.axes211.set_ylim(1000*array(self.stabiliser.control_range)) #should reflect the stabilister control range!!!
		self.axes211.grid(True)
		self.draw()
		
class ApplicationWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.dc = UpdatingGraphCanvas(parent=self,width=5, height=4, dpi=100)
		self.setCentralWidget(self.dc)
	
if __name__=="__main__":
	qApp = QtGui.QApplication(sys.argv)
	aw = ApplicationWindow()
	aw.show()
	sys.exit(qApp.exec_())
