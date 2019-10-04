import sys
sys.path.append("Y:\\Control\\PythonPackages\\")
sys.path.append("D:\\Control\\PythonPackages\\")
import SignalDataModule
#from interferometer_utils import *

test_with_gaussian = False
if test_with_gaussian:
	t = linspace(-1000, 1000, 100000)
	params = (2.3, 0, 1.5, 0) #amp, mu, sigma, off
	gau = gaussian(t, *params)
	sigdat = SignalDataModule.SignalData(t=t, st=gau)
	sigdat.ForwardFourierTransform()

	figure('real space'), clf()
	plot(t, gau, '-', label='graph')
	guess = (1, 0, 0.3, 0) #amp, mu, sigma, off
	((amp, mu, sigma, off),dump) = leastsq(gaussian_residuals, guess, (t, gau))
	plot(t, gaussian(t, amp, mu, sigma, off), '-', label='$\\tau$='
		+ str(round(sigma,9)) + 'units', linewidth=2)
	xlim(-7, 7)
	xlabel('time')
	legend(loc='upper left')

	figure('f space'), clf()
	ft = abs(fftshift(sigdat.sf))
	f = sigdat.f*2*pi
	plot(f, ft, '-', label='graph')
	guess = (400, 0, 0.1, 0) #amp, mu, sigma, off
	((amp, mu, sigma, off),dump) = leastsq(gaussian_residuals, guess, (f, ft))
	plot(f, gaussian(f, amp, mu, sigma, off), '-', label='$\\tau$='
		+ str(round(sigma,9)) + 'units^-1', linewidth=2)
	xlim(-3, 3)
	xlabel('freq')
	legend(loc='upper left')

test_with_sine_wave = False
if test_with_sine_wave:
	t = linspace(-0.1, 0.1, 100001) #in seconds
	freq = 50 #hz
	A = 1
	sinewave = A*sin(2*pi*freq*t)

	figure('sinewave'), clf()
	subplot(2, 1, 1)
	plot(t, sinewave, '-', label='graph')
	xlim(t[0], t[-1])
	xlabel('time')
	ylim(-A*5, A*5)
	grid(1)
	
	sigdat = SignalDataModule.SignalData(t=t, st=sinewave)
	sigdat.ForwardFourierTransform()

	subplot(2, 1, 2)
	ft = fftshift(sigdat.sf)
	f = sigdat.f
	plot(f, ft, '-x', label='graph')
	xlim(-2*freq, 2*freq)
	xlabel('freq')
	#ylim(-2, max(sigdat.sf)*2)
	
test_with_beats = True
if test_with_beats:
	t = linspace(-0.3, 0.3, 100001) #in seconds
	freq1 = 50 #hz
	freq2 = 60
	A = 1
	beats = A*sin(2*pi*freq1*t) + A*sin(2*pi*freq2*t)
	
	figure('beats'), clf()
	subplot(2, 1, 1)
	plot(t, beats, '-', label='graph')
	xlim(t[0], t[-1])
	xlabel('time')
	ylim(-A*5, A*5)
	grid(1)
	
	sigdat = SignalDataModule.SignalData(t=t, st=beats)
	sigdat.ForwardFourierTransform()

	subplot(2, 1, 2)
	ft = fftshift(sigdat.sf)
	f = sigdat.f
	plot(f, ft, '-x', label='graph')
	xlim(-2*freq2, 2*freq2)
	xlabel('freq')
	#ylim(-2, max(sigdat.sf)*2)