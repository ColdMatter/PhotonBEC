
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import pbec_experiment as pbece
import pbec_analysis as pbeca

import pbec_ipc
import spectrum_autoexposure

powers = [400, 800, 1500, 1550, 1600, 1650, 1700, 1750, 1800, 2000, 2200]
#powers = [800, 1400, 1800]
spectrometer = pbece.Spectrometer()

tses = []
for p in powers:
	ts = pbeca.make_timestamp()
	print 'taking data ' + ts
	tses.append(ts)
	experiment = pbeca.ExperimentalDataSet(ts=ts)
	
	print 'setting power to ' + str(p) + 'mW'
	pbec_ipc.ipc_eval('guiSetPowerAndWait(' + str(p) + ')', 'laser_controller')
	spec, res = spectrum_autoexposure.get_autoexposed_spectrum(spectrometer, 100,
		acquire_time_floor=1250, verbose=True)
	
	experiment = pbeca.ExperimentalDataSet(ts=ts)
	experiment.meta.parameters['power_mw'] = p
	for key, value in res.iteritems():
		if key != 'lamb':
			experiment.meta.parameters[key] = value
	experiment.dataset['spectrum'] = pbeca.SpectrometerData(experiment.ts)
	experiment.dataset['spectrum'].lamb = res['lamb']
	experiment.dataset['spectrum'].spectrum = spec
	experiment.saveAllData()
	
print('first_ts, last_ts = "' + str(tses[0]) + '", "' + str(tses[-1]) + '"')