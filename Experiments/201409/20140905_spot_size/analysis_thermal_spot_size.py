#ipython --pylab
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_analysis import *
#from analyse_spectra import *
from matplotlib.font_manager import FontProperties
fontsize=8
fontProp = FontProperties(size = fontsize)
from analyse_images import *
import hene_utils
from scipy.optimize import curve_fit,leastsq


saving=True
#PARAMETERS FOR EACH DATA SET
selector=2
if selector==1:
	first_time,last_time = "125518","130640"
	background_subtraction = 0.95
	colour_weights = (1,1,0,0)
	leastsq_range_adjust = -20,6 #wavelength range for fitting, in nm
	xlimits=(530,622) #for spectra
	ylimits=(1e5,1e9)
	x0,y0= 550,520 #centre x0 and y0
	dx,dy= 150,150 #half-size of roi dx and dy
	spec_smooth=10
	rejected_parameter_values = [100, 90, 110]
	spotsizefileend = "_camera.png"
if selector==2:
	first_time,last_time = "161940","164223"
	background_subtraction = 0.95
	colour_weights = (1,1,0,0)
	leastsq_range_adjust = -20,6 #wavelength range for fitting, in nm
	xlimits=(530,622) #for spectra
	ylimits=(1e5,1e9)
	x0,y0= 550,520 #centre x0 and y0
	dx,dy= 150,150 #half-size of roi dx and dy
	spec_smooth=10
	rejected_parameter_values = []
	spotsizefileend = "_camera.png"#

#PARAMETERS COMMON TO ALL DATA SETS
data_date = "20140905"
#dx,dy= 150,150 #half-size of roi dx and dy
centre_find_dx,centre_find_dy=100,100
smooth_window_len = 1 #for radial profiles
magnification = 3.4 #measured 4/8/14
#Guesses for spectrum fitting
(lam0_guess,T_guess,spec_amplitude_guess,spec_offset_guess) = (575e-9,200,1e7,1e6)
	#NOTE: lam0_guess is completely ignored
#leastsq_range = 540,615 #wavelength range for fitting, in nm

variable_parameter = "set_point"
savename="thermal_spot_size"

#---------------------
#USEFUL FUNCTIONS
def gaussian(r,sig,amp,off):
	#This particular Gaussian is fixed to have its centre at zero
	return off + amp*exp(-r**2 / (2*sig**2))

def gaussian_residuals(pars,ydata,xdata):
	return ( gaussian(xdata, *pars) - ydata )**2

def number_dist_residuals(pars, ydata, xdata):
	#Takes 5 parameters. Calculated residuals in log space
	#"number_distn" is to be found in pbec_analysis
	#Setting mu=0 returns the Boltzmann distribution
	(lam0, T, amplitude, offset) = pars
	mu=0
	pars = (lam0, T, amplitude, mu, offset)
	return (log(number_distn(xdata, *pars)) - log(ydata))**2

def fit_spectrum_thermal(xdata,ydata,leastsq_range,pars_guess,smooth_window_len=5,smooth_window="flat"):
	#This function could be modified to make an educated guess at lam0, e.g. the peak of the distribution plus a couple of nm
	ydata_smooth = smooth(ydata, window_len=smooth_window_len, window=smooth_window)
	#crop data so it the leastsq fit only considers the datapoints in wavelength range leastsq_range[index]
	data_smooth = zip(xdata, ydata_smooth)
	sliced_data_smooth = [x for x in data_smooth if x[0] >= leastsq_range[0] and x[0] <= leastsq_range[1]]
	sliced_xdata, sliced_ydata_smooth = array(zip(*sliced_data_smooth))
	#lam_max =1e-9*sliced_xdata[argmax(sliced_ydata_smooth)] #+ 5e-9#stupid nm <-> m conversion
	#pg = list(pars_guess)
	#pg[0]=lam_max #HACK! override initial guess!!!!!
	#Could also try to hack it so that the guess is always greater than the 568nm contaminant
	#pars_guess = tuple(pg)
	#
	thy_function = number_dist_residuals
	lssolution = leastsq(thy_function, pars_guess, args=(sliced_ydata_smooth, 1e-9*sliced_xdata))
	lam0 = lam_max #HACK! because it wasnt fitting
	(lam0,T,amplitude,offset) = lssolution[0]
	return lssolution[0]

