#ipython --pylab
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_analysis import *
from analyse_spectra import *
from matplotlib.font_manager import FontProperties
fontsize=8
fontProp = FontProperties(size = fontsize)

background_subtraction=True

selector=4
if selector==1:
	first_time,last_time = "123358","124747"
	(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (587.5e-9,200,1e13, +2800.*kB,1e5)
	resolution=0.4e-9
	xlimits=(565,595)
	ylimits=(20e4,1e9)
	leastsq_range = 560,600 #wavelength range for fitting, in nm
	selected_indices=[0,1,2,3,4,5,6,7,8,9,10,11,13,14,15]
	smooth_window_len =1
elif selector==2:
	data_date = "20140731"
	first_time,last_time = "130223","131158"
	(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (594e-9,100,1e14, +2800.*kB,1e5)
	resolution=0.4e-9
	xlimits=(560,605)
	ylimits=(1e6,1e9)
	leastsq_range = 560,597 #wavelength range for fitting, in nm
	selected_indices=[1,2,4,5,6,7,9,10,11,12]
	smooth_window_len =3
	#Why does this need broadening to stabilise the fit?
elif selector==3:
	data_date = "20140730"
	first_time,last_time = "112813","113510"
	(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (583.2e-9,100,1e13, +800.*kB,1e5)
	resolution=0.18e-9
	xlimits=(565,595)
	ylimits=(2e5,1e9)
	leastsq_range = 565,600 #wavelength range for fitting, in nm
	selected_indices=[0,1,3,4,7,8] #ignores samples with frequency excursions
	smooth_window_len =1
elif selector==4:
	data_date = "20140731"
	first_time,last_time = "161943","235959"
	(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (587.5e-9,100,1e13, +2800.*kB,1e5)
	resolution=0.4e-9
	xlimits=(565,595)
	ylimits=(20e4,1e9)
	leastsq_range = 565,595 #wavelength range for fitting, in nm
	selected_indices=[0,1,2,3,4,5,6,8,9,11,12,14,15,16]
	smooth_window_len =4
	#Why does this need broadening to stabilise the fit?


variable_parameter = "laser_power_mW"
#(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (583e-9,3e3,300, -1.*kB,600.)
fitting=True
savename="power_variation"
fit_savename="power_variation_fit"

	
#Start loading the data
first_ts,last_ts = data_date+"_"+first_time,data_date+"_"+last_time
ts_list = timestamps_in_range(first_ts,last_ts,extension = "_meta.json")
ex_list = map(Experiment,ts_list)
print "Loading data..."
dump = [ex.meta.load() for ex in ex_list] #needed now for sorting through experiments
dump = [ex.loadSpectrometerData() for ex in ex_list] #this could be left until later.
#Currently does not load camera data, as it's a bit heavy, and not quite what I'm interested in first up

#Sort into bundles of equal variable_paramater
par_vals = map(lambda x:x.meta.parameters[variable_parameter],ex_list)
unique_par_vals = set(par_vals) #does not preserve order
#keys of ex_dict are values of the variable_parameter
#values of ex_dict are lists of signal and background experiments, bundled in a 2-item dict
ex_dict={}
for upv in unique_par_vals:
	selected_ex_list = filter(lambda x:x.meta.parameters[variable_parameter]==upv,ex_list)
	sig_ex_list = filter(lambda x:x.meta.parameters["AOM_voltage"]!=0,selected_ex_list)
	bkg_ex_list = filter(lambda x:x.meta.parameters["AOM_voltage"]==0,selected_ex_list)
	ex_pair = {"sig":sig_ex_list, "bkg":bkg_ex_list}
	ex_dict.update({upv:ex_pair})

#Now correct for background. Also, here would be a good place to do any averaging, if needed
corr_dict = {}
figure(1),clf()
xlabel("wavelength (nm)"), ylabel("spectrum (a.u.)")
grid(1)
vals = sorted(ex_dict.keys())
if selected_indices==None:
	selected_indices = range(len(vals))

selected_vals = [vals[si] for si in selected_indices]
for val in selected_vals:
	sel = ex_dict[val]
	#Assume there is only one experiment for each parameter, i.e. no averaging
	i=0
	sig,bkg = sel["sig"][i],sel["bkg"][i]
	corr = sig.copy() #a background-corrected Experiment object
	sig_smooth = smooth(sig.spectrum,window_len=smooth_window_len)
	bkg_smooth = smooth(bkg.spectrum,window_len=smooth_window_len)
	if background_subtraction:
		corr.spectrum = 1*sig_smooth - 0.9*bkg_smooth #doesn't seem to work well. why not?
	else:
		corr.spectrum = 1*sig_smooth - 0*bkg_smooth #doesn't seem to work well. why not?
	corr.meta.parameters.update({"bkg_ts":bkg.ts})
	corr_dict.update({val:corr})
	plotfn = [plot,semilogy][1]
	plotfn(corr.lamb,corr.spectrum,label=str(val)+" mW ;"+corr.ts)
	legend(loc="upper left",prop=fontProp)

xlim(xlimits),ylim(ylimits)
savefig(savename+"_"+ts_list[0]+".png")

#-------------------------------
#Define the fitting function
#Based on BE-distribution
#Distribution is convolved with an instrumental resolution, so no singularities.
def number_distn_BE(lams, resolution, lam0, T, amplitude, mu, offset):
	"""
	Locally	defined function, hence the strange name
	Force mu < 0, then add a BEC by hand if and only if mu > mu_crit
	"""
	mu_crit = -0.01 * kB*T #a guess
	mu_ceil = min(mu,mu_crit)
	normalisation = 1./(resolution * sqrt(2*pi))
	#lams: wavelengths
	#lam0: cutoff wavelengths, corresponding to minimum accesible energy
	ll = lam0 / lams
	const = constants.h * constants.c / lam0
	DoS = const * (ll-1) * (ll>1) #returns zero for energies below cutoff, lam0
	de_dlam = (const / lam0) * (ll**2) #a minus sign, deliberately dropped here
	distn = 1.0/ (exp(+(const*(ll-1) - mu_ceil)/(kB*T) )  -1)
	num = amplitude*DoS*distn*de_dlam
	thermal_popn = num/constants.h #does this have the correct units
	thermal_popn = thermal_popn*(thermal_popn>0) + (offset/normalisation) #positive only
	#
	#Detector resolution function
	ind = shape(lams)[0]/2
	dlam = lams[ind+1]-lams[ind]
	lams_det = arange(-4*resolution,+4*resolution,dlam)
	detector_function=normalisation*exp(-lams_det**2 / (2* resolution**2)) #Gaussian.
	
	#And add a condensate
	#Should be a smooth transition....
	#How about, if mu>mu_crit, then use mu as a surrogate for nBEC
	#Better option: nBEC = exp(mu/(kB*T)), the fugacity, albeit a massive hack.
	fugacity = exp(mu/(kB*T))
	nBEC = fugacity #HACK! MASSIVE HACK!
	bec_signal = nBEC * amplitude* normalisation*exp(-(lams-lam0)**2 / (2* resolution**2))
	
	#Broaden the underlying population and add the BEC
	detector_response = convolve(thermal_popn,detector_function,mode="same") + bec_signal

	return detector_response

#Overwrite the function in analyse_spectra.py
def number_dist_residuals_BE(pars, ydata, xdata,resolution):
	#Takes 5 parameters. Calculated residuals in log space
	return (log(number_distn_BE(xdata, resolution, *pars)) - log(ydata))**2

def fit_spectrum_BE_distn(xdata,ydata,resolution,leastsq_range,pars_guess,include_gaussian=False,smooth_window_len=5,smooth_window="flat"):
	ydata_smooth = smooth(ydata, window_len=smooth_window_len, window=smooth_window)
	#
	#crop data so it the leastsq fit only considers the datapoints in wavelength range leastsq_range[index]
	data_smooth = zip(xdata, ydata_smooth)
	sliced_data_smooth = [x for x in data_smooth if x[0] >= leastsq_range[0] and x[0] <= leastsq_range[1]]
	sliced_xdata, sliced_ydata_smooth = array(zip(*sliced_data_smooth))
	
	thy_function = number_dist_residuals_BE
	lssolution = leastsq(thy_function, pars_guess, args=(sliced_ydata_smooth, 1e-9*sliced_xdata,resolution))
	(lam0,T,amplitude,mu,offset) = lssolution[0]
	return lssolution[0]



if fitting:
#Now fit for cutoff wavelength and amplitude
	pars_guess = (lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess)
	pars_fit_dict = {}
	figure(22),clf()
	nvals = len(corr_dict)
	for i in range(nvals):
		k = sorted(corr_dict.keys())[i]
		corr = corr_dict[k]
		pars_fit = fit_spectrum_BE_distn(corr.lamb,corr.spectrum,resolution,\
			leastsq_range,pars_guess,smooth_window_len=smooth_window_len,include_gaussian=True)
		pars_fit_dict.update({k:pars_fit})
		subplot(2,ceil(nvals/2.),i+1)
		val = corr.meta.parameters[variable_parameter]
		plotfn(corr.lamb,corr.spectrum,label=str(val)+" mW ;"+corr.ts)
		#Plot the fit function
		thy_vals = number_distn_BE(corr.lamb*1e-9,resolution,*pars_fit)

		try:
			lab = "Fit; $\mu=$"+str(int(round(pars_fit[3]/kB)))+" K"
			lab += "; $T=$"+str(int(round(pars_fit[1])))+" K"
		except:
			lab = "Fit failed"
		plotfn(corr.lamb,thy_vals,label=lab) #Fitting needs SI units!
		xlim(xlimits)
		ylim(ylimits)
		legend(prop=FontProperties(size=7))
		xlabel("wavelength (nm)"), ylabel("spectrum (a.u.)")
		grid(1)

	lam0_list = [pars_fit_dict[k][0] for k in sorted(corr_dict.keys())]
	T_list = [pars_fit_dict[k][1] for k in sorted(corr_dict.keys())]
	amplitude_list = [pars_fit_dict[k][2] for k in sorted(corr_dict.keys())]
	mu_list = [pars_fit_dict[k][3] for k in sorted(corr_dict.keys())]
	offset_list = [pars_fit_dict[k][4] for k in sorted(corr_dict.keys())]
	
	savefig(fit_savename+"_"+ts_list[0]+".png")

#TESTING ARE FOR NEW FIT FUNCTION
"""
figure(43),clf()
lams = corr.lamb
resolution = 0.4e-9
lam0=583*1e-9
T = 100
amplitude = 1
mu = 3000*kB
offset = 1e6
#nBEC=1e6
vals = number_distn_BE(1e-9*lams, resolution, lam0, T, amplitude, mu, offset)
semilogy(lams,vals)
xlim(530,590)
"""

figure(102),clf()
subplot(2,1,1)
plot(selected_vals, array(mu_list)/kB,"*")
xlabel(variable_parameter)
ylabel("$\mu / k_B$ (K)")
grid(1)
subplot(2,1,2)
plot(selected_vals, array(T_list),"*")
xlabel(variable_parameter)
ylabel("$T$ (K)")
grid(1)

#EoF
