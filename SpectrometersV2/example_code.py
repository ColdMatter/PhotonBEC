import sys
from socket import gethostname
if gethostname().lower() == "ph-photonbec5":
	sys.path.append("D:/Control/PythonPackages/")	
import pbec_ipc
from time import sleep
from time import time
import matplotlib.pyplot as plt

from single_spec_IPC_module import set_spectrometer_mode, set_spectrometer_integration_time, set_spectrometer_n_averages, get_spectrum_measure

########## Control Parameters
spectrometer_server_port = pbec_ipc.PORT_NUMBERS["spectrometer_server V2"]
spectrometer_server_host = 'localhost'


'''
##### Sets the spectrometer mode to either "continuous" or "internal". All data should be acquiered in internal mode. However, the function that...
##### ...gets the data, overrides the mode to "internal" if this is not the case already
set_spectrometer_mode(mode='internal', port=spectrometer_server_port, host=spectrometer_server_host)
'''


'''
##### Sets spectrometer integration time and number of averages
set_spectrometer_integration_time(int_time=50, port=spectrometer_server_port, host=spectrometer_server_host)
set_spectrometer_n_averages(n_averages=1, port=spectrometer_server_port, host=spectrometer_server_host)
'''


##### Grabs some data


spectrum_time_label, spectrum_new_data_flag, lamb, spectrum = get_spectrum_measure(int_time=1000, n_averages=1, n_measures=5, port=spectrometer_server_port, host=spectrometer_server_host)

plt.plot(lamb, spectrum)
plt.yscale('log')
plt.xlabel("Wavelength (nm)", fontsize=9)
plt.ylabel("Spectrum", fontsize=9)
plt.xlim(560, 600)
plt.ylim(1, 40000)
plt.show()