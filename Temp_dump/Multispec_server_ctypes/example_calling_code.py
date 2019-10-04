#Adapted from experiment 20180608_fast_threshold.
#NOT desiogned to stand alone

spectrometer_server_port = pbec_ipc.PORT_NUMBERS["spectrometer_server"]
spectrometer_server_host = 'localhost'
spectrometer_numbers = {'newbie':1,'grey':2,'black':0}
spec_name = 'grey'
spec_number = spectrometer_numbers[spec_name]

def get_spectrum_by_name(name = 'grey'):
	spectrometer_number = spectrometer_numbers[name]
	dump = pbec_ipc.ipc_exec("s.spectros["+str(spectrometer_number)+"].get_data()",port=spectrometer_server_port,host=spectrometer_server_host)
	temp_spectrum = pbec_ipc.ipc_get_array("s.spectros["+str(spectrometer_number)+"].spectrum",port=spectrometer_server_port,host=spectrometer_server_host)
	temp_lam = pbec_ipc.ipc_get_array("s.spectros["+str(spectrometer_number)+"].lamb",port=spectrometer_server_port,host=spectrometer_server_host)
	spectrum_ts = pbec_ipc.ipc_eval("s.spectros["+str(spectrometer_number)+"].ts",port=spectrometer_server_port,host=spectrometer_server_host)
	spectrum_int_time = pbec_ipc.ipc_eval("s.spec_int_times["+str(spectrometer_number)+"]",port=spectrometer_server_port,host=spectrometer_server_host)
	spectrum_n_averages = pbec_ipc.ipc_eval("s.spec_n_averages["+str(spectrometer_number)+"]",port=spectrometer_server_port,host=spectrometer_server_host)
	return temp_lam, temp_spectrum, spectrum_ts, float(spectrum_int_time), float(spectrum_n_averages)

def set_SpecIntTime(time,spec_number):
	pbec_ipc.ipc_eval("setSpectrometerIntegrationTime("+str(time)+","+str(spec_number)+")",host=spectrometer_server_host,port=spectrometer_server_port)
def set_SpecNAverages(n,spec_number):
	pbec_ipc.ipc_eval("setSpectrometerNAverages("+str(n)+","+str(spec_number)+")",host=spectrometer_server_host,port=spectrometer_server_port)
