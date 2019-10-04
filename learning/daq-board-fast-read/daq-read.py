
#read data quickly from the daq board
#https://sine.ni.com/nips/cds/view/p/lang/en/nid/201986
#aim for 12 bit precision and 10 ksamples/sec

#written around 13/2/2017

import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import time

import SingleChannelAI

import matplotlib
import matplotlib.pyplot as plt

N = 10000000
rate = 1e4

#while 1:
for i in range(2):
	print('[' + str(datetime.datetime.now()) + '] reading')
	st = time.time()
	data = SingleChannelAI.SingleChannelAI(Npts=N, rate=rate, device="Dev1", channel="ai0", minval=0, maxval=3.5)
	et = time.time()

	print('[' + str(datetime.datetime.now()) + '] data collection took ' + str(et-st) + ' sec')

	fig = plt.figure(1)
	plt.clf()
	plt.plot(data, '-x', markersize=2)
	plt.grid()
	plt.ylabel('Volts / V')
	plt.xlabel('Point')
	plt.title('Data from DAQ board')
	plt.show()
	
	time.sleep(5)