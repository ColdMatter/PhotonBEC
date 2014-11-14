#coded by JM in 10/2014

import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import scipy.misc
from scipy.optimize import leastsq
import numpy as np

import pbec_analysis

#TODO this queue is made for use of threads, it has mutex stuff inside
# which will make it slow, replace it with a faster alternative
import Queue


#choose border threshold to get most of the parabola but not
# at the expense of speed
floodfill_boundary_threshold = 60

colour_weights = (1, 1, 0, 0) #red, green
smooth_window_len = 10
smooth_window_name = 'flat'


#now all the parabolas are sideways, x = ay^2 + by + c
# so prepare to be slightly confused at all the x/y swapping from
# the parabolas you studied in maths class

#given a y value, find the x of the parabola
def parabola_y_to_x(im, y, mask_im):
	while 1:
		mx = np.argmax(im[y])
		if mask_im[y, mx] == 0: #hot pixel, not in floodfill range
			break
			#darken the pixel and keep looking
		else:
			im[y, mx] = 0
	return mx

def obtain_parabola_from_image(im, mask_im, parabola_row_offset, parabola_row_size):
	xdata = np.zeros(parabola_row_size)
	for y in range(parabola_row_size):
		xdata[y] = parabola_y_to_x(im, y + parabola_row_offset, mask_im)
	return xdata
	
def construct_parabola_from_parameters((a, b, c), parabola_row_size):
	calc_data = np.zeros(parabola_row_size)
	for y in range(parabola_row_size):
		calc_data[y] = a*y*y + b*y + c
	return calc_data
	
def parabola_residuals(pars, xdata, parabola_row_size):
	calc_data = construct_parabola_from_parameters(pars, parabola_row_size)
	return ( xdata -  calc_data )**2
	
def colour_mask_image(im_raw, colour_weights):
	return sum([colour_weights[j]*im_raw[:,:,j] for j in range(im_raw.shape[-1])], 0)


def find_max_pixel(im):
	maxRow = 0
	maxCol = 0
	for r in range(len(im)):
		col = argmax(im[r])
		if im[r, col] > im[maxRow, maxCol]:
			maxCol = col
			maxRow = r
	return maxRow, maxCol
	

#floodfill algorithm with special requirements
# for instance also finds the max and min rows that were filled in
def floodfill(im, startP, borderThreshold):
	minFilledRow = im.shape[0]
	maxFilledRow = 0
	pxqueue = Queue.Queue()
	pxqueue.put(startP)
	while not pxqueue.empty():
		px = pxqueue.get()
		if px[0] > maxFilledRow:
			maxFilledRow = px[0]
		if px[0] < minFilledRow:
			minFilledRow = px[0]
		if im[px[0], px[1]] > borderThreshold:
			im[px[0], px[1]] = 0
			pxqueue.put((px[0] + 1, px[1]))
			pxqueue.put((px[0] - 1, px[1]))
			pxqueue.put((px[0], px[1] + 1))
			pxqueue.put((px[0], px[1] - 1))
	return minFilledRow+1, maxFilledRow

