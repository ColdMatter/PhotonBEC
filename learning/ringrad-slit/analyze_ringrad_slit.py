
import sys
sys.path.append("Y:\\Control\\PythonPackages\\")
#sys.path.append("D:\\Control\\PythonPackages\\")

import time, os

import pbec_analysis as pbeca
import hene_utils

ts = '20150210_125025'
centerx, centery = 456, 413
#slit_halfheight = 300
slit_halfwidth = 50

aperture_radius = 250

def apply_slit(im):
	'''
	returns a new image of the image through the slit
	'''
	#im = im[:, :, 0] #red
	return im[:, centerx - slit_halfwidth: centerx + slit_halfwidth, 0] #red
	
def apply_iris(im, black=0):
	ret = im.copy()
	shape = im.shape
	y, x = ogrid[:shape[0], :shape[1]]
	#have a 2x2 grid of the radius squared at that position
	#e.g. r2[4, 5] gives the r^2 at point 4,5
	r2 = (x-centerx)*(x-centerx) + (y-centery)*(y-centery)
	r2mask = r2 <= aperture_radius**2
	ret[~r2mask] = black
	return ret
	
def apply_optics(im):
	return apply_slit(apply_iris(im))
	

if load_data:
	experiment = pbeca.ExperimentalDataSet(ts=ts)
	experiment.dataset['imagelist'] = pbeca.InterferometerFringeData(experiment.ts, '_imagelist.zip')
	experiment.loadAllData()
	images = []
	for im in experiment.dataset['imagelist'].data:
		images.append(im)

	volts = array(experiment.meta.parameters['volts'])

counts = []
for im in images:
	counts.append(sum(apply_optics(im)))
counts = array(counts)
	
figure('pzt voltage vs intensity through slit'), clf()
plot(volts, counts, 'x-')
title('pzt volts vs counts through slit')
xlabel('pzt volts')
ylabel('number of counts through slit')

figure('pzt voltage vs change in intensity through slit'), clf()
delta_counts = 1.0*counts[1:] - counts[:-1]
plot(volts[:-1], delta_counts, 'x-')
xlabel('pzt volts')
ylabel('change in number of counts through slit')

figure('flea images'), clf()
for i in range(0, len(images), 5):
	subplot(4, 5, (i/5)+1)
	imshow(images[i])
	
figure('flea images through aperture')
for i in range(0, len(images), 5):
	subplot(4, 5, (i/5)+1)
	imshow(apply_optics(images[i]), vmax=0.2, vmin=0)
	colorbar()
	
radii = []
for im in images:
	try:
		radius = hene_utils.ring_radius(im, (centery, centerx), (200, 200), channel=0, window_len=4, min_acceptable_radius=30)[0]
	except IndexError:
		radii.append(0)
	else:
		radii.append(radius)
figure('ring radii vs intensity through slit'), clf()
plot(radii, counts, 'x')
grid()
xlabel('ring radius')
ylabel('counts')

'''
figure(3), clf()
im_folder = pbeca.datafolder_from_timestamp(ts) + pbeca.pbec_prefix + '_' + ts + '\\'
for i, im_name in enumerate([o for o in os.listdir(im_folder) if o.endswith('.png')]):
	if i % 10 != 0:
		continue
	print i
	im = imread(im_folder + im_name)
	subplot(4, 5, i/10)
	imshow(im)
'''