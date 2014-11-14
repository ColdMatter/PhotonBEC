#ipython --pylab
import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_analysis import *
from analyse_spectra import *
from matplotlib.font_manager import FontProperties
fontsize=8
fontProp = FontProperties(size = fontsize)
from analyse_images import *
from threshold_image_fitting import *

background_subtraction=True

selector=2
if selector==1:
	data_date = "20140804"
	#first_time,last_time = "122200","122928"
	#first_time,last_time = "125823","130927"
	first_time,last_time = "143832","235959"
	(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (595e-9,100,1e13, +2800.*kB,1e5)
	resolution=0.2e-9 #spectrometer
	xlimits=(570,605)
	ylimits=(20e4,1e9)
	leastsq_range = 570,605 #wavelength range for fitting, in nm
	selected_indices=None
	smooth_window_len =2
	load_images = True
	colour_weights = (1,0,0,0)
	x0,y0= 540,675 #centre x0 and y0
	dx,dy= 210,190 #half-size of roi dx and dy
	plot_x=False #False means plot y
	magnification = 3.7 #approximate. Not calibrated since May 2014
	fitting_spectra=False
	fitting_images=True
	mask_dx,mask_dy=65,60
	integ = 2 #half number of lines to integrate over to improve SNR. Display only, not fitting.
	mask_roi = [dx-mask_dx,dx+mask_dx,dy-mask_dy,dy+mask_dy] #mask is within full RoI
	fill_max = 1 #display for image cuts and fits
if selector==2:
	data_date = "20140804"
	first_time,last_time = "143832","144747"
	(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (595e-9,100,1e13, +2800.*kB,1e5)
	resolution=0.2e-9 #spectrometer
	xlimits=(570,605)
	ylimits=(20e4,1e9)
	leastsq_range = 570,605 #wavelength range for fitting, in nm
	#selected_indices=[0,4,8]
	selected_indices=None
	smooth_window_len =2
	load_images = True
	colour_weights = (1,0,0,0)
	x0,y0= 520,665 #centre x0 and y0
	dx,dy= 200,180 #half-size of roi dx and dy
	plot_x=True #False means plot y
	magnification = 3.7 #approximate. Not calibrated since May 2014
	fitting_spectra=False
	fitting_images=True
	mask_dx,mask_dy=45,45
	integ = 2 #half number of lines to integrate over to improve SNR. Display only, not fitting.
	mask_roi = [dx-mask_dx,dx+mask_dx,dy-mask_dy,dy+mask_dy] #mask is within full RoI
	fill_max = 0.4 #display for image cuts and fits.
	
variable_parameter = "laser_power_mW"
#(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (583e-9,3e3,300, -1.*kB,600.)
savename="power_variation"
fit_savename=savename+"_fit"
images_savename=savename+"_images"
cuts_savename= savename+"_cuts"
residuals_savename = savename+"_residuals"
#Start loading the data
first_ts,last_ts = data_date+"_"+first_time,data_date+"_"+last_time
ts_list = timestamps_in_range(first_ts,last_ts,extension = "_meta.json")
ex_list = map(Experiment,ts_list)
print "Loading data..."
dump = [ex.meta.load() for ex in ex_list] #needed now for sorting through experiments
#dump = [ex.loadSpectrometerData() for ex in ex_list] #this could be left until later.
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
	#Now reject all pairs where any of the sig or bkg has a camera error
	camera_errors_list = [x.meta.parameters["camera_errors"] for x in selected_ex_list]
	#Nerrors = len(filter(None,camera_errors_list))
	filter_func = lambda x:x==str(None)
	Nerrors = len(filter(lambda x:x!="None",camera_errors_list))
	#If an error is found in any of the experiments for this parameter value, reject the parameter value entirely.
	if Nerrors == 0:
		ex_dict.update({upv:ex_pair})
	else:
		print "Camera errors found for parameter value "+str(upv)

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
	for ex in [sig,bkg]:
		ex.loadSpectrometerData()
		#if load_images: ex.loadCameraData()
	corr = sig.copy() #a background-corrected Experiment object
	sig_smooth = smooth(sig.spectrum,window_len=smooth_window_len)
	bkg_smooth = smooth(bkg.spectrum,window_len=smooth_window_len)
	if background_subtraction:
		corr.spectrum = 1*sig_smooth - 0.99*bkg_smooth #doesn't seem to work well. why not?
	else:
		corr.spectrum = 1*sig_smooth - 0*bkg_smooth #doesn't seem to work well. why not?
	corr.meta.parameters.update({"bkg_ts":bkg.ts})
	corr_dict.update({val:corr})
	plotfn = [plot,semilogy][1]
	plotfn(corr.lamb,corr.spectrum,label=str(val)+" mW ;"+corr.ts)
	legend(loc="upper left",prop=fontProp)

xlim(xlimits),ylim(ylimits)
savefig(ts_list[0]+"_"+savename+".png")

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



if fitting_spectra:
	print "Fitting spectra..."
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
	
	savefig(ts_list[0]+"_"+fit_savename+".png")


#NOW DEAL WITH IMAGE DATA
figure(321),clf()
if fitting_images: figure(322),clf()
nvals = len(corr_dict)
residuals_unmasked_dict={}
residuals_masked_dict={}
sums_dict={}
sums_unmasked_dict={}
for i in range(nvals):
	print "Parameter value "+str(selected_vals[i]),
	corr = corr_dict[selected_vals[i]]
	sig = Experiment(corr.ts)
	bkg = Experiment(corr.meta.parameters["bkg_ts"])
	for ex in [sig,bkg]:
		ex.meta.load()
		ex.loadCameraData()
	
	corr.im = sig.im
	if background_subtraction: corr.im = 1*sig.im - 1.0*bkg.im
	
	figure(321);subplot(4,ceil(nvals/4.),i+1)
	weighted_im = sum([colour_weights[j]*corr.im[:,:,j] for j in range(corr.im.shape[-1])],0)
	display_im=weighted_im[x0-dx:x0+dx,y0-dy:y0+dy]
	imshow(display_im)
	title(corr.ts+", "+str(corr.meta.parameters[variable_parameter]) + " mW",fontsize=8)

	if fitting_images:
		print "...fitting images..."
		figure(322)
		#subplot(4,ceil(nvals/4.),i+1)
		if integ==0:
			display_line_x = weighted_im[x0-dx:x0+dx,y0         ]
			display_line_y = weighted_im[x0         ,y0-dy:y0+dy]
		else:
			display_line_x = mean(weighted_im[x0-dx:x0+dx       ,y0-integ:y0+integ],1)
			display_line_y = mean(weighted_im[x0-integ:x0+integ ,y0-dy:y0+dy      ],0)
		
		display_line=display_line_y
		coord_name="y"
		if plot_x: 
			display_line=display_line_x
			coord_name="x"
		coord_vals = arange(len(display_line))*1e6*point_grey_chameleon_pixel_size / magnification
		plot(coord_vals, display_line,\
			label=corr.ts+"; "+str(corr.meta.parameters[variable_parameter]) + " mW")

		lab = "Fit: "+str(corr.meta.parameters[variable_parameter]) + " mW"
		#(fit_vals,fit_func) = fit_gaussian_to_image(display_im,maxfev=100)
		(fit_vals,fit_func,mask) = fit_gaussian_to_image_masked(display_im,mask_roi,maxfev=100)
		if plot_x:
			coord_fit = fit_vals[0]*1e6*point_grey_chameleon_pixel_size / magnification
			plot(fit_func(coord_vals,coord_fit),label=lab)
			#Grey out area which is masked in the fit
			#fill_between(arange(len(display_line)),0,1,where=mask[dx,:],facecolor="black",alpha=0.1)
		else:
			coord_fit=fit_vals[1]*1e6*point_grey_chameleon_pixel_size / magnification
			plot(fit_func(coord_fit,coord_vals),label=lab)
			#Grey out area which is masked in the fit
			#fill_between(arange(len(display_line)),0,1,where=mask[:,dy],facecolor="black",alpha=0.1)
		#
		Npx,Npy=display_im.shape
		XX,YY = meshgrid(range(Npx),range(Npy))
		fit_im = transpose(fit_func(XX,YY))
		#
		res = display_im-fit_im
		im_unmasked = ma.masked_array(display_im,mask = transpose(1-mask))
		res_masked = ma.masked_array(res,mask = transpose(mask))
		res_unmasked = ma.masked_array(res,mask = transpose(1-mask))
		sum_unmasked_residuals=ma.sum(res_unmasked)
		sum_masked_residuals=ma.sum(res_masked)
		sum_all = sum(display_im)
		sum_unmasked = ma.sum(im_unmasked)
		residuals_unmasked_dict.update({corr.meta.parameters[variable_parameter]:sum_unmasked_residuals})
		residuals_masked_dict.update({corr.meta.parameters[variable_parameter]:sum_masked_residuals})
		sums_dict.update({corr.meta.parameters[variable_parameter]:sum_all})
		sums_unmasked_dict.update({corr.meta.parameters[variable_parameter]:sum_unmasked})
		xlabel(coord_name + " $ / \mu$m")
		legend(prop=fontProp)
		legend(prop=fontProp)
		grid(1)

if fitting_images:
	#Demonstrate mask
	#fill_max = sum(colour_weights)#
	if plot_x:
		fill_between(arange(len(display_line)),0,fill_max,\
			where=mask[dx,:],facecolor="black",alpha=0.1)
	else:
		fill_between(arange(len(display_line)),0,fill_max,\
			where=mask[:,dy],facecolor="black",alpha=0.1)

	title("grey area is masked out for gaussian fit to wings")

	figure(323),clf()
	ps = array(sorted(residuals_unmasked_dict.keys()))
	rs_unmasked = array([residuals_unmasked_dict[p] for p in ps])
	rs_masked = array([residuals_masked_dict[p] for p in ps])
	rs_all = array([sums_dict[p] for p in ps])
	rs_sum_unmasked = array([sums_unmasked_dict[p] for p in ps])

	plot(ps,rs_unmasked,"*:",label="Residual Inside mask")
	#plot(ps,rs_masked,"*:",label="Residual Outside mask")
	#plot(ps,rs_all,"*:",label="Sum over image")
	plot(ps,rs_sum_unmasked,"*:",label="Sum inside mask")
	xlabel("Power (mW)"),ylabel("Residual of masked image fit")
	legend(loc="upper left")
	grid(1)
	title(first_ts+" to "+last_ts)

	for (fn,sn) in [(321,images_savename),(322, cuts_savename),(323, residuals_savename)]:
		figure(fn)
		savefig(ts_list[0]+"_"+sn+".png")


	
	
#EoF
