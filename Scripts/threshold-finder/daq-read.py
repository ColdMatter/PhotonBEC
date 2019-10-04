
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import SingleChannelAI
import time
import numpy as np

vl = []
for i in range(240):
	v = np.mean(SingleChannelAI.SingleChannelAI(Npts=2,rate=1.0e4,device="Dev1",channel="ai0",minval=0,maxval=1.0))
	print str(i) + '\t' + str(v)
	vl.append(v)
	time.sleep(0.3)
	
plot(vl, 'x-')