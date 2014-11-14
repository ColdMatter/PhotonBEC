#execfile("measure_beam_size.py")
from pbec_analysis import *
from repeated_images import *
from scipy.misc import imsave

magnification = 3.4 #imaging system magnification
px = point_grey_chameleon_pixel_size/magnification
x0,y0=500,600 #defines center of subimage search area
dx,dy = 180,180 #defines half-size of RoI, in pixels
#Mostly work in units of pixels, except for text output

for i in range(1):
	ts = TimeStamp()
	print ts
	im_raw = grabImage(ts=None) #images come out as negative. Why?
	fig,pars_fit = fit_and_plot(im_raw,ts,x0,y0,dx,dy,px)
	fig.subplots_adjust(top=0.85)
	fig.suptitle(str(map(round,array(pars_fit[2:4])*px*1e6))+" $\mu$m",fontsize=36)
	fig.savefig("temp"+"_beam_size.png")

#fig.savefig(ts+"_beam_size.png")

#execfile("measure_beam_size.py")
#EoF
