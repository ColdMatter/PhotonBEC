
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

from numpy import array, unravel_index

from time import sleep

def get_autoexposed_spectrum(spectrometer, int_time, acquire_time_floor=150, min_int_time=1, max_int_time=3000, \
	max_iter=14, min_acceptable_value = 2000, max_acceptable_value=60000, int_time_factor=2, verbose = False):
	
	#Set up the loop
	count = 0
	maxval = 0
	while (count < max_iter) & ((maxval < min_acceptable_value) or (maxval > max_acceptable_value)):
		count += 1
		nAverage = 1 if int_time >= acquire_time_floor else int(acquire_time_floor / int_time)
		if verbose: 
			print "setting int_time and nAverage to "+str((int_time, nAverage))
		spectrometer.setup()
		spectrometer.start_measure(int_time, nAverage)
		spec = spectrometer.get_data()
		spectrometer.close()
		res = {"int_time": int_time, 'nAverage': nAverage, "maxval": maxval, "Niter": count}
				
		maxval = max(spec)
		if verbose: print "maxval = "+str(maxval)
		if maxval > max_acceptable_value:
			int_time = int_time / int_time_factor
			if int_time < min_int_time:
				int_time = min_int_time
				if verbose: print "Can't go lower!"
				break
		elif maxval < min_acceptable_value:
			int_time = int_time * int_time_factor
			if int_time > max_int_time:
				int_time = max_int_time
				if verbose: print "Can't go higher!"
				break
				
	return spec, res

if __name__=="__main__":
	#im, res = get_single_autoexposed_image("chameleon", shutter=2, gain=24, binning = [4,4], verbose=True)
	im, res = get_single_autoexposed_image("grasshopper_2d", shutter=64, gain=0, binning = [4,4], verbose = True)
	figure(1); clf(); imshow(im)



#EoF