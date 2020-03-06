import sys
from socket import gethostname
if gethostname().lower() == "ph-photonbec5":
	sys.path.append("D:/Control/PythonPackages/")	
import pbec_ipc
from time import sleep
from time import time
import matplotlib.pyplot as plt




def get_spectrometer_integration_time(port, host):
	return float(pbec_ipc.ipc_eval("getSpectrometerIntegrationTime()", port=port, host=host))



def get_spectrometer_n_averages(port, host):
	return float(pbec_ipc.ipc_eval("getSpectrometerNAverages()", port=port, host=host))


def set_spectrometer_mode(port, host, mode='continuous'):
	if mode == 'continuous' or mode == 'internal':
		call_str = r'set_spectrometer_mode("'+mode+'")'
		print(call_str)
		pbec_ipc.ipc_exec(call_str, port=port, host=host)
	else:
		raise Exception("***Unknown spectrometer mode***")



def set_spectrometer_integration_time(port, host, int_time=100):
	pbec_ipc.ipc_exec("setSpectrometerIntegrationTime("+str(int_time)+")", port=port, host=host)



def set_spectrometer_n_averages(port, host, n_averages=25):
	pbec_ipc.ipc_exec("setSpectrometerNAverages("+str(n_averages)+")", port=port, host=host)



def set_spectrometer_external_trigger(port, host, external_trigger):
	pbec_ipc.ipc_exec("setSpectrometerExternalTrigger("+str(external_trigger)+")", port=port, host=host)
	


def get_spectrum_measure(port, host, int_time=10, n_averages=1, n_measures=1):
	if not n_measures >=1:
		raise Exception("*** Error: Invalid number of measures ***")
	pbec_ipc.ipc_exec("get_single_spectrum("+str(int_time)+','+str(n_averages)+','+str(n_measures)+')', port=port, host=host)
	spectrum_time_label = pbec_ipc.ipc_get_array("s.spectro.spectrum_time_label", port=port, host=host)
	spectrum_new_data_flag = pbec_ipc.ipc_get_array("s.spectro.spectrum_new_data_flag", port=port, host=host)
	lamb = pbec_ipc.ipc_get_array("s.spectro.lamb", port=port, host=host)
	spectrum = pbec_ipc.ipc_get_array("s.spectro.spectrum", port=port, host=host)
	return spectrum_time_label, spectrum_new_data_flag, lamb, spectrum



