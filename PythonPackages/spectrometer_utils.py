
import pbec_analysis as pbeca
import numpy as np
import matplotlib.mlab as ml

def get_lambda_range(lamb, fromL, toL):
	assert(fromL <= toL)
	assert(fromL >= lamb[0])
	assert(toL <= lamb[-1])
	hi = 0 #this is a crap way of doing it but this function
	lo = 0 # isnt a bottleneck so the speed hit doesnt matter
	for i, v in enumerate(lamb):
		if v > fromL:
			lo = i
			break
	for i, v in enumerate(lamb):
		if v > toL:
			hi = i
			break
	return (hi, lo)
	#return (
	#	int( (fromL - lamb[0]) * len(lamb) / (lamb[-1] - lamb[0]) ),
	#	int( (toL - lamb[0]) * len(lamb) / (lamb[-1] - lamb[0]) )
	#	)

def get_background(lamb, spectrum, data_lamb_range=(530, 630)):
	spec_data_range = pbeca.getLambdaRange(lamb, *data_lamb_range)
	spectrum_no_data = list(spectrum[:spec_data_range[0]]) + list(spectrum[spec_data_range[1]:])
	background = np.mean(spectrum_no_data)
	noise_stddev = np.std(spectrum_no_data)
	return background, noise_stddev

def find_spectrum_cutoff(lamb, spectrum, data_lamb_range=(530, 630), spectrometer_resolution_pixels=3):
	####spectrometer_resolution_pixels = 3 #about 0.35nm
	background, noise_stddev = get_background(lamb, spectrum)
	spectrum_less_background = spectrum - background
	
	if max(spectrum_less_background) > noise_stddev*20:
		#find lambda0 with threshold being a fraction of peak value
		threshold = max(spectrum_less_background) / 15
		very_noisey=False
	else:
		#find lambda0 with threshold being a multiple of std dev
		threshold = noise_stddev*2
		#these magic numbers should be 3 * 15 = 20 so the two possible method
		# have a continuous crossover when going from one function to the other
		very_noisey=True
		
	spec_data_range = pbeca.getLambdaRange(lamb, *data_lamb_range)
	try:
		argmax_of_data_range = spec_data_range[0] + np.argmax(spectrum_less_background[spec_data_range[0]:spec_data_range[1]])
		spectrum_after_peak = spectrum_less_background[argmax_of_data_range:spec_data_range[1]]
		lambda_upper_bound_index = ml.find(spectrum_after_peak < threshold)[0] + argmax_of_data_range
		lambda_upper_bound = lamb[lambda_upper_bound_index]
				
		lambda_0_index = lambda_upper_bound_index - spectrometer_resolution_pixels
		lambda_ground_state_lower_bound_index = lambda_upper_bound_index - spectrometer_resolution_pixels*2
		lambda_0 = lamb[lambda_0_index]
		lambda_ground_state_lower_bound = lamb[lambda_ground_state_lower_bound_index]
	except IndexError:
		lambda_0 = 589
		lambda_upper_bound = 600 # try, else added by BTW 20161129
		
	#lambda_upper_bound is the low-value after the peak
	#lambda_0 is the peak
	#lambda_ground_state_lower_bound is the upper bound if you wanted to integrate over the ground state
	return lambda_upper_bound, lambda_0