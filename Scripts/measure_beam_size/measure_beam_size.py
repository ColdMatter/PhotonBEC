#number_of_cycles=1; name_extra=None;execfile("measure_beam_size.py")
#name_extra being non-None means it will save the image to a file

sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("Y:\\Control\\PythonPackages\\")

from pbec_analysis import *
from pbec_experiment import get_single_image
from pbec_experiment import camera_pixel_size_map
from analyse_images import fit_and_plot_image
from analyse_images import mean_and_std_dev
from scipy.misc import imsave, imresize
import Image
import os

number_of_cycles = int(raw_input("number of cycles[1] :") or 1)
camera_name = raw_input("camera name[chameleon] :") or "chameleon"
post_binning = int(raw_input("post-processing binning[4] :") or 4)
interval = int(raw_input("interval/msec[100] :") or 100) / 1000.0
saving = raw_input("saving? leave blank for false: ") != ""
print('saving = ' + str(saving))

#magnification = 3.4 #imaging system magnification. Measured 4/8/14 for main chameleon
magnification = 3.6 #imaging system magnification. Measured 29/8/14 for flea
#magnification = 3.26 #imaging system magnification. Measured 27/10/15 for mini setup chameleon
binning = 1 #please set manually, Settings -> Standard Video Modes -> 640x480 for bin=2
px = binning * camera_pixel_size_map[camera_name] / magnification
x0,y0=400,400 #defines center of subimage search area, without taking into account post-binning
dx,dy = 350,350 #defines half-size of RoI, in pixels, without taking into account post-binning
auto_guess=True
debug = True

def log(x):
	if debug:
		print(x)

for i in range(number_of_cycles):
	ts = make_timestamp()
	im_raw = get_single_image(camera_name)

	if post_binning==1:
		im_bin = im_raw
		px_binned = px
	else:
		im_bin = imresize(im_raw, array(im_raw.shape)/post_binning, interp="bilinear")
		px_binned = px*post_binning
	
	im_bin_bw= im_bin[:,:,0]# + im_bin[:,:,1]
	if auto_guess:
		log('auto guessing mean and std dev')
		x0,y0,dx_half,dy_half = mean_and_std_dev(im_bin_bw)
		log('auto guessed x0,y0,dx_half,dy_half = %d, %d, %d, %d' % (x0,y0,dx_half,dy_half))
		dx,dy=dx_half*2,dy_half*2
		if dx>x0: 
			dx=x0-1
		elif dx+x0>im_raw.shape[1]:
			dx = im_raw.shape[1]-x0-1
		if dy>y0: 
			dy=y0-1
		elif dy+y0>im_raw.shape[1]:
			dy = im_raw.shape[1]-y0-1
		log('autoguess after crop x0,y0=' + str((x0, y0)) + ' dx,dy=' + str((dx, dy)))
	elif post_binning!=1:
		x0, y0, dx, dy = x0/post_binning, y0/post_binning, dx/post_binning, dy/post_binning
		
	
	#fig, pars_fit = fit_and_plot_image(im_raw, ts, x0, y0, dx, dy, px)
	fig, pars_fit = fit_and_plot_image(im_bin, ts, x0, y0, dx, dy, px_binned)
	fig.subplots_adjust(top=0.85)
	fitted_sizes_um = (map(lambda x: round(x,1), array(pars_fit[2:4])*px_binned*1e6)) 
	fig.suptitle(str(fitted_sizes_um)+" $\mu$m", fontsize=36)
	fig.savefig("temp"+"_beam_size.png")
	print "Saving "+ts+"; timestamp copied to clipboard"
	def save():
		#if saving was false you can run this function from the command line
		cd = CameraData(ts,data=im_raw)
		ex = ExperimentalDataSet(ts)
		ex.dataset={"cam_image":cd}
		ex.meta.parameters={"magnification":magnification,"camera_name":camera_name,"post_binning":post_binning}
		ex.meta.parameters.update({"fitted_sizes_um":fitted_sizes_um})
		ex.meta.comments = "Measured beam size"
		ex.saveAllData()
		fig.savefig(timestamp_to_filename(ts,"_beam_size.png"))
		#Also save display figure in data folder
		os.system('echo '+ts+' | clip')
	if saving:
		save()
	imsave("raw-image.png", im_raw)
	print(ts + " pars_fit=" + str(pars_fit))
	sys.stdout.write("\x07") #beep
	time.sleep(interval)


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
