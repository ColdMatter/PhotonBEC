

#set laser power
#take pd reading
#repeat, end up with function mapping laser power to pd reading

#set laser power to max
#set AOM amplitude
#take PD reading
#repeat, end up with function mapping aom amplitude to pd reading

#combine functions, get function mapping aom amplitude to laser power

import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import SingleChannelAI
import SingleChannelAO
import pbec_ipc
import numpy as np
import time, json

from scipy.optimize import leastsq
from scipy.optimize import brentq
from scipy.interpolate import interp1d

import pbec_analysis as pbeca

laser_power_range = range(1, 13, 1) #see lab book 20/7/15
amplitude_range = linspace(0, 1.5, 101) #taken from original calibrate_AOM_amplitude.py

def set_AOM_amplitude(a):
	'''function for easier naming / thinking'''
	print 'setting aom amplitude to ' + str(a)
	SingleChannelAO.SetAO0(a)

def set_laser_power(power_mW):
	sys.stdout.write('setting laser power to ' + str(power_mW) + '.. ')
	pbec_ipc.ipc_eval('guiSetPowerAndWait(' + str(int(power_mW)) + ')', 'laser_controller')
	print 'done'
	
def read_pd_voltage(sleep_time):
	time.sleep(sleep_time)
	v = np.mean(SingleChannelAI.SingleChannelAI(Npts=2,rate=1.0e4,device="Dev1",channel="ai0",minval=0,maxval=1.0))
	return v
	
def read_pd_voltage_average(N = 3, sleep_time = 0.3):
	v = np.mean([read_pd_voltage(sleep_time) for i in range(N)])
	print 'read ' + str(v) + ' V from photodiode'
	return v
	
'''
print 'make sure you\'ve run on_startup.bat to set the AOM amplitude correctly'
print 'calibrating laser power vs PD reading'
Ll = []
Lv = []
for lp in laser_power_range:
	set_laser_power(lp)
	v = read_pd_voltage_average()
	Ll.append(lp)
	Lv.append(v)
	
#plot(Ll, Lv, '-x')
'''
#TODO fit to a straight line, that is your function'''
print 'calibrating AOM amplitude vs PD reading'
set_laser_power(laser_power_range[-1])
Aa = []
Av = []
for a in amplitude_range:
	set_AOM_amplitude(a)
	v = read_pd_voltage_average(N = 1, sleep_time = 1)
	Aa.append(a)
	Av.append(v)
	
#plot(Aa, Av, '-x')

#convert AOM function to a transmission, which can then be multiplied by duty cycle

data = {}
#data['Ll'] = Ll
#data['Lv'] = Lv
data['Aa'] = Aa
data['Av'] = Av
fd = open('data.json', 'w')
fd.write(json.dumps(data))
fd.close()

#sys.exit(0)

fd = open('data.json')
data = json.loads(fd.read())
fd.close()

'''
def line(x, m, c):
	return m*x + c
def line_residuals(pars, xdata, ydata):
	return ( line(xdata, *pars) - ydata )**2
	
Ll = array(data['Ll'])
Lv = array(data['Lv'])
guess = (1, 0)
((Lm, Lc), dump) = leastsq(line_residuals, guess, (Ll, data['Lv']))
print Lm, Lc

clf()
plot(data['Ll'], data['Lv'], 'x-')
fakex = linspace(data['Ll'][0], data['Ll'][-1], 100)
plot(fakex, line(fakex, Lm, Lc), '-')
'''

Aa = array(data['Aa'])
Av = array(data['Av'])
At = Av / max(Av) #becomes a transmission, also we're assuming no offset


if 1:
	figure('AOM'), clf()
	plot(Aa, At, '-x')
	Ax = linspace(Aa[0], Aa[-1], 100)
	#plot(Ax, interp1d(Aa, At)(Ax), '-')
	plot(Ax, interp1d(Aa, At, kind='cubic')(Ax), '--')
	xlim(0, 1.5)
	ylim(0, 1.5)

aom_func = interp1d(Aa, At, kind='cubic')

def aom_func_v(x, t):
	return aom_func(x) - t

def A_n1_brentq(t):
	'''
	inverse of A(a) = t
	give it t it will return a
	'''
	print Aa[0], Aa[-1], t
	ai = brentq(aom_func_v, Aa[0], Aa[-1], args=(t, ))
	return ai
	
def A_T(t):
	upindex = ravel(argwhere(At >= t))[0]
	print 'at[up]=' + str(At[upindex]) + ' t=' + str(t) + ' up-1=' + str(At[upindex-1])
	assert At[upindex] >= t and At[upindex-1] < t
	ai = brentq(aom_func_v, Aa[upindex], Aa[upindex-1], args=(t, ))
	return ai
	
A_n1 = A_T

AAt = linspace(0.01, 0.99, 100)
AAa = array([A_n1(t) for t in AAt])
#figure('inverse'), clf()
plot(AAt, AAa, '-')
plot(linspace(0, 1.5, 10), linspace(0, 1.5, 10), '--')

print 'checking the inverse function is good'
for ai, tt in zip(AAa, AAt):
	treal = aom_func(ai)
	if abs(1.0 - tt/treal) > 0.01:
		print 'uh oh, tt/treal = ' + str(tt/treal)
