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
from scipy.optimize import curve_fit


saving=True
#PARAMETERS FOR EACH DATA SET
selector=1
if selector==1:
	first_time,last_time = "110045","110117"
if selector==2:
	first_time,last_time = "123353","123715"

#PARAMETERS COMMON TO ALL DATA SETS
data_date = "20140821"
ylimits=(1e7,1e9)
colour_weights = (1,0,0,0)
x0,y0= 400,600 #centre x0 and y0
dx,dy= 300,300 #half-size of roi dx and dy
#dx,dy= 150,150 #half-size of roi dx and dy
centre_find_dx,centre_find_dy=100,100
smooth_window_len = 1 #for radial profiles
magnification = 3.4 #measured 4/8/14
#Guesses for spectrum fitting
(lam0_guess,T_guess,spec_amplitude_guess,spec_offset_guess) = (575-9,200,1e7,1e8)
	#NOTE: lam0_guess is completely ignored
#leastsq_range = 540,615 #wavelength range for fitting, in nm
leastsq_range_adjust = -40,10 #wavelength range for fitting, in nm
xlimits=(540,622) #for spectra
spec_smooth=10

variable_parameter = "set_point"
savename="thermal_spot_size"

#---------------------
#USEFUL FUNCTIONS
def gaussian(r,sig,amp,off):
	#This particular Gaussian is fixed to have its centre at zero
	return off + amp*exp(-r**2 / (2*sig**2))

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
	lam_max =1e-9*sliced_xdata[argmax(sliced_ydata_smooth)] -5e-9#stupid nm <-> m conversion
	pg = list(pars_guess)
	pg[0]=lam_max #HACK! override initial guess!!!!!
	pars_guess = tuple(pg)
	#
	thy_function = number_dist_residuals
	lssolution = leastsq(thy_function, pars_guess, args=(sliced_ydata_smooth, 1e-9*sliced_xdata))
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

#Parcel out the experiments
ex_dict={}
for upv in unique_par_vals:
	selected_ex_list = filter(lambda x:x.meta.parameters[variable_parameter]==upv,ex_list)
	#Now reject all parameters where any of the data has a camera error
	camera_errors_list = [x.meta.parameters["camera_errors"] for x in selected_ex_list]
	filter_func = lambda x:x==str(None)
	Nerrors = len(filter(lambda x:x!="None",camera_errors_list))
	if Nerrors == 0:
		ex_dict.update({upv:selected_ex_list})
	else:
		print "Camera errors found for parameter value "+str(upv)

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
	ex = ex_dict[upv][0]
	label_str = ex.ts+"; "+str(upv)
	#Load the data
	ex.loadCameraData()
	ex.loadSpectrometerData() #defaults to correcting for transmission vs wavelength
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
	fitpars, covmat = curve_fit(gaussian, rs, rad_prof, p0=(sig_guess,amp_guess,off_guess))
	sig_fit,amp_fit,off_fit = fitpars
	#-----------------------
	#Spectrum analysis
	pars_guess = (lam0_guess,T_guess,spec_amplitude_guess,spec_offset_guess)
	#Re-jig leastsq_range for shorter wavelength cutoffs.
	smoothed_spec = smooth(ex.spectrum, window_len=spec_smooth, window="flat")
	lam_max = ex.lamb[argmax(smoothed_spec)]
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
if saving: savefig(savename+"_cutoffs.png")


figure(102),clf()
plot(1e9*lam0_vals,1e6*sigs_um,"*")
plot(1e9*lam0_vals,1e6*thermal_size(q,T=T,RoC=RoC,lambda_0=lam0_vals))
xlabel("Fitted $\lambda_0$ (nm)"), ylabel("rms thermal spot size ($\mu$m)")
grid(1)
title(first_ts +" to "+last_ts)

if saving: savefig(savename+"_size_vs_lam0.png")


#EoF