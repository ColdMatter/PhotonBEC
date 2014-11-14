#ipython --pylab
from pbec_analysis import *
from scipy.optimize import leastsq
from numpy import ma
from analyse_images import *

#-------------------------------
#A FUNCTION TO 2D-GAUSSIAN FIT ONLY THE WINGS OF AN IMAGE
#-------------------------------
def residuals_2d_masked(pars,value_data,position_data):
	x0,y0,sxp,syp,tan_theta,offset,amplitude = pars
	flat_mask = ravel(transpose(value_data.mask))
	flat_data = ma.masked_array(ravel(transpose(value_data)),mask=flat_mask)
	xx = ma.masked_array(ravel(position_data[0]),mask=flat_mask)
	yy = ma.masked_array(ravel(position_data[1]),mask=flat_mask)
	err = ma.power(ma.subtract(flat_data,gaussian_2d(xx,yy,x0,y0,sxp,syp,tan_theta,offset,amplitude)),2)
	return err


def fit_gaussian_to_image_masked(im,mask_coords,maxfev=1000):
    #Should return centre position, sizes, angle and a function which gives the fitted gaussian
    #mask_coords format: x0,x1,y0,y1: the bounds of a rectangular mask
    Npx,Npy=im.shape
    x = range(Npx)
    y = range(Npy)

    #------BEGIN DODGY: matching shape correctly?
    XX,YY = meshgrid(x,y)
    x0_guess = sum(transpose(XX)*im) / sum(im)
    y0_guess = sum(transpose(YY)*im) / sum(im)
    sxp_guess = sqrt(sum((transpose(XX-x0_guess)**2)*im) / sum(im))
    syp_guess = sqrt(sum((transpose(YY-y0_guess)**2)*im) / sum(im))
    #-----END DODGY

    tan_theta_guess =0.
    offset_guess = im.min()
    amplitude_guess = sum(im)/(2*pi*sxp_guess *syp_guess)
    pars_guess = x0_guess,y0_guess,sxp_guess,syp_guess,tan_theta_guess,offset_guess,amplitude_guess

    #----NOW THE MASKING
    mask = ones_like(XX)
    mask = mask * (XX>mask_coords[0]) * (XX<mask_coords[1]) * (YY>mask_coords[2]) * (YY<mask_coords[3])
    XX_masked = ma.masked_array(XX,mask=mask)
    YY_masked = ma.masked_array(YY,mask=mask)
    im_masked = ma.masked_array(transpose(transpose(im)),mask=transpose(mask)) #why the transpose? seems to cause problems...FIXME

    #and the fitting
    all_stuff = leastsq(residuals_2d_masked, pars_guess,args = (im_masked,(XX_masked,YY_masked)),full_output=1,maxfev=100)
    pars_fit = all_stuff[0]

    x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit = pars_fit

    def fit_gaussian(x,y):
		return gaussian_2d(x,y,x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit)

    return pars_fit,fit_gaussian,mask

#-------------------------------
#EXAMPLE: EXTRACT DIFFERENCE BETWEEN GAUSSIAN-WING-FIT AND DATA
#-------------------------------
#It might even be worth fitting the residual with a gaussian, to determine the size shape and amplitude of the bit that remains
#Example needs im and mask and fit_func
"""
Npx,Npy=im.shape
XX,YY = meshgrid(range(Npx),range(Npy))
fit_im = transpose(fit_func(XX,YY))
res = im-fit_im
res_masked = ma.masked_array(res,mask = ~mask)
ma.sum(res_masked)
sum(res)

figure(6),clf()
imshow(res),colorbar()
"""
#execfile("threshold_image_fitting.py")
#EoF
