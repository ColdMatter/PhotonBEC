#----------------------------------
#SignalDataModule.py
#Created 15/10/2009 by Rob Nyman
#----------------------------------
#This code is distributed under the Destructive Uncommons license
#which means that there is at least a 2% likelihood that some damage
#will be done to your computer or your reputation, and that the 
#author(s) take no blame.
#----------------------------------
#Modifications
#Date		Modification
#--/--/--
#
#NOTE: When plotting spectra, use plot( signaldata.f, fftshift(signaldata.sf)) , and please don't ask too many questions. 

from scipy import *
from scipy.signal import resample
from numpy import *
from numpy.fft import *
from matplotlib.pyplot import *
from matplotlib.mlab import find

class SignalData:
    """
    A class to help with signal analysis, transforms and filtering.
    Only takes 1D signals
    Time domain: time linearly spaced from zero forward
    Freq domain: freq linearly spaced from -fmax to +fmax

    Example code:
    --------------
    from SignalDataModule import SignalData
    t=linspace(0,8,1000)
    st=[sin(2*pi*tt)+sin(20*pi*tt) for tt in t]
    sig=SignalData(t=t,st=st)
    subplot(2,1,1),plot(sig.t,sig.st)
    (f,sf)=sig.ForwardFourierTransform()
    subplot(2,1,2),plot(sig.f,sig.sf)
    sig.LowPassFilter(5)
    subplot(2,1,1),plot(sig.t,sig.st)
    legend(["unfiltered","filtered"])
    subplot(2,1,2),plot(sig.f,sig.sf)
    """
    def __init__(self,t=None,f=None,st=None,sf=None):
	self.t,self.f,self.st,self.sf=None,None,None,None
	if t!=None: self.t=copy(t) #time values
	if f!=None: self.f=copy(f) #freq values
	if st!=None: self.st=copy(st) #time domain signal
	if sf!=None: self.sf=copy(sf) #freq domain signal
    #
    def CopyMe(self):
	mycopy=SignalData(t=copy(self.t),\
			st=copy(self.st),\
			f=copy(self.f),\
			sf=copy(self.sf))
	#
	if self.t ==None:mycopy.t =None
	if self.st==None:mycopy.st=None
	if self.f ==None:mycopy.f =None
	if self.sf==None:mycopy.sf=None
	return mycopy
    #
    def ForwardFourierTransform(self):
	if (self.t==None) & (self.st==None):
	    self.InverseFourierTransform()
	fmax= 1/(2* ( self.t[1]-self.t[0]) )
	fmin=-1/(2* ( self.t[1]-self.t[0]) )
	self.sf=fft(self.st)
	self.f=linspace(fmin,fmax,len(self.t))
	return self.f,self.sf
    #
    def InverseFourierTransform(self):
	if (self.f==None) & (self.sf==None):
	    self.ForwardFourierTransform()
	tstep=1./(2*self.f.max())
	Npts=len(self.f)
	self.st=ifft(self.sf)
	self.t=linspace(0,tstep*Npts,Npts)
	return self.t,self.st
    #
    def TimeDomainFilter(self, tt, impulse_response):
	if (self.t==None) & (self.st==None):
	    self.InverseFourierTransform()
	dt=self.t[1]
	dtt=tt[1]
	Nresample=int(round(len(tt)*dtt/dt))
	(resampled_impulse_response,resampled_tt)=resample(impulse_response,Nresample,t=tt,window="hamming")
	normalised_res_imp_res=resampled_impulse_response/sum(resampled_impulse_response)
	st_filtered=convolve(self.st,normalised_res_imp_res,mode="same")
	self.st=st_filtered #Replaces original signal!
	self.ForwardFourierTransform() #Replaces original signal!
	return t,st_filtered
    #
    def FrequencyDomainFilter(self, ff, freq_response):
	if (self.t==None) & (self.st==None):
	    self.ForwardFourierTransform()
	#
	if abs(ff.max()+ff.min())>(ff.max()-ff.min())/1e8:
	    print "Frequency domain must be symmetric about zero"
	    sf_filtered=None
	#
	elif abs(ff.max()-self.f.max())<(ff.max()+self.f.max())/1e8:
	    #Equal frequency ranges
	    sf_filtered=self.sf * freq_response
	elif ff.max()>self.f.max():
	    #filter covers larger freq span: interpolate filter, cutoff to signal freqs
	    print "Frequency is wider than the signal frequencies: please re-define the filter"
	    sf_filtered=None
	elif ff.max()<self.f.max():
	    #filter doesn't cover signal freq span: cutoff to filter freqs
	    print "Frequency is narrower than the signal frequencies: please re-define the filter"
	    sf_filtered=None
	#
	if sf_filtered!=None:
	    self.sf=sf_filtered #Replaces original signal!
	    self.InverseFourierTransform()
	return self.f,sf_filtered
    #
    def LowPassFilter(self,cutoff):
	if self.f==None:
	    self.ForwardFourierTransform()
	freq_response = fftshift(exp(-(self.f)**2 / (2*(cutoff**2)) )) #freq domain filter impulse response
	self.FrequencyDomainFilter(self.f,freq_response)
    #
    def HighPassFilter(self,cutoff):
	if self.f==None:
	    self.ForwardFourierTransform()
	freq_response = 1 - fftshift(exp(-(self.f)**2 / (2*(cutoff**2)) )) #freq domain filter impulse response
	self.FrequencyDomainFilter(self.f,freq_response)
    #
    def DownSample(self,resample_time):
	if self.t==None:
	    self.InverseFourierTransform()
	if resample_time<self.t[1]:
	    print "DownSample error: new sample rate higher than original sample rate"
	    short_sig,short_t =self.st,self.t
	elif resample_time==self.t[1]:
	    print "DownSample warning: nothing to do, sample rate unchanged"
	    short_sig,short_t = self.st,self.t
	else:
	    tmax=self.t[-1]
	    short_sig, short_t = resample(self.st,round(tmax/resample_time),t=self.t)
	#
	self.t=copy(short_t)
	self.st=copy(short_sig)
	self.ForwardFourierTransform()
	#return self.t,self.st
    #
    def CropTime(self,t1=0,t2=1):
	#t1=self.t.min(),
	#t2 = self.t.max()
	keep_flag = [(tt>t1)&(tt<t2) for tt in self.t]
	t_crop = self.t[find(keep_flag)]
	st_crop = self.st[find(keep_flag)]
	self.t = t_crop.copy()
	self.st = st_crop.copy()
    def CopyAndCropTime(self,t1=0,t2=1):
	#Note: does not copy Fourier Transform
	if self.t ==None:
	    new_t =None
	    new_st=None
	else:
		#keep_flag = (self.t>t1) & (self.t<t2)
		#new_t = self.t[keep_flag]
		#new_st = self.st[keep_flag]
		dt = self.t[4]-self.t[3] # first data points often corrupted. Why?
		ind1 = floor((t1 - self.t[0])/dt)
		ind2 = floor((t2 - self.t[0])/dt)
		new_t  = self.t[ind1:ind2]
		new_st = self.st[ind1:ind2]
	#
	mycopy=SignalData(t=copy(new_t),st=copy(new_st))
	return mycopy
    def PlotMe(self,fignum=359):
	figure(fignum)
	if (self.t==None) & (self.st==None):
	    self.InverseFourierTransform()
	if (self.f==None) & (self.sf==None):
	    self.ForwardFourierTransform()
	subplot(2,1,1), plot(self.t,self.st)
	xlabel("time"),ylabel("signal")
	subplot(2,1,2), plot(self.f,fftshift(self.sf))
	xlabel("frequency"),ylabel("signal")
	show()

#End of file
