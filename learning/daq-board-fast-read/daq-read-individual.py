
#read data from the daq board with lots of individual calls 

#written around 11/4/2017

import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import time, datetime

import SingleChannelAI

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

reading_count = 200
Npts = 1000
rate = 1e4
interval = 0.05

points = []
for i in range(reading_count):
	print('[' + str(datetime.datetime.now()) + '] reading')
	data = SingleChannelAI.SingleChannelAI(Npts=Npts, rate=rate, device="Dev1", channel="ai0", minval=0, maxval=5)
	points.append(np.mean(data))
	
	time.sleep(interval)
	
	
fig = plt.figure(1)
plt.clf()
plt.plot(points, '-x', markersize=2)
plt.grid()
plt.ylabel('Volts / V')
plt.xlabel('Point')
plt.title('Data from DAQ board')
plt.show()