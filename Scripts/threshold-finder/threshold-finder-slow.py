import sys
sys.path.append("D:\\Control\\PythonPackages\\")

from time import sleep
import scipy.misc
import numpy as np
from scipy.optimize import leastsq

import pbec_experiment as pbece
import pbec_analysis as pbeca
import pbec_ipc
from analyse_images import fit_gaussian_to_image
import autoexposure

def logB(A, base):
	return log(A) / log(base)
def my_logspace(start, end, step, base=10): #numpy.logspace is coded in a way not helpful to us
	return logspace(logB(start, base), logB(end, base), step, base=base)

cavity_center = (456, 723) #None #for auto finding
p_large_range = my_logspace(100, 2200, 16)
p_small_range_rel = linspace(-0.3, 0.3, 9)

camera_label = 'chameleon'
colour_weights = (1, 1, 1)
debug_graphs = False
bec_region_radius = 35e-6 * 4 / pbece.camera_pixel_size_map[camera_label]
 #size of bec ~35um, magnification 4
print 'bec region radius = ' + str(bec_region_radius) + 'px'

def cam_get_image(cam, max_attempts=5):
	im = None
	for i in range(max_attempts):
		im = cam.get_image() #untriggered
		if im != None:
			break
	return im

def colour_to_monochrome(im):
	return sum(im*colour_weights, 2) / sum(colour_weights)
	
def take_power_ground_state_data(power_range, imshape):
	w = arange(imshape[1])
	h = arange(imshape[0])
	ww, hh = meshgrid(w, h)
	dist_im = sqrt((cavity_center[1] - ww)**2 + (cavity_center[0] - hh)**2)
	image_apature = dist_im < bec_region_radius

	print 'taking background'
	SingleChannelAO.SetAO0(1.05)
	
	ims = []
	p0i = []
	for power_mW in power_range:
		print 'setting power to ' + str(power_mW) + 'mW'
		pbec_ipc.ipc_eval('guiSetPowerAndWait(' + str(int(power_mW)) + ')', 'laser_controller')
		print 'obtaining autoexposed image'
		im, meta = autoexposure.get_single_autoexposed_image(camera_label, interesting_colours = colour_weights)
		ims.append(im.copy())
		
		#print 'setting shutter to ' + str(s)
		#cam.set_property('shutter', s)
		#print 'setting gain to ' + str(g)
		#cam.set_property('gain', g)
		sleep(0.5)

		im = colour_to_monochrome(im)
		windowed_im = im * image_apature

		power = sum(windowed_im)
		area = 2*pi*bec_region_radius**2
		intensity = power / area / meta['shutter'] * 10**(-meta['gain']/20.0)
		p0i.append((power_mW, intensity))
		print 'output = ' + str(power) + 'counts shutter=' + str(meta['shutter']) + 'msec gain=' + str(meta['gain']) + 'dB'
		print 'intensity = ' + str(intensity)

	return p0i, ims
	
def save_power_ground_state_data(p0i, images, power_range):
	ts = pbeca.make_timestamp()
	experiment = pbeca.ExperimentalDataSet(ts=ts)
	experiment.meta.parameters['power_range'] = list(power_range)
	experiment.meta.parameters['power_vs_intensity'] = list(p0i)
	experiment.dataset['images'] = pbeca.InterferometerFringeData(experiment.ts, '_images.zip')
	experiment.dataset['images'].setData(images)
	experiment.saveAllData()
	print 'saved data to timestamp ' + ts


#p0i = [(5.0, 0.0031163973005996428), (84.5, 0.0031992799398992545), (164.0, 0.0032627914307371145), (243.5, 0.0033339220003762563), (323.0, 0.0034282548213083607), (402.5, 0.0035225948300506554), (482.0, 0.0036758605067296604), (561.5, 0.0040040650593229808), (641.0, 0.17738642475955407), (720.5, 0.3902215870681206), (800.0, 0.597061794768036)]
	

def ground_state_power_function(p, pth, alpha, a, b):
	threshold_mask = p > pth
	it = alpha*p + (a - alpha)*pth + b
	ib = a*p + b
	return threshold_mask*ib + ~threshold_mask*it
def ground_state_power_residuals(pars, xdata, ydata):
	return (ground_state_power_function(xdata, *pars) - ydata)**2