#Thermal physics
T = 300 #Kelvin
n_L =1.5 #refractive index of solvent
RoC = 0.25 #mirror radius of curvature
q=8 #or maybe 9, not sure
lambda_0=585e-9 #approx

from scipy import constants

def thermal_size(q,T=T,RoC=RoC,lambda_0=590e-9):
	#sigma, not w
	#NOTE: factor 2 not 4 in denominator: I think it's now correct
	prefac = (kB * T * lambda_0**2 * RoC)  / (2* constants.h * n_L * constants.c)
	return sqrt(q*prefac)

#----------------------------------
#START LOADING THE META DATA
first_ts,last_ts = data_date+"_"+first_time,data_date+"_"+last_time
ts_list = timestamps_in_range(first_ts,last_ts,extension = "_meta.json")
ex_list = map(Experiment,ts_list)
print "Loading metadata..."
dump = [ex.meta.load() for ex in ex_list] #needed now for sorting through experiments

par_vals = map(lambda x:x.meta.parameters[variable_parameter],ex_list)
unique_par_vals = list(set(par_vals))
unique_par_vals.sort()
#Remove unwanted values
for rpv in rejected_parameter_values:
	unique_par_vals.remove(rpv)

#Parcel out the experiments
ex_dict={}
for upv in unique_par_vals:
	selected_ex_list = filter(lambda x:x.meta.parameters[variable_parameter]==upv,ex_list)
	sig_ex_list = filter(lambda x:x.meta.parameters["AOM_voltage"]!=0,selected_ex_list)
	bkg_ex_list = filter(lambda x:x.meta.parameters["AOM_voltage"]==0,selected_ex_list)
	ex_pair = {"sig":sig_ex_list, "bkg":bkg_ex_list}
	#Now reject all parameters where any of the data has a camera error
	camera_errors_list = [x.meta.parameters["camera_errors"] for x in selected_ex_list]
	filter_func = lambda x:x==str(None)
	Nerrors = len(filter(lambda x:x!="None",camera_errors_list))
	if Nerrors == 0:
		ex_dict.update({upv:ex_pair})
	else:
		print "Camera errors found for parameter value "+str(upv)

#LOAD AND BACKGROUND SUBTRACT DATA
corr_dict = {}
for upv in unique_par_vals:
	sel = ex_dict[upv]
	#Assume there is only one experiment for each parameter, i.e. no averaging
	i=0
	sig,bkg = sel["sig"][i],sel["bkg"][i]
	for ex in [sig,bkg]:
		ex.loadSpectrometerData()
		ex.loadCameraData()
		#if load_images: ex.loadCameraData()
	corr = sig.copy() #a background-corrected Experiment object
	sig_smooth = smooth(sig.spectrum,window_len=smooth_window_len)
	bkg_smooth = smooth(bkg.spectrum,window_len=smooth_window_len)
	#Now subtract the images too/ Do they need smoothing?
	im_sig,im_bkg = sig.im, bkg.im
	corr.spectrum = sig_smooth - background_subtraction*bkg_smooth #doesn't seem to work well. why not?
	corr.im = im_sig - background_subtraction*im_bkg
	'''
	if background_subtraction:
		corr.spectrum = 1*sig_smooth - 0.99*bkg_smooth #doesn't seem to work well. why not?
		corr.im = 1*im_sig - 0.99*im_bkg
	else:
		corr.spectrum = 1*sig_smooth - 0*bkg_smooth #doesn't seem to work well. why not?
		corr.im = 1*im_sig - 0*im_bkg
	'''
	corr.meta.parameters.update({"bkg_ts":bkg.ts})
	corr_dict.update({upv:corr})

