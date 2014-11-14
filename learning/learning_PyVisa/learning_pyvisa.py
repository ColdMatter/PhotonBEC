#ipython --pylab

#exec(open("learning_pyvisa.py").read())
from visa import *
import time

if 0:
	laser_quantum=instrument("COM5")
	print(laser_quantum.ask("STATUS?"))
	print(laser_quantum.ask("POWER?"))
#-----------

USB_name="USB0::0x0699::0x03AA::C013639"
#Alternatively: USB_name = get_instruments_list()[0]
tek=instrument(USB_name)
tek.write("ACQ?\r\n")
print(tek.read_raw())
tek.ask("ACQ?")
tek.ask("DIS?")
tek.ask("WAVF?")

tek.write("DATA:ENC ASCII")
#tek.write("CH1:VOLTS 2E-3")
tek.write("DATA:SOURCE CH1")
tek.write("HOR:MAIN:SCALE 20e-3")

#ymult=float(tek.ask("WFMPRE:YMULT?"))
#xincr=float(tek.ask("WFMPRE:XINCR?"))
#dump = tek.ask("CURVE?")
#data = array(dump.split(","),dtype=int)
#plot(ymult*data)

def get_data():
	#A crude function to return some data from a TEKTRONIX oscilloscope.
	ymult=float(tek.ask("WFMPRE:YMULT?"))
	xincr=float(tek.ask("WFMPRE:XINCR?"))
	dump = tek.ask("CURVE?")
	data = ymult*array(dump.split(","),dtype=int)
	t = xincr*array(range(len(data)))
	clf()
	plot(t,data)




#EOF
