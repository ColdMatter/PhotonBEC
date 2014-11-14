from pbec_analysis import *
from scipy.optimize import leastsq
from matplotlib.font_manager import FontProperties
fontsize=6
fontProp = FontProperties(size = fontsize)

#TODO: make compatible with pbec_analysis
def number_dist_incl_gauss(lam, lam0, T, n_amp, mu, offset, g_width, g_amp):
	return (number_distn(lam, lam0, T, n_amp, mu, 0)
		+ g_amp*exp(-1 * (lam - lam0)**2 / (2*g_width*g_width))
		+ offset)
	

def number_dist_residuals_incl_gauss(pars, ydata, xdata):
	#Takes 7 parameters
	#return (number_dist_incl_gauss(xdata, *pars) - ydata)**2
	return (log(number_dist_incl_gauss(xdata, *pars)) - log(ydata))**2

def number_dist_residuals_excl_gauss(pars, ydata, xdata):
	#Takes 5 parameters
	#return (number_distn(xdata, *pars) - ydata)**2
	return (log(number_distn(xdata, *pars)) - log(ydata))**2

#-------------------
def fit_spectrum_BE_distn(xdata,ydata,leastsq_range,pars_guess,include_gaussian=False,smooth_window_len=5,smooth_window="flat"):
	ydata_smooth = smooth(ydata, window_len=smooth_window_len, window=smooth_window)
	#
	#crop data so it the leastsq fit only considers the datapoints in wavelength range leastsq_range[index]
	data_smooth = zip(xdata, ydata_smooth)
	sliced_data_smooth = [x for x in data_smooth if x[0] >= leastsq_range[0] and x[0] <= leastsq_range[1]]
	sliced_xdata, sliced_ydata_smooth = array(zip(*sliced_data_smooth))
	
	if include_gaussian:
		#pars_guess = (lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess,gaussian_width_guess,gaussian_amplitude_guess)
		lssolution = leastsq(number_dist_residuals_incl_gauss, pars_guess, args=(sliced_ydata_smooth, 1e-9*sliced_xdata))
		(lam0,T,amplitude,mu,offset,gaussian_width,gaussian_amplitude) = lssolution[0]
	else:
		#pars_guess = (lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess)
		lssolution = leastsq(number_dist_residuals_excl_gauss, pars_guess, args=(sliced_ydata_smooth, 1e-9*sliced_xdata))
		(lam0,T,amplitude,mu,offset) = lssolution[0]
	return lssolution[0]


def fit_and_plot_spectrum(xdata,ydata,leastsq_range,pars_guess,include_gaussian=False,smooth_window_len=5,smooth_window="flat",fignum=None,clear_fig=False,label="",fit_label=""):
	if include_gaussian:
		thy_function = number_dist_incl_gauss
	else:
		thy_function = number_distn
	#
	fit_vals = fit_spectrum_BE_distn(xdata,ydata,leastsq_range,pars_guess,include_gaussian=include_gaussian,smooth_window_len=smooth_window_len,smooth_window=smooth_window)
		#--------------------------------------
	#OPTIONAL PLOTTING OF INDIVIDUAL SPECTRA
	if fignum!=None: figure(fignum)
	#subplot(4,4,q)
	thy_vals = thy_function(1e-9*xdata,*fit_vals)
	ydata_smooth = smooth(ydata, window_len=smooth_window_len, window=smooth_window)
	semilogy(xdata,ydata,label=label)
	#semilogy(xdata,thy_vals,label="T="+str(fit_vals[1]))
	plot_label="T="+str(round(fit_vals[1],1))+" K"
	if fit_label=="lam0":
	    plot_label+=" ;lam0="+str(round(1e9*fit_vals[0],1))+" nm"
	semilogy(xdata,thy_vals,label=plot_label)
	#ylim(3e5,1e8)
	#xlim(spectrum_plot_range)
	legend(loc="best",prop=fontProp)
	#----------------------------------------
	return fit_vals,thy_function
