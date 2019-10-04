import sys, json

import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) == 1:
	print 'drag a data-acquisiion json data file to display'
	raw_input('press any key to continue . . .')

#daq_data['data']
#daq_data['ts']
#daq_data['rate_s_per_sec']

fig = plt.figure('display-json-daq')
plt.clf()
for i, daq_path in enumerate(sys.argv[1:]):
	daq_fd = open(daq_path, 'r')
	daq_data = json.load(daq_fd)
	daq_fd.close()

	plt.subplot(len(sys.argv)-1, 1, i+1)
	plt.title(daq_data['ts'])
	xaxis = np.arange(len(daq_data['data']))/daq_data['rate_s_per_sec']
	plt.plot(xaxis, daq_data['data'], '-')
	plt.grid(1)
	plt.ylabel("Reading / V")
	
plt.xlabel("Time / s")
plt.show()