#CHECK THAT ALL FILES HAVE SAME SPOT-SIZE DATA, AND FIND THAT SIZE
ss_ts_list = [corr_dict[x].meta.parameters["spot_size_ts"] for x in corr_dict]
spot_size_check = ss_ts_list.count(ss_ts_list[0]) == len(ss_ts_list)
if spot_size_check:
	spot_size_ts = ss_ts_list[0]
	ss_filename = timestamp_to_filename(spot_size_ts,file_end=spotsizefileend)
	ss_im = imread(ss_filename)
	im_raw_bw= ss_im[:,:,0] #red channel only
	x0ss,y0ss,dxss_half,dyss_half = mean_and_std_dev(im_raw_bw)
	dxss,dyss=dxss_half*2,dyss_half*2
	if dxss>x0ss: 
		dxss=x0ss-1
	elif dxss+x0ss>ss_im.shape[1]:
		dxss = ss_im.shape[1]-x0ss-1
	if dyss>y0ss: 
		dyss=y0ss-1
	elif dyss+y0ss>ss_im.shape[1]:
		dyss = ss_im.shape[1]-y0ss-1
	#
	px = point_grey_chameleon_pixel_size / magnification 
	print('fitting pump spot size image')
	fig,pars_fit = fit_and_plot_image(ss_im,spot_size_ts,x0ss,y0ss,dxss,dyss,px,fignum=5)
	(x0_fit,y0_fit,sxp_fit,syp_fit,tan_theta_fit,offset_fit,amplitude_fit) = pars_fit
	#We're interested in sxp_fit and syp_fit
	#figure(5),clf()
	#imshow(ss_im),title(spot_size_ts)

#--------------------------------
#LOAD, ANALYSE AND DISPLAY THE DATA
print "Loading and analysing data..."
Nvals = len(unique_par_vals)
figure(1),clf()
figure(2),clf()
figure(3),clf()
figure(4),clf()
plotfn = semilogy #could be "plot"
inferred_parameters=[]
for i in range(Nvals):
	upv = unique_par_vals[i]
	print variable_parameter +" = "+str(upv)
	#Load the data
	ex = corr_dict[upv] #Might work?
	###ex = ex_dict[upv][0]
	###ex.loadCameraData()
	###ex.loadSpectrometerData() #defaults to correcting for transmission vs wavelength
	label_str = ex.ts+"; "+str(upv)
	#---------------------
	#Image analysis
	weighted_im = sum([colour_weights[j]*ex.im[:,:,j] for j in range(ex.im.shape[-1])],0)
	cut_weighted_im = weighted_im[x0-dx:x0+dx,y0-dy:y0+dy]
	centre_find_im = weighted_im[x0-centre_find_dx:x0+centre_find_dx,y0-centre_find_dy:y0+centre_find_dy]
	#x,y,sx,sy = mean_and_std_dev(cut_weighted_im)
	x,y,sx,sy = mean_and_std_dev(centre_find_im)
	x = x + (dx-centre_find_dx)
	y = y + (dy-centre_find_dy)
	rad_prof = hene_utils.radial_profile(cut_weighted_im,(x,y),window_len=smooth_window_len)
	rs = arange(len(rad_prof))
	#Now fit with a Gaussian
	sig_guess = sqrt(sum((rs-0.)**2 * rad_prof)/len(rad_prof)) #the zero is to remind you that the gaussian has its centre fixed at zero
	off_guess = mean(rad_prof[-20:]) #Take last 20 points as background
	amp_guess = mean(rad_prof[:10]) -  off_guess #Take first 10 points as peak
	#Fails sometimes, when exceeding maxfev=800 function calls. Could be replaced by leastsq which fails less disastrously
	#fitpars, covmat = curve_fit(gaussian, rs, rad_prof, p0=(sig_guess,amp_guess,off_guess))
	fitpars, unknown_thingy = leastsq(gaussian_residuals, (sig_guess,amp_guess,off_guess), args=(rad_prof,rs))
	sig_fit,amp_fit,off_fit = fitpars
	#-----------------------
	#Spectrum analysis
	#Re-jig leastsq_range for shorter wavelength cutoffs.
	smoothed_spec = smooth(ex.spectrum, window_len=spec_smooth, window="flat")
	lam_max = ex.lamb[argmax(smoothed_spec)]
	#print lam_max
	pars_guess = (1e-9*lam_max,T_guess,spec_amplitude_guess,spec_offset_guess)
	leastsq_range = (lam_max+leastsq_range_adjust[0], lam_max+leastsq_range_adjust[1])
	spec_fit = fit_spectrum_thermal(ex.lamb,ex.spectrum,leastsq_range,pars_guess,smooth_window_len=spec_smooth)
	(lam0_fit,T_fit,spec_amplitude_fit,spec_offset_fit) = spec_fit
	#-------------------------------
	#Display
	#Images
	figure(1)
	subplot(ceil(Nvals/2.),2,i+1)
	imshow(cut_weighted_im),colorbar()
	title(label_str)
	#Radial profiles of images
	figure(2)
	plot(rad_prof,label=label_str)
	plot(rs,gaussian(rs,sig_fit,amp_fit,off_fit),label="fit for "+str(upv))
	xlabel("Radius (px)"),ylabel("Image profile (a.u.)")
	legend(loc="best",prop=fontProp),grid(1)
	#Spectra
	figure(4)
	subplot(ceil(Nvals/2.),2,i+1)
	mu=0
	plotfn(ex.lamb,number_distn(ex.lamb*1e-9,lam0_fit,T_fit,spec_amplitude_fit,mu,spec_offset_fit)\
		,label="fit, $\lambda_0=$"+str(round(lam0_fit*1e9,1))+" nm") #fitted spectrum
	for fignum in [3,4]:
		figure(fignum)
		plotfn(ex.lamb,smoothed_spec,label=label_str)
		xlabel("$\lambda$ (nm)"),ylabel("Spectrum (a.u.)")
		legend(loc="best",prop=fontProp),grid(1)
		xlim(xlimits),ylim(ylimits)
	
	#----------------------
	#Collect inferred parameters for later display
	inf_params = {"upv":upv,"x":x,"y":y,"sig_fit":sig_fit,"amp_fit":amp_fit,"off_fit":off_fit}
	inf_params.update({"lam0_fit":lam0_fit,"T_fit":T_fit})
	inferred_parameters.append(inf_params)

