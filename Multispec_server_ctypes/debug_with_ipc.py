import sys
from socket import gethostname
if gethostname()=="ph-photonbec3":
	sys.path.append("D:\\Control\\PythonPackages\\")

import pbec_ipc

host = "localhost"
port = 47907 #hard coded for now  

#pbec_ipc.ipc_eval("s.thread.paused",port,host)

import pbec_analysis
import time

data_list = []
for i in range(1):
	time.sleep(0.03)
	spectrum = pbec_ipc.ipc_get_array("s.spectros[1].spectrum",port,host)
	remote_ts = pbec_ipc.ipc_eval("s.spectros[0].ts",port,host)
	local_ts = pbec_analysis.make_timestamp(3)
	bec_counts = sum(spectrum[642:648])
	data_list.append((local_ts,remote_ts,bec_counts))

bec_fluctuations = [d[2] for d in data_list]
plot(bec_fluctuations)