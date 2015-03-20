from pylab import *
import sys
#sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("C:\\photonbec\\Control\\PythonPackages\\")

import numpy as np
import scipy.misc
import numpy.fft as fft
from scipy.optimize import leastsq
import cv2
import pbec_analysis as pbeca
from scipy.signal import argrelmax, argrelmin
import matplotlib.pyplot as plt

colour_weights = (1, 1, 0, 0)
plot_graphs = False

def find_freq_from_autocorrelation(t_axis, data,verbose=False):
	#s: signal to be processed; t_axis: times for each data point; assumed ordered
	data = data - np.mean(data)
	data = pbeca.smooth(data, window_len=4)
	ac = np.correlate(data, data, 'same')
	maxima = argrelmax(ac)[0]
	maxima_midplus = [m for m in maxima if m>len(data)/2 - 1]
	if verbose:
		if len(maxima_midplus) < 2: print 'failed finding freq'
	#
	if plot_graphs:
		plt.figure('autocorrelation'), plt.clf()
		plt.plot(t_axis - t_axis[0], ac, 'x-')
		plt.grid()
		plt.legend()
		plt.ylabel("autocorrelation")
		plt.xlabel('piezo volts difference')
	#
	ratio_freq = 1./(t_axis[maxima_midplus[1]] - t_axis[maxima_midplus[0]])
	return ratio_freq, ac

def find_visibility_using_continuous_ft(t_axis, data, f_search_range=0.2, f_search_resolution=0.005):
	#code optional argument to pass frequency without calculating
	#print 'true freq = ' + str(true_freq)
	datasum = np.sum(data)
	realdata = data
	data = data - np.mean(data)
	ratio_freq, ratio_autocor = find_freq_from_autocorrelation(t_axis, data)
	freqs = []
	fts = []
	search_range = ratio_freq * f_search_range
	search_resolution = ratio_freq * f_search_resolution
	for a in np.arange(-search_range, search_range, search_resolution):
		f = ratio_freq + a
		ratio_ft_a = sum(data * np.cos(2*np.pi*f * t_axis))
		ratio_ft_b = sum(data * np.sin(2*np.pi*f * t_axis))
		ratio_ft_c = np.sqrt(ratio_ft_a**2 + ratio_ft_b**2)
		#print 'data ft a=%f b=%f c=%f' % (ratio_ft_a, ratio_ft_b, ratio_ft_c)
		freqs.append(f)
		fts.append(ratio_ft_c)
		
	if plot_graphs:
		plt.figure('fringes'), plt.clf()
		plt.plot(t_axis, realdata, 'x-')
		plt.ylabel('fringe')
		plt.xlabel('piezo volts')
		plt.grid()
		
		plt.figure('continuious fourier transform'), plt.clf()
		plt.plot(freqs, fts, 'x-')
		plt.xlabel('frequency')
		plt.ylabel('ft')

	cont_ft_freq = freqs[np.argmax(fts)]
	#print 'frequency from continuous FT = ' + str(cont_ft_freq)
	#print 'max(fts)=' + str(max(fts)) + ' datasum=' + str(datasum)
	vis_cont_ft = 2*max(fts) / datasum
	#print 'visibility from continuous FT = ' + str(vis_cont_ft)
	return vis_cont_ft


def colour_to_monochrome(im):
	return sum(im*colour_weights, 2) / sum(colour_weights)

def calc_visibility_mm(signal, axis=0):
	#naive calculation
	return (1.0*np.max(signal, axis) - np.min(signal, axis)) / (np.max(signal, axis) + np.min(signal, axis))
	
def rms(x, axis=None):
	return sqrt(np.mean(x**2, axis=axis))

def calc_visibility_rms(signal, axis=0):
	m = np.mean(signal, axis)
	sm = signal - m.reshape(len(signal), 1)
	r = rms(sm, axis)
	return sqrt(2) * r / m

def calc_visibility_fourier(signal,axis=0, f_search_range = 0.04, f_search_resolution = 0.04/40):
	#TODO FIXME. whats wrong? this comment doesn't tell us whats wrong!
	if axis==1:
		visibilities=[]
		posns = arange(0,signal.shape[1])
		for k in range(signal.shape[0]):
			try:
				sig = signal[k, :]
				vis = find_visibility_using_continuous_ft(posns, sig, f_search_range=f_search_range, f_search_resolution=f_search_resolution)
			except IndexError:
				vis=0
			visibilities.append(vis)
	else:
		print "calc_vfisibility_fourier was not built this way round: change the axes!"
		visibilities = [None]
	return visibilities
	
