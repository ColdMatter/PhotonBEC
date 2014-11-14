#--------------------
#execfile("apd_characterisation.py")
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
#####laser_power = 10 #in mW #TO BE SET BY CALLING PROGRAM
#####nd_filter = 1.0 #in mW #TO BE SET BY CALLING PROGRAM
Navg = 128

#DISPLAY PARAMETERS
font_size = 10
ch2_prefac=1e-2 #for display only

#----------------------------
#SET UP EXPERIMENT
#Instantiate laser controller
lq = LaserQuantum() #Note: methods fail hard if another process is accessing the laser controller

title_comment = "Laser power "+str(laser_power)+" mW; ND filter" + str(nd_filter)

tek.setAverages(Navg)
tek.setTimeBase(timebase)
tek.setActiveChannels([1,2])

#-----START COLLECTING DATA-------
print "Acquiring from 'scope..."
tek.stopAcquisition()
tek.startAcquisition(run_once = 1)
t_data,(ch1_data,ch2_data)=tek.getData()
first_ts = TimeStamp()
print "... "+first_ts
ch1_data_mean=ch1_data
ch1_data_tot=ch1_data
ch2_data_mean=ch2_data
ch2_data_tot=ch2_data

for i in range(Nruns-1):
	count=i+1
	if (count+1) in [1,2]: print count+1
	if not((count+1)%5): print count+1
	tek.startAcquisition(run_once = 1)
	t_data,(ch1_data,ch2_data)=tek.getData()
	ch1_data_tot +=ch1_data
	ch1_data_mean = ch1_data_tot / (count+1.0)
	ch2_data_tot +=ch2_data
	ch2_data_mean = ch2_data_tot / (count+1.0)
	latest_ts = TimeStamp()
	#
	#SAVE DATA
	parameters = {"laser power":laser_power,\
		"Navg scope":Navg,"Nruns":(count+1),\
		"ND filter":nd_filter}#Include laser power, PD gain, etc, here
	parameters.update(parameters_extra)
	comments ="First and last timestamps: "+first_ts+", "+latest_ts
	comments+= "; "+comment_extra #From calling program
	df = DataFormat(first_ts, indep_variable = t_data,\
		dep_variables={"Trigger":ch2_data_mean,"PDdata":ch1_data_mean},\
		comments = comments,\
		parameters = parameters,\
		links={"preview png":pbec_prefix+"_"+first_ts+".png"})
	if saving: df.saveData()
	#
	#PLOT AS YOU GO
	#
	figure(1),clf()
	plot(1e6*t_data,ch2_prefac*1e3*ch2_data_mean,label=str(ch2_prefac)+" *CH2")
	plot(1e6*t_data,1e3*ch1_data_mean,label="CH1")
	title_string = first_ts+" to "+latest_ts+"; Navg (on scope) "+str(Navg)+" ; Nruns (software) "+ str((count+1))
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
	savefig("dump"+".png")
	if saving: 
		savefig(TimeStampToFileName(first_ts,file_end=".png"))

tek.startAcquisition()
#
#EOF
