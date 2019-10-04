
import sys
sys.path.append("Y:\\Control\\PythonPackages\\")

#import pbec_analysis as pbeca

first_ts,last_ts = "20141127_150253", "20141127_150357"
image_crop = (40, 67, 35, 62) #row_start, row_end, col_start, col_end

colour_weights = (1, 1, 0, 0)

import numpy as np
import scipy.misc

def gaussian(x, y, cx, cy, s):
	return np.exp(-1.0 * ((x-cx)**2 + (y-cy)**2) / s**2 )

def create_gaussian_image(cx, cy, s, shape, color):
	color = array(color)
	im = zeros(shape)
	for r in range(shape[0]):
		for c in range(shape[1]):
			im[r][c] = color*gaussian(r, c, cx, cy, s)
	return im

'''
	create_gaussian_image(10, 7, 3, (30, 50, 3), (255, 0, 0)),
	create_gaussian_image(20, 40, 5, (30, 50, 3), (127, 127, 0)),
	create_gaussian_image(15, 30, 4, (30, 50, 3), (0, 0, 255))
'''
'''
shape = 400, 500, 3
im_list = [
	create_gaussian_image(100, 100, 50, shape, (255, 0, 0)),
	create_gaussian_image(200, 250, 150, shape, (127, 127, 0)),
	create_gaussian_image(150, 450, 70, shape, (0, 0, 255))
	]
'''

shape = 400, 500
im_list = [
	create_gaussian_image(100, 100, 400, shape, 1),
	create_gaussian_image(200, 250, 450, shape, 1),
	create_gaussian_image(150, 450, 480, shape, 1)
	]

im_list = array(im_list)
	
figure(1), clf()
for i, im in enumerate(im_list):
	subplot(1, 3, i+1)
	imshow(im)
colorbar()

def mean_image(im_list):
	im_mean = zeros_like(im_list[0])
	for im in im_list:
		for r in range(im.shape[0]):
			for c in range(im.shape[1]):
				im_mean[r][c] += im[r][c] / len(im_list)
	return im_mean
	
#im_mean = mean_image(im_list)
#figure(2), clf()
#imshow(im_mean)
#colorbar()

figure(3), clf()
imshow(mean(im_list, 0))
colorbar()

def m_image(im_list, fun=max):
	im_m = im_list[0].copy()
	for im in im_list:
		for r in range(im.shape[0]):
			for c in range(im.shape[1]):
				im_m[r][c] = fun(im_m[r][c], im[r][c])
	return im_m


figure(4), clf()
subplot(1, 2, 1)
im_max = m_image(im_list, max)
imshow(im_max)
subplot(1, 2, 2)
im_min = m_image(im_list, min)
imshow(im_min)
colorbar()

figure(5), clf()
subplot(1, 2, 1)
im_max = np.max(im_list, 0)
imshow(im_max)
subplot(1, 2, 2)
im_min = np.min(im_list, 0)
imshow(im_min)
colorbar()


	
def calc_visibility_mm(signal):
	#naive calculation
	return (1.0*max(signal) - min(signal)) / (max(signal) + min(signal))
	
def rms(x, axis=None):
	return sqrt(mean(x**2, axis=axis))

def calc_visibility_rms(signal):
	m = mean(signal)
	return sqrt(2) * rms(signal - m) / (m)
	
calc_visibility = calc_visibility_mm

def make_visibility_im(im_arr):
	pass