def make_visibility_mm_image(im_arr):
	im_max = np.max(im_arr, 0)
	im_min = np.min(im_arr, 0)
	return (im_max - im_min) / (im_max + im_min)
	
def make_visibility_rms_image(im_arr):
	im_mean = mean(im_arr, 0)
	return sqrt(2) * rms(im_arr - im_mean, 0) / im_mean

def rebin1d(a, binsize):
	cutoff = a.shape[1] % binsize
	if cutoff != 0:
		a = a[:, :-cutoff]
	sh = a.shape[0], a.shape[1]/binsize, binsize
	return mean(a.reshape(sh), -1)
	
def bin_image(im,binning=None):
	if binning == None:
		return im
	else:
		im1 = rebin1d(im, binning[0])
		return rebin1d(im1.transpose(), binning[1]).transpose()
	
		
def crop(im, fromY, toY, fromX, toX):
	return im[fromY:toY, fromX:toX]


def get_overlap_crop(p_im, q_im, x, y):
	fromX = max(0, x)
	fromY = max(0, y)
	toX = min(q_im.shape[1] + x, p_im.shape[1])
	toY = min(q_im.shape[0] + y, p_im.shape[0])
	return fromY, toY, fromX, toX

def image_q_shift(q_im, x, y, a):
	M = np.float32([[1, 0, x], [0, 1, y]])
	dsize = q_im.shape
	#cv2 records the width, height the other way around so swap them
	dsize = list(dsize)
	dsize[0], dsize[1] = dsize[1], dsize[0]
	dsize = tuple(dsize)
	q_im = q_im*a
	q_im_t = cv2.warpAffine(q_im, M, dsize)
	return q_im_t

def find_image_shift(origin_ts):
	oexp = pbeca.ExperimentalDataSet(origin_ts)
	oexp.dataset['block_p_image'] = pbeca.CameraData(oexp.ts, '_block_p_image.png')
	oexp.dataset['block_q_image'] = pbeca.CameraData(oexp.ts, '_block_q_image.png')
	oexp.dataset['block_b_image'] = pbeca.CameraData(oexp.ts, '_block_b_image.png')
	oexp.loadAllData()

	p_im = colour_to_monochrome(oexp.dataset['block_p_image'].data)
	q_im = colour_to_monochrome(oexp.dataset['block_q_image'].data)
	b_im = colour_to_monochrome(oexp.dataset['block_b_image'].data)

	remove_background = False
	if remove_background:
		p_im = p_im - b_im
		q_im = q_im - b_im

	def image_difference(p_im, q_im, x, y, a):
		p = p_im
		q = image_q_shift(q_im, x, y, a)
		fromY, toY, fromX, toX = get_overlap_crop(p_im, q_im, x, y)
		diffim = (p - q)[fromY:toY, fromX:toX]
		return sum(diffim**2)
		#return sum((p_im - q_im_t) / (p_im + q_im_t))
		#return sum(p_im - q_im_t)

	def image_difference_residuals(pars, rp_im, rq_im, pshape, qshape):
		x, y, a = pars
		p_im = reshape(rp_im, pshape)
		q_im = reshape(rq_im, qshape)
		imd = image_difference(p_im, q_im, x, y, a)
		#print 'imd = ' + str(imd) + ' x,y,a = ' + str((x, y, a))
		return array([imd]*5)

	guess = (0, 0, 1)
	lsfit = leastsq(image_difference_residuals, guess, (ravel(p_im), ravel(q_im), p_im.shape, q_im.shape), epsfcn=1.0)
	x, y, a = lsfit[0]
	print 'p to q shift = (%f, %f) amplitude shift = %f' % (x, y, a)
	print 'imgdiff = ' + str(image_difference(p_im, q_im, x, y, a))

	def shiftims(x, y, a):
		figure('shifted image quadratures' + str((x, y))), clf()
		p = p_im
		q = image_q_shift(q_im, x, y, a)
		cr = get_overlap_crop(p_im, q_im, x, y)
		fromY, toY, fromX, toX = cr
		#print 'overlap crop = ' + str(cr)
		added = (p + q)[fromY:toY, fromX:toX]
		diff = (p - q)[fromY:toY, fromX:toX]
		subplot(1, 2, 1)
		imshow(added)
		colorbar()
		title('shift added')
		subplot(1, 2, 2)
		imshow(diff)
		colorbar()
		title('shift subtracted')

	show_debug_graphs = False
	if show_debug_graphs:
		figure('origin image quadratures'), clf()
		subplot(1, 2, 1)
		imshow(p_im)
		title('p im')
		colorbar()
		subplot(1, 2, 2)
		imshow(q_im)
		title('q im')
		colorbar()
		shiftims(*lsfit[0])
		
	return lsfit[0]
	
