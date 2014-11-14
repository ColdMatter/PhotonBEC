#ipython --pylab
#execfile("analyse_images.py")
from pbec_analysis import *
from scipy.optimize import leastsq
from scipy.misc import imsave

#Tools for fitting images

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

def residuals_2d(pars,value_data,position_data):
	#Must be written to take 1D arrays not 2D arrays, to be used by scipy.optimize.leastsq
	#position_data is a 2-tuple of arrays of XX and YY each of the same shape as value_data
	x0,y0,sxp,syp,tan_theta,offset,amplitude = pars
	flat_data = ravel(transpose(value_data)) #Does this need transposing?
	xx = ravel(position_data[0])#Does this need transposing?
	yy = ravel(position_data[1])#Does this need transposing?
	err = (flat_data-gaussian_2d(xx,yy,x0,y0,sxp,syp,tan_theta,offset,amplitude))**2
	return err

def mean_and_std_dev(im):
	#Should return centre position, sizes, angle and a function which gives the fitted gaussian
	im = array(im,dtype=float) #deals with large numbers, avoiding integer overflow
	Npx,Npy=im.shape
	x = range(Npx)
	y = range(Npy)
	#
	#------BEGIN DODGY: matching shape correctly?
	XX,YY = meshgrid(x,y)
	x0_guess = sum(transpose(XX)*im) / sum(im)
	y0_guess = sum(transpose(YY)*im) / sum(im)
	#It seems that the std dev estimation is not robust when dealing with large integers!
	sxp_guess = sqrt(sum((transpose(XX-x0_guess)**2)*im) / sum(im))
	syp_guess = sqrt(sum((transpose(YY-y0_guess)**2)*im) / sum(im))
	return x0_guess,y0_guess,sxp_guess,syp_guess


def fit_gaussian_to_image(im,maxfev=1000):
	#Should return centre position, sizes, angle and a function which gives the fitted gaussian
	Npx,Npy=im.shape
	x = range(Npx)
	y = range(Npy)
	XX,YY = meshgrid(x,y)
	#
	x0_guess,y0_guess,sxp_guess,syp_guess = mean_and_std_dev(im)
	#
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

def fit_and_plot(im_raw,ts,x0,y0,dx,dy,px,maxfev=200,colour_weights=(1.0,1.0,0)):
	subim=im_raw[x0-dx:x0+dx,y0-dy:y0+dy,:]
	r,g,b=colour_weights
	im = 1-(r*subim[:,:,0]+g*subim[:,:,1]+b*subim[:,:,2]) #crude conversion to black and white
		#Also, sometimes 1-image is -1, which doesn't make sense
	####im = im*(im>0) #HACK to ensure positive images

	figure(24),clf()
	subplot(2,2,1)
	#s = "$1/e^2$ diameter = $2w = 4 \sigma$"
	#title(s)
	imshow(im,cmap=cm.gray)

	#-------------------------
	#Plotting the resulting fit
	dump = fit_gaussian_to_image(im,maxfev=maxfev)

	x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit = dump[0]
	fitfunc = dump[1]

	Npx,Npy=im.shape
	x = array(range(Npx))
	y = array(range(Npy))
	XX,YY = meshgrid(x,y)
	im_fit = transpose(fitfunc(XX,YY))

	figure(24),clf()
	subplot(2,2,1)
	#s = "$1/e^2$ diameter = $2w = 4 \sigma$"
	#title(s)
	title(ts)
	imshow(im,cmap=cm.gray)

	subplot(2,2,2)
	fit_string = "$\sigma_{x'},\sigma_{y'} = "+str(round(1e6*px*abs(array(sxp_fit)),1))+", " +str(round(1e6*px*abs(array(syp_fit)),1))+"\,\mu$m"
	#fit_string = "$\sigma_{x'},\sigma_{y'} = "+str(round(abs(array(sxp_fit)),1))+", " +str(round(abs(array(syp_fit)),1))+"$ px"
	fit_string+=r" ${\rm tan}\theta=$"+str(round(tan_theta_fit,2))
	title("Fit: "+ fit_string)
	imshow(im_fit,cmap=cm.gray)

	#plot cross-sections in appropriate places for comparison
	x0=round(x0_fit)
	if x0>Npx-1:
		x0=Npx-1
	x0 = x0*(x0>=0)
		
	y0=round(y0_fit)
	if y0>Npy-1:
		y0=Npy-1
	y0 = y0*(y0>=0)

	subplot(2,2,3)
	plot(x,im[:,y0])
	plot(x,im_fit[:,y0])
	xlabel("x / px"),ylabel("Red+Green, cut at centre")
	subplot(2,2,4)
	plot(y,im[x0,:])
	plot(y,im_fit[x0,:])
	xlabel("y / px")
	fig = gcf()
	return fig,(x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit)



#EoF
