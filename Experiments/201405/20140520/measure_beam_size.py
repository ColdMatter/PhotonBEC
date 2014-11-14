#execfile("measure_beam_size.py")
from pbec_analysis import *
from point_grey import *
from analyse_images import *
from scipy.misc import imsave

magnification = 3.4 #imaging system magnification
binning = 1 #please set manually, Settings -> Standard Video Modes -> 640x480 for bin=2
px = binning*point_grey_chameleon_pixel_size/magnification
x0,y0=480,640 #defines center of subimage search area
dx,dy = 470,470 #defines half-size of RoI, in pixels
auto_guess=True
#number_of_cycles=1
#name_extra=None

for i in range(number_of_cycles):
	ts = make_timestamp()
	ts_argument=None
	if name_extra!=None:
		ts_argument = ts
	im_raw = grab_image(ts=ts_argument,name_extra=name_extra,numberOfColours=1) #images come out as negative. Why?
	if auto_guess: 
		im_raw_bw= im_raw[:,:,0]+im_raw[:,:,1]
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
		#
	fig,pars_fit = fit_and_plot(im_raw,ts,x0,y0,dx,dy,px,maxfev=200)
	fig.subplots_adjust(top=0.85)
	fig.suptitle(str(map(lambda x: round(x,1),array(pars_fit[2:4])*px*1e6))+" $\mu$m",fontsize=36)
	fig.savefig("temp"+"_beam_size.png")
	print ts
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

def thermal_size(q):
	#sigma, not w
	prefac = (constants.Boltzmann * T * lambda_0**2 * RoC)  / (4* constants.h * n_L * constants.c)
	return sqrt(q*prefac)

#execfile("measure_beam_size.py")
#EoF
