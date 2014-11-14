#--------------------
#execfile("photodetector_characterisation.py")
from __future__ import division
import sys
import time

from pbec_data_format import *
sys.path.append("D:\Control\PythonPackages")
#Import locally-written packages
from tektronix import *
from pbec_analysis import *
from LaserQuantum import *

#EXPERIMENTAL CONTROL PARAMETERS
PDgain_dB=10 #Changed in hardware
#####laser_power = 10 #in mW #TO BE SET BY CALLING PROGRAM
Nruns = 128
Navg = 128
timebase=500e-9

#DISPLAY PARAMETERS
font_size = 10
ch2_prefac=1e-3 #for display only
title_comment = "Nominal power "+str(laser_power)+" mW; photodiode gain setting "+str(PDgain_dB)+"dB"

#----------------------------
#SET UP EXPERIMENT
#Instantiate laser controller
lq = LaserQuantum() #Note: methods fail hard if another process is accessing the laser controller

lq.setPower(laser_power)
current_power = lq.getPower()
power_tolerance=0.02
while abs(current_power-laser_power) > laser_power*power_tolerance:
	#FIXME: can be fooled by correct but unstable laser power 
	print "Waiting for laser power to settle. Set "+str(laser_power)+" mW; current "+str(current_power) +" mW"
	time.sleep(2)
	current_power = lq.getPower()

tek.setAverages(Navg)
tek.setTimeBase(timebase)
tek.setActiveChannels([1,2])

#-----START COLLECTING DATA-------
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
	#SAVE DATA
	parameters = {"laser power":laser_power,"Navg scope":Navg,"Nruns":count,"PDgain_dB":PDgain_dB}#Include laser power, PD gain, etc, here
	comments ="First and last timestamps: "+first_ts+", "+latest_ts
	comments+= "; "+comment_extra #From calling program
	df = DataFormat(first_ts, indep_variable = t_data,\
		dep_variables={"Trigger":ch2_data_mean,"PDdata":ch1_data_mean},\
		comments = comments,\
		parameters = parameters,\
		links={"preview png":pbec_prefix+"_"+first_ts+".png"})
	df.saveData()
	#
	#PLOT AS YOU GO
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
	#Save a preview figure. TODO: the DataFormat class should probably handle this.
	savefig(TimeStampToFileName(first_ts,file_end=".png"))

#
#EOF
