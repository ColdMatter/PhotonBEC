#ipython --pylab
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_analysis import *
from analyse_spectra import *

data_date = "20140725"
#first_time,last_time = "113630","113854"
first_time,last_time = "123722","123948"
variable_parameter = "laser_power_mW"
smooth_window_len =1


#A useful function or two
def plot_image_and_spectrum(ex,fignum=12):
	figure(fignum)
	suptitle(ex.ts)
	subplot(2,1,1)
	imshow(ex.im) #deals with negative values coming up in background subtraction in an entirely graceless manner
	subplot(2,1,2)
	semilogy(ex.lamb,ex.spectrum)
	xlabel("wavelength (nm)"), ylabel("spectrum (a.u.)")
	grid(1)

def plot_spectrum(ex,fignum=13):
	figure(fignum)
	title(ex.ts)
	semilogy(ex.lamb,ex.spectrum)
	xlabel("wavelength (nm)"), ylabel("spectrum (a.u.)")
	grid(1)

	
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
for val in ex_dict:
	sel = ex_dict[val]
	#Assume there is only one experiment for each parameter, i.e. no averaging
	i=0
	sig,bkg = sel["sig"][i],sel["bkg"][i]
	corr = sig.copy() #a background-corrected Experiment object
	sig_smooth = smooth(sig.spectrum,window_len=smooth_window_len)
	bkg_smooth = smooth(bkg.spectrum,window_len=smooth_window_len)
	corr.spectrum = sig_smooth - bkg_smooth
	#corr.spectrum = sig.spectrum.copy() - bkg.spectrum.copy()
	corr.meta.parameters.update({"bkg_ts":bkg.ts})
	corr_dict.update({val:corr})
	semilogy(corr.lamb,corr.spectrum,label=str(val)+" mW ;"+corr.ts)
	legend(loc="lower center")

xlim(525,610),ylim(1,1e4)

#Now fit for cutoff wavelength and amplitude
#leastsq_range = 570,600 #in nm
#(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (590e-9,300.,3e7, -100.*kB,500.)
#pars_guess = (lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess)
#pars_fit_list = []
#for k in corr_dict:
#	corr = corr_dict[k]
#	pars_fit = fit_spectrum_BE_distn(corr.lamb,corr.spectrum,\
#		leastsq_range,pars_guess,smooth_window_len=5)
#	pars_fit_list.append(pars_fit)
#
#lam0_list = [pf[0] for pf in pars_fit_list]
#plot_image_and_spectrum(c_ex)