#coded by JM in 2/2016

import sys
sys.path.append("D:\\Control\\PythonPackages\\")

#load image
#convert to greyscale
#flood fill to find the region of interest
#find the lowest-x boundary for each y, that should be parabola shaped
# can fit it

#calibrate the energy scale
#for each y in parabola fit the temperature

#note that all the parabolas are sideways, x = ay^2 + by + c
# so prepare to be slightly confused at all the x/y swapping compared to the parabolas you studied at school
# possibly a useful refactoring would be to rename everything in terms of energy and momentum, since y == momentum, x == energy

import pbec_analysis as pbeca

import scipy.misc
from scipy.optimize import leastsq
import Queue
import numpy as np
import matplotlib.mlab as ml

from scipy import constants
kB = constants.Boltzmann
hbar = constants.hbar

colour_weights = (1, 1, 0, 0) #red, green
##floodfill_boundary_threshold = 40 #this could be deduced by taking the average of a dark part of the image

#from data first_ts, last_ts = "20160217_174755", "20160217_175533"
default_calibration_2d = {'lam0': 597.2e-9, 'grad_lam':-120e-9, 'p0':-5.4e-29, 'grad_p':6.65e30}

def pixel_to_wavelength_momentum(pixelX, pixelY, calibration_2d=default_calibration_2d):
	wavelength = pixelX / calibration_2d['grad_lam'] + calibration_2d['lam0']
	momentum = pixelY / calibration_2d['grad_p'] + calibration_2d['p0']
	return (wavelength, momentum)

def colour_mask_image(im_raw, colour_weights=colour_weights):
	'''
	turns an image with three channels into a greyscale image
	'''
	return sum([colour_weights[j]*im_raw[:,:,j] for j in range(im_raw.shape[-1])], 0)

def find_max_pixel(im):
	maxRow = 0
	maxCol = 0
	for r in range(len(im)):
		col = np.argmax(im[r])
		if im[r, col] > im[maxRow, maxCol]:
			maxCol = col
			maxRow = r
	return maxRow, maxCol

#floodfill algorithm with special requirements
# for instance also finds the max and min rows that were filled in
#flood fills pixels with zero until it reaches a boundary
#returns the boundaries in y that the flood fill reached which gives the range of the parabola
def floodfill(im, startP, borderThreshold, debug):
	minFilledRow = im.shape[0]
	maxFilledRow = 0
	areaFound = 0
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
			areaFound += 1
			
			if px[0] > 0:
				pxqueue.put((px[0] - 1, px[1]))
			if px[1] > 0:
				pxqueue.put((px[0], px[1] - 1))
			if px[0]+1 < im.shape[0]:
				pxqueue.put((px[0] + 1, px[1]))
			if px[1]+1 < im.shape[1]:
				pxqueue.put((px[0], px[1] + 1))
			
	if debug:
		print 'floodfill area found = ' + str(areaFound)
	return minFilledRow+1, maxFilledRow, areaFound
	
#given a y value, find the x of the parabola
#valid only in the range of y returned by floodfill()
def find_parabola_y_from_x(mask_im, y, min_parabola_thickness=4, scan_from_left=True):
	#not the fastest algo in the world
	#using find() is probably better
	#min_parabola_thickness#required to not be thrown off by hot pixels
	x_range = range(mask_im.shape[1])
	if not scan_from_left:
		x_range = x_range[::-1]
	for x in x_range:
		if all(mask_im[y, x : x+min_parabola_thickness] == 0):
			return x
	if min_parabola_thickness == 1:
		raise ValueError('no parabola here')
	else:
		return find_parabola_y_from_x(mask_im, y, min_parabola_thickness-1, scan_from_left)

def find_data_area_bounds(im_raw, floodfill_boundary_threshold=40, debug=False):
	im = colour_mask_image(im_raw, colour_weights)
	if debug:
		figure('im-greyscale'),clf()
		subplot(1, 2, 1)
		title('colour image')
		imshow(im_raw)
		subplot(1, 2, 2)
		title('greyscale image')
		imshow(im)

	masked_im = im.copy()#.transpose()
	while 1:
		maxRow, maxCol = find_max_pixel(masked_im)
		if masked_im[maxRow, maxCol] <= floodfill_boundary_threshold:
			raise ValueError('max pixel too dim (' + str(masked_im[maxRow, maxCol]) + '), position=(' + str(maxCol)
				+ ', ' + str(maxRow) + '), unable to floodfill, dying..')
		minFilledRow, maxFilledRow, areaFound = floodfill(masked_im, (maxRow, maxCol), borderThreshold=floodfill_boundary_threshold, debug=debug)
		if areaFound > 10000: #magic number 100 so that we keep flood filling until a really large area is found instead of just hot pixels
			break
	minFilledRow += 10 #shift these a few pixels so our algorithm doesnt fail at the weird edges
	maxFilledRow -= 10
			
	if debug:
		figure('masked_im'),clf()
		title('masked image found by floodfill')
		imshow(masked_im)
		plot([0, masked_im.shape[1]], [minFilledRow, minFilledRow], 'r-', label='minimum y value') 
		plot([0, masked_im.shape[1]], [maxFilledRow, maxFilledRow], 'g-', label='maximum y value')
		legend()
		title('2d spectrum image after floodfill has found the area with all the data')
	return masked_im, minFilledRow, maxFilledRow
	
