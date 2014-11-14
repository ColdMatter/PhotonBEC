#exit()

#ipython --pylab
#execfile("threshold_image_fitting.py")
from pbec_analysis import *
from scipy.optimize import leastsq
from numpy import ma

#--------------------------
#UTILITY FUNCTIONS
#--------------------------
def gaussian_2d(x,y,x0,y0,sxp,syp,tan_theta,offset,amplitude):
	"""
	Gaussian in 2D, with possible rotation of principle axes
	Arguments:
	x,y: co-ordinates at which to evaluate
	x0,y0: centre
	sxp, syp: rms sizes along principle axes
	tan_theta: angle of principle axes to co-ordinate axes
	offset: global addition
	amplitude: magnitude of peak
	"""
	theta = arctan(tan_theta)
	cos_t= cos(theta)
	sin_t= sin(theta)
	xp = x*cos_t - y*sin_t
	yp = y*cos_t + x*sin_t
	xp0 = x0*cos_t - y0*sin_t
	yp0 = y0*cos_t + x0*sin_t
	exponent = ( ((xp-xp0)/sxp)**2 + ((yp-yp0)/syp)**2 ) / 2.
	return  amplitude * exp(-exponent) + offset



#-------------------------
#SOME DATA
#-------------------------
test_data_name = "./20140428_150450_pretty_picture.png"
im_raw = imread(test_data_name)
im_greyscale = mean(im_raw[:,:,:2],2) #implicitly assumes that quantum efficiency is the same for all colours; picks only red and green
im = array(im_greyscale)

#TODO: add a fake condensate peak near the middle, to check wether masking works or not.
Npx,Npy=im.shape
x = range(Npx)
y = range(Npy)
XX,YY = meshgrid(x,y)

mask_coords = array([500,560,510,570])+0
x1,y1=532,542
sx1,sy1=8,8
a1=1.

condensate_bit = gaussian_2d(transpose(XX),transpose(YY),x1,y1,sx1,sy1,0.,0.,a1)
im = im+condensate_bit

figure(1),clf()
imshow(im),colorbar()

#-------------------------------
#FIRST, A FUNCTION TO 2D-GAUSSIAN FIT AN IMAGE
#-------------------------------
def residuals_2d(pars,value_data,position_data):
	#Must be written to take 1D arrays not 2D arrays, to be used by scipy.optimize.leastsq
	#position_data is a 2-tuple of arrays of XX and YY each of the same shape as value_data
	x0,y0,sxp,syp,tan_theta,offset,amplitude = pars
	flat_data = ravel(transpose(value_data)) #Does this need transposing?
	xx = ravel(position_data[0])#Does this need transposing?
	yy = ravel(position_data[1])#Does this need transposing?
	err = (flat_data-gaussian_2d(xx,yy,x0,y0,sxp,syp,tan_theta,offset,amplitude))**2
	return err


def fit_gaussian_to_image(im,maxfev=1000):
    #Should return centre position, sizes, angle and a function which gives the fitted gaussian
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

    all_stuff = leastsq(residuals_2d, pars_guess,args = (im,(XX,YY)),full_output=1,maxfev=maxfev)
    pars_fit = all_stuff[0]

    x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit = pars_fit

    def fit_gaussian(x,y):
	return gaussian_2d(x,y,x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit)

    return pars_fit,fit_gaussian

#test fit 
"""
dump = fit_gaussian_to_image(im,maxfev=100)
x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit = dump[0]
fitfunc = dump[1]
Npx,Npy=im.shape
x = range(Npx)
y = range(Npy)
XX,YY = meshgrid(x,y)
figure(2),clf()
subplot(2,1,1)
imshow(im),colorbar()
subplot(2,1,2)
imshow(transpose(fitfunc(XX,YY))),colorbar()
#NOTE: Why does the transpose thing happen in meshgrid?
"""

#-------------------------------
#SECOND, A FUNCTION TO 2D-GAUSSIAN FIT ONLY THE WINGS OF AN IMAGE
#-------------------------------

"""
def fit_gaussian_to_masked_image(im,mask_coords,maxfev=1000):
"""
def residuals_2d_masked(pars,value_data,position_data):
	x0,y0,sxp,syp,tan_theta,offset,amplitude = pars
	flat_mask = ravel(transpose(value_data.mask))
	flat_data = ma.masked_array(ravel(transpose(value_data)),mask=flat_mask) #Does this need transposing?
	xx = ma.masked_array(ravel(position_data[0]),mask=flat_mask)#Does this need transposing?
	yy = ma.masked_array(ravel(position_data[1]),mask=flat_mask)#Does this need transposing?
	#err = (flat_data-gaussian_2d(xx,yy,x0,y0,sxp,syp,tan_theta,offset,amplitude))**2
	err = ma.power(ma.subtract(flat_data,gaussian_2d(xx,yy,x0,y0,sxp,syp,tan_theta,offset,amplitude)),2)
	#err = err * err.mask
	return err



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
#execfile("threshold_image_fitting.py")
#mask format: x0,x1,y0,y1: the bounds of a rectangular mask
#mask_coords = [510,550,520,560]
mask = ones_like(XX)
mask = mask * (XX>mask_coords[0]) * (XX<mask_coords[1]) * (YY>mask_coords[2]) * (YY<mask_coords[3])
XX_masked = ma.masked_array(XX,mask=mask)
YY_masked = ma.masked_array(YY,mask=mask)
im_masked = ma.masked_array(transpose(transpose(im)),mask=transpose(mask)) #why the transpose? seems to cause problems...FIXME
figure(6),clf(), imshow(im_masked)
sum(im_masked)
#figure(6),clf(), imshow(XX_masked)
#figure(6),clf(), imshow(YY_masked)


#all_stuff = leastsq(residuals_2d, pars_guess,args = (im_masked,(XX_masked,YY_masked)),full_output=1,maxfev=100)
all_stuff = leastsq(residuals_2d_masked, pars_guess,args = (im_masked,(XX_masked,YY_masked)),full_output=1,maxfev=100)
pars_fit = all_stuff[0]

x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit = pars_fit

def fit_gaussian(x,y):
    return gaussian_2d(x,y,x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit)

#    return pars_fit,fit_gaussian

#dump = fit_gaussian_to_image(im,maxfev=100)
#x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit = dump[0]
#fitfunc = dump[1]
fitfunc = fit_gaussian
Npx,Npy=im.shape
x = range(Npx)
y = range(Npy)
XX,YY = meshgrid(x,y)

figure(2),clf()
subplot(2,1,1)
imshow(im),colorbar()
subplot(2,1,2)
imshow(transpose(fitfunc(XX,YY))),colorbar()

figure(3),clf()
#plot cross-sections in appropriate places for comparison
x0,y0=round(x0_fit), round(y0_fit)
subplot(2,1,1)
plot(x,im[:,y0])
plot(x,transpose(fitfunc(XX,YY))[:,y0])
xlabel("x")
subplot(2,1,2)
plot(y,im[x0,:])
plot(y,transpose(fitfunc(XX,YY))[x0,:])
xlabel("y")

#-------------------------------
#THIRD, EXTRACT DIFFERENCE BETWEEN GAUSSIAN-WING-FIT AND DATA
#-------------------------------


#execfile("threshold_image_fitting.py")
#EoF