def fit_power_ground_state_find_pth(p0i, pth_guess=500):
	p, i = zip(*p0i)
	p = array(p)
	i = array(i)
	guess = (pth_guess, 1e-6, 3e-3, -1.5) 
	(fit_pars, dump) = leastsq(ground_state_power_residuals, guess, (p, i))
	pth, alpha, a, b = fit_pars
	print zip(('pth', 'alpha', 'a', 'b'), fit_pars)
	return pth, fit_pars
	
def plot_power_ground_state_data(p0i, fit_pars, pth):
	p, i = zip(*p0i)
	fake_p_axis = linspace(p[0], p[-1], 200)

	ts = pbeca.make_timestamp()
	figlabel = 'input-power-vs-ground-state-intensity' + ts
	figure(figlabel), clf()
	plot(p, i, '-x', label='data')
	plot(fake_p_axis, ground_state_power_function(fake_p_axis, *fit_pars), '-', label='fit, Pth=' + str(round(pth, 1)) + 'mW')
	ylim(-0.02,)
	xlabel('Input Power / mW')
	ylabel('Ground State Population / arb units')
	title('Input Power vs Ground State Intensity')
	legend(loc="upper left")
	savefig(figlabel + '.png')

	figlabel = 'input-power-vs-log-ground-state-intensity' + ts
	figure(figlabel), clf()
	loglog(p, i, '-x', label='data')
	loglog(fake_p_axis, ground_state_power_function(fake_p_axis, *fit_pars), '-', label='fit, Pth=' + str(round(pth, 1)) + 'mW')
	xlabel('Input Power / mW')
	ylabel('Ground State Population / arb units')
	title('Input Power vs Ground State Intensity')
	legend(loc="upper left")
	savefig(figlabel + '.png')


im = None
raw_input('finding center of image, set to a fairly bright cloud and press enter')
cam = pbece.getCameraByLabel(camera_label)
try:
	im = cam_get_image(cam)
finally:
	if cam.open:
		cam.close()
im = colour_to_monochrome(im)
if not cavity_center:
	print 'obtained image, fitting'
	fit_pars, gauss_fun = fit_gaussian_to_image(im) #allows angle to change, which probably wont happen for us
	x0_fit, y0_fit, sxp_fit, syp_fit, tan_theta_fit, offset_fit, amplitude_fit = fit_pars
	cavity_center = (int(x0_fit), int(y0_fit))
	print 'center of cavity ' + str(cavity_center)
	sys.exit(0)
	
if debug_graphs:
	figure('center of mass debug'), clf()
	imshow(im)
	pixelY, pixelX = cavity_center
	pixelY = int(pixelY)
	pixelX = int(pixelX)
	plot([pixelX - bec_region_radius, pixelX + bec_region_radius], [pixelY - bec_region_radius, pixelY + bec_region_radius], 'w-')
	plot([pixelX + bec_region_radius, pixelX - bec_region_radius], [pixelY - bec_region_radius, pixelY + bec_region_radius], 'w-')
	xlim(0, im.shape[1]), ylim(0, im.shape[0])
	
print 'finding first estimate of pth, powers=' + str(p_large_range)
first_power_intensity, images = take_power_ground_state_data(p_large_range, im.shape)
save_power_ground_state_data(first_power_intensity, images, p_large_range)

figure('first images'), clf()
for i, imm in enumerate(images):
	subplot(3, 6, i+1)
	imshow(imm)
pth_first, fit_pars = fit_power_ground_state_find_pth(first_power_intensity)
plot_power_ground_state_data(first_power_intensity, fit_pars, pth_first)
print 'first pth = ' + str(pth_first)

p_small_range = pth_first + p_small_range_rel*pth_first
print 'taking data at powers ' + str(list(p_small_range))
second_power_intensity, images = take_power_ground_state_data(p_small_range, im.shape)
save_power_ground_state_data(second_power_intensity, images, p_small_range)
figure('second images'), clf()
for i, imm in enumerate(images):
	subplot(3, 3, i+1)
	imshow(imm)

pth_second, fit_pars = fit_power_ground_state_find_pth(second_power_intensity, pth_first)
plot_power_ground_state_data(second_power_intensity, fit_pars, pth_second)

print 'second pth = ' + str(pth_second)

#background subtraction
#make work with AOM
#do scan of lam0
#work out errors, either bootstrapping(=assuming best estimate of underlying is the data we already have, so sample it with repetitions and see how result changes) or assuming gaussian/using residual change