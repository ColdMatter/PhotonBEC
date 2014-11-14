#execfile("measure_beam_size.py")
from pbec_analysis import *
from point_grey import *
from analyse_images import *
from scipy.misc import imsave

magnification = 3.4 #imaging system magnification
binning = 2 #please set manually, Settings -> Standard Video Modes -> 640x480 for bin=2
px = binning*point_grey_chameleon_pixel_size/magnification
x0,y0=430,630 #defines center of subimage search area
dx,dy = 400,400 #defines half-size of RoI, in pixels

x0,y0 = 215,315 #for binning=2
dx,dy = 200,200

#x0,y0=600,600 #defines center of subimage search area
#dx,dy = 214,314 #defines half-size of RoI, in pixels
#dx,dy = 320,320 #defines half-size of RoI, in pixels
#Mostly work in units of pixels, except for text output

for i in range(100):
	ts = make_timestamp()
	im_raw = grab_image(ts=None,numberOfColours=1) #images come out as negative. Why?
	fig,pars_fit = fit_and_plot(im_raw,ts,x0,y0,dx,dy,px,maxfev=200)
	fig.subplots_adjust(top=0.85)
	fig.suptitle(str(map(lambda x: round(x,1),array(pars_fit[2:4])*px*1e6))+" $\mu$m",fontsize=36)
	fig.savefig("temp"+"_beam_size.png")
	print ts
	sys.stdout.write("\x07") #beep


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
