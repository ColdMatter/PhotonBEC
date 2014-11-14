import sys
sys.path.append("Y:\\Control\\PythonPackages\\")
from pbec_analysis import *

colour_weights=(1,1,0,0)
lam_lims = (550,620)
#spatial_ROI=(520,730)
#data_date ="20141111"
#first_time,last_time="130218","130241"

#spatial_ROI=(500,750)
#lam_lims = (560,610)
#first_date ="20141112"
#first_time,last_time="114007","114035"
#ts_list = timestamps_in_range(data_date+"_"+first_time,data_date+"_"+last_time,extension="_meta.json")
first_ts,last_ts = "20141111_130218", "20141112_114035"
ts_list = timestamps_in_range(first_ts,last_ts,extension="_meta.json")

ex_list = map(Experiment,ts_list)

#ex = Experiment(ts)
#ex.loadAllData()

def DisplayExperiment(ex,fignum=1234):
	#For now, assumes that image and spectrum data are present
	figure(fignum)
	clf()
	subplot(2,1,1)
	suptitle(ex.ts)
	imshow(sqrt(ex.im))
	#
	subplot(2,1,2)
	semilogy(ex.lamb,ex.spectrum)
	xlabel("$\lambda$ (nm)"),ylabel("spectrum")

#Attempt to calibrate
#RULE: always adjust the 2D data; leave the spectrometer data untouched
#xim=pixel number
#lam = spectrometer-calibrated wavelength in nm
#a = constant of proportionality
#lam0=offset wavelength, for pixel #0
#lam = a*xim + lam0
#NOTE: lam0 ~ 550 seems like a good guess; a = 0.01 nm per pixel seems order-of-magnitude
a = 0.025
lam0=562
bkg = 13
xims = arange(len(spectrum_1D))*a + lam0
amplitude=130

Nval = len(ex_list)
figure(1),clf()
figure(2),clf()
figure(3),clf()
for i in range(Nval):
	ex = ex_list[i]
	print ex.ts
	ex.meta.load()
	ex.loadCameraData()
	ex.loadSpectrometerData(correct_transmission=False)
	figure(1)
	subplot(Nval,1,i+1)
	semilogy(ex.lamb,ex.spectrum,label=ex.ts)
	xlabel("$\lambda$ (nm)")
	#ylim(500,3000)
	xlim(lam_lims),legend(loc="lower center")
	ylabel("extra-cavity spectrum")
	#
	display_im = sum(ex.im[spatial_ROI[0]:spatial_ROI[1],:,:]* colour_weights,2)
	figure(2)
	subplot(Nval,2,2*i-1)
	imshow(display_im,label=ex.ts),colorbar()
	subplot(Nval,2,2*i)
	spectrum_1D=sum(display_im,0)
	semilogy(spectrum_1D,label=ex.ts),legend(loc="best")
	xlabel("$\lambda$ (NOT CALIBRATED)")

	figure(3)
	subplot(Nval,1,i+1)
	semilogy(ex.lamb,ex.spectrum,label=ex.ts+" spectrometer")
	semilogy(xims,amplitude*(spectrum_1D - bkg),label=ex.ts+" 2D, "+str(ex.meta.parameters["lock_set_point"]))
	legend(loc="best",prop={"size":9})
	xlim(lam_lims),ylim(100,10000)

figure(3), xlabel("$\lambda$ (nm)")

#EoF