def fit_parabola_given_area_bounds(masked_im, minFilledRow, maxFilledRow, debug=False, scan_from_left=True):
	parabola_row_size = maxFilledRow - minFilledRow
	parabola_x = np.zeros(parabola_row_size)
	parabola_y = np.arange(parabola_row_size)
	for y in parabola_y:
		parabola_x[y] = find_parabola_y_from_x(masked_im, y + minFilledRow, scan_from_left=scan_from_left)
	parabola_y += minFilledRow

	polynomial_order = 2
	ls_solution = np.polyfit(parabola_y, parabola_x, polynomial_order)
	ls_solution = [ls_solution]
	#print 'fit paras = ' + str(ls_solution[0])
	
	#this code fits the parabola only at the bottom, where it is very close to a parabola instead of some other shape further out
	if polynomial_order == 2: #if playing around with other orders, dont do this
		y_minimum_value = -ls_solution[0][1] / 2 / ls_solution[0][0]
		y_minimum_index = ml.find(parabola_y > y_minimum_value)[0]
		#say that the parabolic linear region is a third of the entire range, i.e. 1/6 either side
		char_length = (maxFilledRow - minFilledRow) / 6 #characteristic length
		center_parabola_y = parabola_y[y_minimum_index - char_length : y_minimum_index + char_length]
		center_parabola_x = parabola_x[y_minimum_index - char_length : y_minimum_index + char_length]
		ls_solution = np.polyfit(center_parabola_y, center_parabola_x, polynomial_order)
		ls_solution = [ls_solution]
		#print 'fit paras = ' + str(ls_solution[0])
		
	if debug:
		figure('found parabola'), clf()
		plot(parabola_y, parabola_x, label='data')
		#ls_solution = [(8.28e-4, -1.136, 1026)]
		#plot(parabola_y, parabola(parabola_y, ls_solution[0]), label='fit')
		used_y_axis = parabola_y
		if polynomial_order == 2:
			used_y_axis = center_parabola_y
		plot(used_y_axis, np.polyval(ls_solution[0], used_y_axis), label='fit')
		xlabel('y axis on image (momentum)')
		ylabel('x axis on image (energy)')
		legend(loc='upper center')
		title('parabola boundary fitted')
		
		figure('parabola on image'),clf()
		imshow(im_raw)
		plot(polyval(ls_solution[0], used_y_axis), used_y_axis, 'g-', label='fit')
		title('parabola fit drawn on 2d spectrum')

	#return fit_a, fit_b, fit_c 
	return ls_solution[0]

	
def fit_2dparabola(im_raw, debug=False):
	masked_im, minFilledRow, maxFilledRow = find_data_area_bounds(im_raw, debug)
	return fit_parabola_given_area_bounds(masked_im, minFilledRow, maxFilledRow, debug)

def calc_parabola_vertex(masked_im, fit_a, fit_b, fit_c, scan_from_left=True):
	xm = -fit_b/2/fit_a
	ym = find_parabola_y_from_x(masked_im, int(xm), scan_from_left=scan_from_left) #the desired value for calibrating the wavelength scale
	return xm, ym

#--------------------
#TOOLS ADDED 25/3/16 by RAN. Some redundancy, but never mind
def calib_spec_2D(spec_2D, grad_p=6.705e29, p0=-1.722e32, grad_e=-7.84e22, e0=3.544e-19, grad_lam = 4.458e01, lam0 = 5.589e02):
	mom_indices = np.arange(spec_2D.shape[0])
	lamb_indices= np.arange(spec_2D.shape[1])

	mom = (mom_indices/grad_p) + p0 #clearly miscalibrated. Check again
	lamb = (lamb_indices/grad_lam) + lam0 #seems about correct.
	return mom, lamb

def mirrorTransmissionCorrect2DSpec(spec_2D,**kwargs):
	mom,lamb_2D = calib_spec_2D(spec_2D,**kwargs)
	transmissions_2D=pbeca.LaserOptikMirrorTransmission(lamb_2D)
	correction_factor,dump = np.meshgrid(transmissions_2D,mom)
	return spec_2D / correction_factor

#EoF