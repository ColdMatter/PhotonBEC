#number_of_cycles=1; name_extra=None;execfile("measure_beam_size.py")
#name_extra being non-None means it will save the image to a file

sys.path.append("D:\\Control\\PythonPackages\\")

from pbec_analysis import *
from pbec_experiment import get_single_image
from pbec_experiment import camera_pixel_size_map
from analyse_images import fit_and_plot_image
from analyse_images import mean_and_std_dev
from scipy.misc import imsave
import os

number_of_cycles = int(raw_input("number of cycles[1] :") or 1)
camera_name = raw_input("camera name[flea] :") or "flea"
saving = raw_input("saving? leave blank for false: ") != ""
print('saving = ' + str(saving))

#magnification = 3.4 #imaging system magnification. Measured 4/8/14 for main chameleon
magnification = 3.6 #imaging system magnification. Measured 29/8/14 for flea
binning = 1 #please set manually, Settings -> Standard Video Modes -> 640x480 for bin=2
px = binning * camera_pixel_size_map[camera_name] / magnification
x0,y0=400,400 #defines center of subimage search area
dx,dy = 200,200 #defines half-size of RoI, in pixels
auto_guess=True

#if saving was false you can run this function from the command line
def save():
	ex = Experiment(ts)
	ex.setCameraData(im_raw)
	ex.meta.comments = "Measured beam size"
	ex.saveAllData()
	os.system('echo '+ts+' | clip')
	print "Saving "+ts+"; timestamp copied to clipboard"

for i in range(number_of_cycles):
	ts = make_timestamp()
	im_raw = get_single_image(camera_name)
	
	if saving:
		save()

	if auto_guess: 
		im_raw_bw= im_raw[:,:,0]# + im_raw[:,:,1]
		x0,y0,dx_half,dy_half = mean_and_std_dev(im_raw_bw)
		dx,dy=dx_half*2,dy_half*2
		if dx>x0: 
			dx=x0-1
		elif dx+x0>im_raw.shape[1]:
			dx = im_raw.shape[1]-x0-1
		if dy>y0: 
			dy=y0-1
		elif dy+y0>im_raw.shape[1]:
			dy = im_raw.shape[1]-y0-1
		#print('autoguess x0,y0=' + str((x0, y0)) + ' dx,dy=' + str((dx, dy)))
		#
	
	fig, pars_fit = fit_and_plot_image(im_raw, ts, x0, y0, dx, dy, px)
	fig.subplots_adjust(top=0.85)
	fig.suptitle(str(map(lambda x: round(x,1), array(pars_fit[2:4])*px*1e6))+" $\mu$m", fontsize=36)
	fig.savefig("temp"+"_beam_size.png")
	imsave("raw-image.png", im_raw)
	print(ts + " pars_fit=" + str(pars_fit))
	sys.stdout.write("\x07") #beep

#ts=make_timestamp();print ts;im=grab_image(ts,"_check_therm")
#number_of_cycles=1; name_extra="_spot_size";execfile("measure_beam_size.py");print ts
#number_of_cycles=20; name_extra=None;execfile("measure_beam_size.py")

#---------RANDOM RUBBISH LEFT OVER FROM SOME OTHER THINGS I'M DOING
T = 300 #Kelvin
n_L =1.5 #refractive index of solvent
lambda_0 = 590e-9 #cavity cutoff wavelength
q = 5 #electric field penetration into mirror surfaces
RoC = 0.25 #mirror radius of curvature
from scipy import constants

def thermal_size(q,T=T,RoC=RoC,lambda_0=590e-9):
	#sigma, not w
	#NOTE: factor 2 not 4 in denominator: I think it's now correct
	prefac = (kB * T * lambda_0**2 * RoC)  / (2* constants.h * n_L * constants.c)
	return sqrt(q*prefac)

#execfile("measure_beam_size.py")
#EoF
