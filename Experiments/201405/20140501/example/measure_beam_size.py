#execfile("measure_beam_size.py")
from pbec_analysis import *
from repeated_images import *
from scipy.misc import imsave

magnification = 3.4 #imaging system magnification
px = point_grey_chameleon_pixel_size/magnification
x0,y0=430,630 #defines center of subimage search area
#dx,dy = 180,180 #defines half-size of RoI, in pixels
dx,dy = 320,320 #defines half-size of RoI, in pixels
#Mostly work in units of pixels, except for text output

for i in range(100):
	ts = TimeStamp()
	print ts
	im_raw = grabImage(ts=None) #images come out as negative. Why?
	fig,pars_fit = fit_and_plot(im_raw,ts,x0,y0,dx,dy,px)
	fig.subplots_adjust(top=0.85)
	fig.suptitle(str(map(lambda x: round(x,1),array(pars_fit[2:4])*px*1e6))+" $\mu$m",fontsize=36)
	fig.savefig("temp"+"_beam_size.png")

#fig.savefig(ts+"_beam_size.png")
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
