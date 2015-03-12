from __future__ import division
import numpy as np
import pbec_analysis as pbeca
from scipy.signal import argrelmax, argrelmin
import matplotlib.pyplot as plt

plot_graphs = False

def find_freq_from_autocorrelation(t_axis, data):
	#s: signal to be processed; t_axis: times for each data point; assumed ordered
	data = data - np.mean(data)
	data = pbeca.smooth(data, window_len=4)
	ac = np.correlate(data, data, 'same')
	maxima = argrelmax(ac)[0]
	maxima_midplus = [m for m in maxima if m>len(data)/2 - 1]
	print maxima_midplus
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
	print ratio_freq
	#print 'freq from autocorrelation = ' + str(ratio_freq)
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
