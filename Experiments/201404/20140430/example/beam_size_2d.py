#ipython --pylab
#exec(open("beam_size_2d.py").read())
#Analysis re-used from D:\People\Nyman\waveguide_chip\analysis\2010\20100914_fit_beam_shape
from pbec_analysis import *
from scipy.optimize import leastsq
from matplotlib.font_manager import FontProperties
fontsize=8
fontProp = FontProperties(size = fontsize)

#---------------
#USER INPUTS
#---------------
magnification = 3.4 #imaging system magnification
#####hot_pixel_locations = [930:932,104:106] #TODO: eliminate always-on pixel
px = point_grey_chameleon_pixel_size/magnification

#eid,filend = "20140428_102135", "" #spherical side
#eid,filend = "20140428_102756", "" #spherical side
#eid,filend = "20140428_102941", "" #spherical side
#eid,filend = "20140428_103143", "" #spherical side
#eid,filend = "20140428_113014", "" #spherical side
#eid,filend = "20140428_113144", "" #spherical side
#eid,filend = "20140428_113315", "" #spherical side
#eid,filend = "20140428_113439", "" #spherical side
#eid,filend = "20140428_113752", "" #spherical side
#eid,filend = "20140428_123900", "" #spherical side
#eid,filend = "20140428_124200", "" #spherical side
#eid,filend = "20140428_141756", "" #spherical side
eid,filend = "20140428_150634", "" #spherical side


savename=eid+"_beam_size_2Dfit"
x0,y0=700,700 #defines center of subimage search area
dx,dy = 600,600 #defines half-size of RoI, in pixels
integ_x=1 #Strip half-width for x-integration (size in y)
integ_y=1 #Strip half-width for y-integration (size in x)

#---------------
#LOAD DATA
#---------------
df = DataFolder(eid)
im_raw = imread(df+eid+filend+".png")
im_greyscale = mean(im_raw[:,:,:2],2) #implicitly assumes that quantum efficiency is the same for all colours; picks only red and green
#im_greyscale = im_raw[:,:,1] #picks only green channel
im = im_greyscale
Npx_all,Npy_all=im.shape

#---------------
#DERIVED QUANTITIES
#---------------


#find position of brightest pixel


#blank out hot pixel area, TODO smoothing is below to avoid this but cant make it work
for xxx in range(5):
	for yyy in range(5):
		im[xxx][yyy] = 0

# first smooth to stop hot pixels confusing us
#smooth_im = array([smooth(f, 100, 'hanning') for f in im])
#smooth_im = transpose(array([smooth(f, 100, 'hanning') for f in transpose(smooth_im)]))

#by turning the 2d array into a 1d array and using max() functions
max_index = argmax(im.ravel()) #index of max value
x_max = max_index / im_greyscale.shape[1] - x0+dx #coordinates in the subimage
y_max = max_index % im_greyscale.shape[1] - y0+dy
#im[520][800] == im.ravel()[520 * im.shape[1] + 800]

subim=im[x0-dx:x0+dx,y0-dy:y0+dy]
Npx,Npy=subim.shape
imsave("subim.png", subim)

x = linspace(0,Npx*px,Npx)
y = linspace(0,Npy*px,Npy)
XX,YY = meshgrid(x,y)


#---------------
#FITTING
#---------------
#x0_guess,y0_guess =  px*dx,px*dx
x0_guess,y0_guess =  px*x_max,px*y_max
sxp_guess, syp_guess = px*dx/6., px*dy/6.
tan_theta_guess=0.
offset_guess=0.
amplitude_guess = 1.0

#x0_guess=375e-6
#y0_guess=401e-6
#sxp_guess=67e-6
#syp_guess=88e-6
#theta_guess=3.4
#offset_guess = 0.08
#amplitude_guess = 1
pars_guess_2d = x0_guess,y0_guess,sxp_guess,syp_guess,tan_theta_guess,offset_guess,amplitude_guess



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


#-----------------
#FITTING
#(p_fit_2d,stuff) = leastsq(residuals_2d, pars_guess_2d,args = (subim,(XX,YY)),full_output=1)
all_stuff = leastsq(residuals_2d, pars_guess_2d,args = (subim,(XX,YY)),full_output=1,maxfev=1000)
p_fit_2d = all_stuff[0]
x0_2d,y0_2d,sxp_2d,syp_2d,tan_theta_2d,offset_2d,amplitude_2d= p_fit_2d

#nearest-to-centre indices:
x0_2d_ind = find(x < (x0_2d)).max() #y0+dy
y0_2d_ind = find(y < (y0_2d)).max() #x0+dx
#cut_x = sum(im[x0-dx:x0+dx:,y0+y0_2d_ind-integ_x:y0+y0_2d_ind+integ_x],1)/(2*integ_x)
#cut_y = sum(im[x0+x0_2d_ind-integ_y:x0+x0_2d_ind+integ_y,y0-dy:y0+dy],0)/(2*integ_y)
cut_x = sum(subim[:,y0_2d_ind-integ_x:y0_2d_ind+integ_x],1)/(2*integ_x)
cut_y = sum(subim[x0_2d_ind-integ_y:x0_2d_ind+integ_y,:],0)/(2*integ_y)



#---------------
#PLOTTING
figure(3),clf()
suptitle(savename)
subplot(2,2,1)
s = "$1/e^2$ diameter = $2w = 4 \sigma$"
title(s)
contourf(1e3*y,1e3*x,subim,30,cmap=cm.gray,label="data")
xlabel("y/mm"),ylabel("x/mm")
#
subplot(2,2,2)
#fit_string = "$w_{x'},w_{y'} = "+str(round(1e6*abs(2*array(sxp_2d)),1))+", " +str(round(1e6*abs(2*array(syp_2d)),1))+"\,\mu$m"
fit_string = "$\sigma_{x'},\sigma_{y'} = "+str(round(1e6*abs(array(sxp_2d)),1))+", " +str(round(1e6*abs(array(syp_2d)),1))+"\,\mu$m"
#fit_string+=r" $tan\theta=$"+str(round(mod(theta_2d,2*pi),2))+" rad"
fit_string+=r" ${\rm tan}\theta=$"+str(round(tan_theta_2d,2))
title("Fit: "+ fit_string)
contourf(1e3*y,1e3*x,transpose(gaussian_2d(XX,YY,*p_fit_2d)),30,cmap=cm.gray,label="fit") #IS TRANSPOSE NECESSARY?
xlabel("y/mm"),ylabel("x/mm")
#
subplot(2,2,3)
plot(1e3*x,cut_x)
plot(1e3*x,gaussian_2d(x,y0_2d,*p_fit_2d),label="y0="+str(round(1e6*y0_2d,1))+ "$\mu$m")
#plot(1e3*x,gaussian_2d(x,dy*px,*p_fit_2d),label="y0="+str(round(1e6*y0_2d,1))+ "$\mu$m")
xlabel("x/mm"),ylabel("Amplitude")
legend(loc="best",prop=fontProp)

subplot(2,2,4)
plot(1e3*y,cut_y)
plot(1e3*y,gaussian_2d(x0_2d,y,*p_fit_2d),label="x0="+str(round(1e6*x0_2d,1))+ "$\mu$m")
#plot(1e3*y,gaussian_2d(dx*px,y,*p_fit_2d),label="x0="+str(round(1e6*x0_2d,1))+ "$\mu$m")
xlabel("y/mm"),ylabel("Amplitude")
legend(loc="best",prop=fontProp)
subplots_adjust(hspace=0.2,wspace=0.3,top=0.90,bottom=0.07)

savefig(savename+".png")


#EOF