#-------------------------
#META ANALYSIS
#--------------------------
sigs_px = array([p["sig_fit"] for p in inferred_parameters])
#Should convert pixels to microns...
sigs_um = sigs_px * point_grey_chameleon_pixel_size / magnification 
par_vals = array([p["upv"] for p in inferred_parameters])
lam0_vals = array([p["lam0_fit"] for p in inferred_parameters])


sig_thermal_avg = thermal_size(q,T=T,RoC=RoC,lambda_0=580e-9) #should include inferred lam0 from spectra
figure(101),clf()
plot(par_vals,1e9*lam0_vals,"*-")
grid(1)
xlabel("set point (px)"), ylabel("Fitted $\lambda_0$ (nm)")
title(first_ts +" to "+last_ts)
if saving: savefig(first_ts+savename+"_cutoffs.png")


figure(102),clf()
plot(1e9*lam0_vals,1e6*sigs_um,"*")
plot(1e9*lam0_vals,1e6*thermal_size(q,T=T,RoC=RoC,lambda_0=lam0_vals))
xlabel("Fitted $\lambda_0$ (nm)"), ylabel("rms thermal spot size ($\mu$m)")
grid(1)
title(first_ts +" to "+last_ts+"\n"+"Pump spot: "+spot_size_ts+\
	"; Sizes "+str((round(sxp_fit,1),round(syp_fit,1)))+" $\mu$m")

annotate(str(ex.meta.parameters["concn_uM"])+" $\mu$M",\
	xy=(0.1, 0.9), xycoords='axes fraction',fontsize=18)
if saving: savefig(first_ts+savename+"_size_vs_lam0.png")


#EoF