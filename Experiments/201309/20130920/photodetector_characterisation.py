#--------------------
#execfile("test.py")
from __future__ import division
import sys
sys.path.append("D:\Control\PythonPackages")
#Import locally-written packages
from tektronix import *
from pbec_analysis import *
from LaserQuantum import *

#Instantiate laser controller
lq = LaserQuantum() #Note: methods fail hard if another process is accessing the laser controller

font_size = 10

title_comment = "Nominal power 1 mW; photodiode gain setting 10dB"
Nruns = 128
Navg = 128
ch2_prefac=1e-3 #-1000
#tek.setTimeBase(0.5e-6)
#tek.setActiveChannels(1)
tek.setAverages(Navg)
tek.setTimeBase(500e-9)
tek.setActiveChannels([1,2])

first_ts = TimeStamp()
t_data,(ch1_data,ch2_data)=tek.getData()
ch1_data_mean=ch1_data
ch1_data_tot=ch1_data
ch2_data_mean=ch2_data
ch2_data_tot=ch2_data

for i in range(Nruns-1):
	count=i+1
	if count in [1,2]: print count
	if not(count%5): print count
	t_data,(ch1_data,ch2_data)=tek.getData()
	ch1_data_tot +=ch1_data
	ch1_data_mean = ch1_data_tot / (count+1.0)
	ch2_data_tot +=ch2_data
	ch2_data_mean = ch2_data_tot / (count+1.0)
	latest_ts = TimeStamp()
	#
	figure(1),clf()
	plot(1e6*t_data,ch2_prefac*1e3*ch2_data_mean,label=str(ch2_prefac)+" *CH2")
	plot(1e6*t_data,1e3*ch1_data_mean,label="CH1")
	title_string = first_ts+" to "+latest_ts+"; Navg (on scope) "+str(Navg)+" ; Nruns (software) "+ str(count)
	#title_string+="\n CH2: amplifier input; CH1: output"
	title_string+="\n CH2: trigger; CH1: output"
	title_string+="\n"+title_comment
	#
	legend()
	xlabel("t / $\mu$s")
	ylabel("Signal / mV")
	grid(1)
	subplots_adjust(top=0.87)
	title(title_string, fontsize= font_size)
	savefig("temp.png")

#
#EOF
