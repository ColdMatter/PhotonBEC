#ipython --pylab
import time
from pbec_analysis import *


#INSTRUCTIONS TO USER
#run cavity stabiliser: you'll have to manually set it working. 
#close both FlyCap and AvaSoft applications
sleep_time_s = 20
ex_list = []
take_new_data = False
analyse_old_data = True
locked=False
base_comment = "Stability test; "
colour_weights=(1,1,0,0) #4-channel images


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

def time_number_from_timestamp(ts):
	#assumes includes no numbers after the decimal place
	#Only useful for plot purposes
	#YYYYMMDD,hhmmss,d=ts.split("_")
	YYYYMMDD,hhmmss=ts.split("_")
	hh,mm,ss=int(hhmmss[:2]),int(hhmmss[2:4]),int(hhmmss[-2:])
	#decimal_places = float("0."+d)
	seconds_today = 3600*hh + 60*mm + ss# + decimal_places
	return seconds_today

#loop over data acquisition...
if take_new_data:
	from pbec_experiment import *
	AOM_on, AOM_off = 0.9,0
	spectrometer_exposure_ms = 200
	for i in range(50):
		for (AOM_V,extra_comment) in [(AOM_on,"signal"),(AOM_off,"background")]:
			SingleChannelAO.SetAO0(AOM_V) #on voltage = 0.9
			res = get_single_image_and_spectrum("chameleon", spectrometer_exposure_ms)
			ex = Experiment(ts=res["ts"])
			ex.setCameraData(res["im"])
			ex.setSpectrometerData(res["lamb"],res["spectrum"])
			ex.meta.comments = base_comment + extra_comment
			ex.meta.parameters={"AOM_voltage":AOM_V,\
				"spectrometer_exposure_ms":spectrometer_exposure_ms}
			ex_list.append(ex)
			ex.saveAllData()
			print ex.ts + "\t"+extra_comment
		SingleChannelAO.SetAO0(AOM_on)
		time.sleep(sleep_time_s)
		
	plot_image_and_spectrum(ex,fignum=12)

#Now analyse
if analyse_old_data:
	from analyse_spectra import *
	data_date = "20140724"
	if locked:
		first_time,last_time = "114620","120811"
		locked_string = "locked"
	else:
		first_time,last_time = "125243","235959"
		locked_string = "unlocked"
	first_ts,last_ts = data_date+"_"+first_time,data_date+"_"+last_time
	ts_list = timestamps_in_range(first_ts,last_ts,extension = "_meta.json")
	ex_list = map(Experiment,ts_list)
	print "Loading data..."
	dump = [ex.meta.load() for ex in ex_list]
	dump = [ex.loadSpectrometerData() for ex in ex_list]
	#Divide up: signal and background
	sig_ex_list = filter(lambda x:x.meta.parameters["AOM_voltage"]!=0,ex_list)
	bkg_ex_list = filter(lambda x:x.meta.parameters["AOM_voltage"]==0,ex_list)
	paired_ex_list = zip(sig_ex_list,bkg_ex_list)
	#Combine into background-subtracted Experiment
	#NOTE: I don't use the images for anything. Maybe I shouldn't bother loading them.
	corrected_ex_list = []
	print "Analysing data..."
	for pair in paired_ex_list:
		c_ex = pair[0].copy()
		#Assumes "ex.lamb" is constistent.
		c_ex.spectrum =  pair[0].spectrum.copy()-pair[1].spectrum.copy()
		"""
		subtracted_images = pair[0].im.copy()-pair[1].im.copy() #may contain negative values!!!
		weighted_image = [colour_weights[i]*subtracted_images[:,:,i] for i in range(len(colour_weights))]
		c_ex.im =  sum(weighted_image,0) #turns into greyscale
		"""
		c_ex.meta.parameters.update({"bkg_ts":pair[1].ts})
		corrected_ex_list.append(c_ex)
	
	#Now fit for cutoff wavelength and amplitude
	leastsq_range = 570,600 #in nm
	(lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess) = (590e-9,300.,3e7, -100.*kB,500.)
	pars_guess = (lam0_guess,T_guess,amplitude_guess,mu_guess,offset_guess)
	pars_fit_list = []
	for c_ex in corrected_ex_list:
		pars_fit = fit_spectrum_BE_distn(c_ex.lamb,c_ex.spectrum,\
			leastsq_range,pars_guess,smooth_window_len=5)
		pars_fit_list.append(pars_fit)

	lam0_list = [pf[0] for pf in pars_fit_list]
	amplitude_list = [pf[2] for pf in pars_fit_list]
	c_ts_list = [c_ex.ts for c_ex in corrected_ex_list]
	plot_times = map(time_number_from_timestamp,c_ts_list)
	figure(112),clf()
	subplot(2,1,1)
	plot(plot_times, array(lam0_list)*1e9,"x")
	#xlabel("Time since midnight (s)"), 
	ylabel("$\lambda_0$ (nm)"),grid(1)
	subplot(2,1,2)
	plot(plot_times, array(amplitude_list),"x")
	xlabel("Time since midnight (s)"), ylabel("Amplitude (a.u.)"),grid(1)
	suptitle("Cavity "+locked_string+", data from "+ts_list[0]+" to "+ts_list[-1])
	savefig("summary_graph_"+locked_string+".png")
	std_dev_lam0 = std([l0 for l0 in lam0_list if not(isnan(l0))])
	print "Std. dev of lam0, when not nan is "+str(1e9*std_dev_lam0)+" nm"

#plot_image_and_spectrum(c_ex)