def gaussian(x, amp, mu, sigma, off):
	return amp*exp(-1.0 * ((x - mu)**2) / (2 * sigma**2)) + off
def gaussian_residuals(pars, xdata, ydata):
	return ( gaussian(xdata, *pars) - ydata )**2	
def lorentzian(x, amp, x0, gam, off):
	return amp * gam**2 / ((x - x0)**2 + gam**2) + off
def lorentzian_residuals(pars, xdata, ydata):
	return ( lorentzian(xdata, *pars) - ydata )**2

def coherence_length_func(xaxis, visibilities, residuals_func = lorentzian_residuals):
	guess = (1, -50, 50, 0) #amp, mu, sigma, off. sigma is width parameter, either for gaussian or lorentzian
	((amp, mu, sigma, off),dump) = leastsq(residuals_func, guess, (xaxis, visibilities))
	return abs(sigma)

def load_data_func(origin_ts, ts_list, binning):
	print 'finding origin'
	shiftx, shifty, ampshift = find_image_shift(origin_ts)
	
	#analyzing all the coarse positions
	###
	
	#sorting by coarse position
	oexperiment_list = [pbeca.ExperimentalDataSet(ts=ts) for ts in ts_list]
	[oexperiment.meta.load() for oexperiment in oexperiment_list]
	oexperiment_list.sort(key = lambda d: d.meta.parameters["coarse_position_meters"])

	print 'loading all data'
	new_oexperiment_list = []
	for i, oexperiment in enumerate(oexperiment_list):
		sys.stdout.write('\rloading ' + str(i+1) + ' out of ' + str(len(oexperiment_list)))
		#must instantiate new dictionary because pointers
		oexperiment.dataset["p_fringes"] = pbeca.InterferometerFringeData(oexperiment.ts, '_p_fringes.zip')
		oexperiment.dataset["q_fringes"] = pbeca.InterferometerFringeData(oexperiment.ts, '_q_fringes.zip')
		oexperiment.loadAllData()
		
		fromY, toY, fromX, toX = get_overlap_crop(oexperiment.dataset["p_fringes"].data[0],
			oexperiment.dataset["q_fringes"].data[0], shiftx, shifty)
		
		oexperiment.dataset['p_fringes'].data = array([
			bin_image(colour_to_monochrome(crop(im, fromY, toY, fromX, toX)),binning=binning)
			for im in oexperiment.dataset['p_fringes'].data])
		oexperiment.dataset['q_fringes'].data = array([
			bin_image(crop(image_q_shift(colour_to_monochrome(im), shiftx, shifty, ampshift), fromY, toY, fromX, toX),binning=binning)
			for im in oexperiment.dataset['q_fringes'].data])
	print '\nconverting to array'

	p_image_data = array([oexperiment.dataset['p_fringes'].data for oexperiment in oexperiment_list])
	q_image_data = array([oexperiment.dataset['q_fringes'].data for oexperiment in oexperiment_list])
	coarse_positions = array([oexperiment.meta.parameters["coarse_position_meters"] for oexperiment in oexperiment_list])
	fine_positions = array(oexperiment_list[0].meta.parameters['fine_position_volts'])
	print 'done, image_data.shape = ' + str(p_image_data.shape)
	#4d array: arctan_data[z_c][z_f][row][col]
	arctan_data = arctan2(q_image_data[:,:,:,:], p_image_data[:,:,:,:])

	return p_image_data, q_image_data, coarse_positions, fine_positions, arctan_data



#EoF
