#ipython --pylab
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_analysis import *
from analyse_spectra import *
from matplotlib.font_manager import FontProperties
fontsize=8
fontProp = FontProperties(size = fontsize)

background_subtraction=False

data_date = "20140730"
first_time,last_time = "112813","235959"
variable_parameter = "laser_power_mW"
smooth_window_len =1
leastsq_range = 572,588 #wavelength range for fitting, in nm
(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (583e-9,3e3,300, -1.*kB,600.)
(gauss_width,gauss_amplitude)=0.4e-9, 100.
fitting=True
savename="power_variation"
fit_savename="power_variation_fit"
xlimits=(570,590)
ylimits=(700,3e4)
if background_subtraction:
	ylimits=(100,3e4)
	offset_guess=100

	
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
selected_indices = range(len(vals))
selected_indices=[0,1,3,4,7,8] #ignores samples with frequency excursions
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
		corr.spectrum = 1*sig_smooth - 0.7*bkg_smooth #doesn't seem to work well. why not?
	else:
		corr.spectrum = 1*sig_smooth - 0*bkg_smooth #doesn't seem to work well. why not?
	corr.meta.parameters.update({"bkg_ts":bkg.ts})
	corr_dict.update({val:corr})
	plotfn = [plot,semilogy][1]
	plotfn(corr.lamb,corr.spectrum,label=str(val)+" mW ;"+corr.ts)
	legend(loc="upper left",prop=fontProp)

xlim(xlimits),ylim(ylimits)
savefig(savename+"_"+ts_list[0]+".png")

if fitting:
#Now fit for cutoff wavelength and amplitude
	pars_guess = (lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess)
	pars_guess += (gauss_width,gauss_amplitude)
	pars_fit_dict = {}
	figure(22),clf()
	nvals = len(corr_dict)
	for i in range(nvals):
		k = sorted(corr_dict.keys())[i]
		corr = corr_dict[k]
		pars_fit = fit_spectrum_BE_distn(corr.lamb,corr.spectrum,\
			leastsq_range,pars_guess,smooth_window_len=5,include_gaussian=True)
		pars_fit_dict.update({k:pars_fit})
		subplot(2,ceil(nvals/2.),i+1)
		val = corr.meta.parameters[variable_parameter]
		plotfn(corr.lamb,corr.spectrum,label=str(val)+" mW ;"+corr.ts)
		#Plot the fit function
		thy_vals = number_dist_incl_gauss(corr.lamb*1e-9,*pars_fit)
		if isnan(pars_fit[6]):
			lab = "Fit failed"
		else:
			lab = "Fit; $N_{BEC}=$"+str(int(pars_fit[6]))
		plotfn(corr.lamb,thy_vals,label=lab) #Fitting needs SI units!
		xlim(xlimits)
		ylim(ylimits)
		legend(prop=FontProperties(size=7))
		xlabel("wavelength (nm)"), ylabel("spectrum (a.u.)")
		grid(1)

	lam0_list = [pars_fit_dict[k][0] for k in sorted(corr_dict.keys())]
	T_list = [pars_fit_dict[k][1] for k in sorted(corr_dict.keys())]
	mu_list = [pars_fit_dict[k][3] for k in sorted(corr_dict.keys())]
	bec_width_list = [pars_fit_dict[k][5] for k in sorted(corr_dict.keys())]
	Nbec_list = [pars_fit_dict[k][6] for k in sorted(corr_dict.keys())]
	
	savefig(fit_savename+"_"+ts_list[0]+".png")
