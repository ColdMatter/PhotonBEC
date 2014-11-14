#--------------------
#execfile("ringdown_measurement.py")
from __future__ import division
import sys
import time

from pbec_data_format import *
sys.path.append("D:\Control\PythonPackages")
#Import locally-written packages
from tektronix import *
from pbec_analysis import *
from LaserQuantum import *
from SingleChannelAO import *

lq = LaserQuantum()

#EXPERIMENTAL CONTROL PARAMETERS
Navg = 128
AOM_on_volts,AOM_off_volts = 0.9,0.0
scope_averaging_time = 6#6#in seconds...estimated to be 6 seconds

#DISPLAY PARAMETERS
font_size = 10
ch2_prefac=2e-3 #for display only

#----------------------------
#SET UP EXPERIMENT
#----------------------------
title_comment = "Ringdown. Laser power "+str(laser_power)+" mW; ND filter factor " + str(nd_filter)

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
print "Acquiring from 'scope..."
tek.stopAcquisition()
tek.startAcquisition(run_once=1)
t_data,(ch1_data,ch2_data)=tek.getData()

#Measure background with lights off
SingleChannelAO(AOM_off_volts)
tek.startAcquisition(run_once=1)
t_data,(bkg_ch1_data,bkg_ch2_data)=tek.getData()
SingleChannelAO(AOM_on_volts)

first_ts = TimeStamp()
print "... "+first_ts
ch1_data_mean=ch1_data
ch1_data_tot=ch1_data
ch2_data_mean=ch2_data
ch2_data_tot=ch2_data
bkg_ch1_data_mean=bkg_ch1_data
bkg_ch1_data_tot=bkg_ch1_data
bkg_ch2_data_mean=bkg_ch2_data
bkg_ch2_data_tot=bkg_ch2_data

for i in range(Nruns-1):
	count=i+1
	if count in [1,2]: print str(count+1)+" runs"
	if not((count+1)%5): print str(count+1)+" runs"
	tek.startAcquisition(run_once=1)
	t_data,(ch1_data,ch2_data)=tek.getData()
	SingleChannelAO(AOM_off_volts)
	tek.startAcquisition(run_once=1)
	t_data,(bkg_ch1_data,bkg_ch2_data)=tek.getData()
	SingleChannelAO(AOM_on_volts)
	ch1_data_tot +=ch1_data
	ch1_data_mean = ch1_data_tot / (count+1.0)
	ch2_data_tot +=ch2_data
	ch2_data_mean = ch2_data_tot / (count+1.0)
	bkg_ch1_data_tot +=bkg_ch1_data
	bkg_ch1_data_mean = bkg_ch1_data_tot / (count+1.0)
	bkg_ch2_data_tot +=bkg_ch2_data
	bkg_ch2_data_mean = bkg_ch2_data_tot / (count+1.0)
	latest_ts = TimeStamp()
	#
	#SAVE DATA
	parameters = {"laser power":laser_power,\
		"Navg scope":Navg,"Nruns":count+1,\
		"ND filter":nd_filter}
	parameters.update(parameter_extra) #from calling file
	comments ="First and last timestamps: "+first_ts+", "+latest_ts
	comments+= "; "+comment_extra #From calling program
	data_dict = {"Trigger":ch2_data_mean,"PDdata":ch1_data_mean,\
					"Trigger_bkg":bkg_ch2_data_mean, "PDdata_bkg":bkg_ch1_data_mean}
	df = DataFormat(first_ts, indep_variable = t_data,\
		dep_variables=data_dict,\
		comments = comments,\
		parameters = parameters,\
		links={"preview png":pbec_prefix+"_"+first_ts+".png"})
	if saving: df.saveData()
	#
	#PLOT AS YOU GO
	#
	figure(1),clf()
	plot(1e6*t_data,ch2_prefac*1e3*    ch2_data_mean,label=str(ch2_prefac)+" *CH2")
	plot(1e6*t_data,           1e3*    ch1_data_mean,label="CH1")
	plot(1e6*t_data,ch2_prefac*1e3*bkg_ch2_data_mean,label=str(ch2_prefac)+" *CH2_bkg")
	plot(1e6*t_data,           1e3*bkg_ch1_data_mean,label="CH1_bkg")
	title_string = first_ts+" to "+latest_ts+"; Navg (on scope) "+str(Navg)+" ; Nruns (software) "+ str(count+1)
	#title_string+="\n CH2: amplifier input; CH1: output"
	title_string+="\n CH2: trigger; CH1: APD output"
	title_string+="\n"+title_comment
	#
	legend()
	xlabel("t / $\mu$s")
	ylabel("Signal / mV")
	grid(1)
	subplots_adjust(top=0.87)
	title(title_string, fontsize= font_size)
	#Save a preview figure. TODO: the DataFormat class should probably handle this.
	savefig("dump"+".png")
	if saving: savefig(TimeStampToFileName(first_ts,file_end=".png"))

SingleChannelAO(AOM_on_volts)
tek.startAcquisition()
#
#EOF