def fit_parabola(im_raw, plotfit=False):
	#im_raw = scipy.misc.imread("pbec_20141029_161004_20um_slit.png")
	#im = im_raw[:,:,im_channel]
	im = colour_mask_image(im_raw, colour_weights)

	maxRow, maxCol = find_max_pixel(im)
	masked_im = im.copy()
	parabola_row_range = floodfill(masked_im, (maxRow, maxCol), borderThreshold=floodfill_boundary_threshold)

	parabola_row_offset = parabola_row_range[0]
	parabola_row_size = parabola_row_range[1] - parabola_row_range[0]
	xdata = obtain_parabola_from_image(im, masked_im, parabola_row_offset, parabola_row_size)
	
	#near the stationary point of the parabola there are lots of bright pixels
	# this can mess up the calculation for parabola_row_range from floodfill()
	# so to find the real range of the parabola, find the very large spike in
	# the derivative of xdata
	dxdata = np.zeros(parabola_row_size - 1)
	large_delta = []
	for i in range(parabola_row_size - 1):
		dxdata[i] = xdata[i] - xdata[i + 1]
		#threshold for too-large change is chosen to be 100
		if abs(xdata[i] - xdata[i + 1]) > 100:
			large_delta.append(i)
	if len(large_delta) > 0:
		large_delta = np.array(large_delta)
		top_deltas = large_delta[large_delta < maxRow - parabola_row_offset]
		bottom_deltas = large_delta[large_delta > maxRow - parabola_row_offset]
		print 'td = ' + str(top_deltas) + ' bd = ' + str(bottom_deltas)
		
		parabola_row_offset = top_deltas[-1] + 1 + parabola_row_range[0]
		parabola_row_size = bottom_deltas[0] - top_deltas[-1] - 1
		xdata = xdata[top_deltas[-1] + 1:bottom_deltas[0]]
	else:
		print 'skipping overexpose fix'
	
	if plotfit:
		figure(1), clf()
		plot(xdata)
		figure(2), clf()
		plot(xdata, np.array(range(parabola_row_size)) + parabola_row_offset, "y")
		imshow(im)
		scatter([maxCol], [maxRow], c='w', marker='x')
	
	parameters_guess = (-0.01, 6.0, 1600.0) #(a, b, c)
	ls_solution = leastsq(parabola_residuals, parameters_guess, args = (xdata, parabola_row_size))

	(a, b, c) = ls_solution[0]
	#print a, b, c
	
	if plotfit:
		calc_data = construct_parabola_from_parameters(ls_solution[0], parabola_row_size)
		plot(calc_data, np.array(range(parabola_row_size)) + parabola_row_offset, "w")
	
	ym = -b/2/a + parabola_row_offset #y value of minimum
	xm = parabola_y_to_x(im, int(ym), masked_im) #x value of minimum, the desired value for calibrating the wavelength scale
	return xm, ls_solution[0]
	
	

arg1 = "20141029_161004", "_20um_slit.png"
arg2 = "20141030_165700", ".png"
arg3 = "20141110_123639", ".png"
im_raw = scipy.misc.imread(pbec_analysis.timestamp_to_filename(*arg2))
print fit_parabola(im_raw, True)




#print (maxRow, maxCol, im[maxRow, maxCol])

#print "parabola row range = " + str(parabola_row_range)
#ImageDraw.floodfill(im, (maxRow, maxCol), 0, border)
#cant use ImageDraw.floodfill() because it assumes the border is an individual color
# while we need to use a threshold system, i.e. filling all colors above a certain value

#the idea if using histogram() to discover the correct threshold for floodfill is a bad
# idea because it will still depend on some arbitrary human decision in the proportional cutoff
#fact is the images you take will depend on many things: experimental setup, camera settings and more
# so a human will have to choose the threshold at some point
'''
import matplotlib.pyplot as plt
#n, bins, patches = plt.hist(im.flatten(), im[maxRow, maxCol], fc='k', ec='k', log=True)
np.histogram(im.flatten(), 
print n
print bins
'''


'''
from pbec_experiment import *
import time
cam = getCameraByLabel('grasshopper')

try:
	for i in range(1):
		im_raw = cam.get_image()
		if im_raw == None:
			print('error')
			time.sleep(0.1)
			continue
		ts = pbec_analysis.make_timestamp()
		imsave(pbec_analysis.timestamp_to_filename(ts, file_end=".png"), im_raw)
		
		xm, parabola = fit_parabola(im_raw, True)
		print xm
		#figure(str(i) + " xm=" + str(xm))
		#imshow(colour_mask_image(im_raw, colour_weights))
		#calc_data = construct_parabola_from_parameters(parabola)
		#plot(calc_data, np.array(range(parabola_row_range[1] - parabola_row_range[0])) + parabola_row_range[0], "w")
		
		time.sleep(1.5)
finally:
	cam.close()
'''