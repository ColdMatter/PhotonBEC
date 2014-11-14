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
Nruns = 32
Navg = 128
timebase=500e-9

#DISPLAY PARAMETERS
font_size = 10
ch2_prefac=-1e3 #for display only

#----------------------------
#SET UP EXPERIMENT
#ASK FOR HUMAN INPUT
input_amplitude=float(raw_input("Please type the input amplitude in mV...\n")) #Waits for human to type a number
title_comment = "Amplifier: Input amplitude "+str(input_amplitude)+" mV"
#----------

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
	parameters = {"input amplitude":input_amplitude,"Navg scope":Navg,"Nruns":count}
	comments ="First and last timestamps: "+first_ts+", "+latest_ts
	comments+= "; "+comment_extra #From calling program
	labels=["Output", "Input"]
	df = DataFormat(first_ts, indep_variable = t_data,\
		dep_variables={labels[0]:ch1_data_mean,labels[1]:ch2_data_mean},\
		comments = comments,\
		parameters = parameters,\
		links={"preview png":pbec_prefix+"_"+first_ts+".png"})
	df.saveData()
	#
	#PLOT AS YOU GO
	#
	figure(1),clf()
	plot(1e6*t_data,ch2_prefac*1e3*ch2_data_mean,label=str(ch2_prefac)+" *"+labels[1])
	plot(1e6*t_data,1e3*ch1_data_mean,label=labels[0])
	title_string = first_ts+" to "+latest_ts+"; Navg (on scope) "+str(Navg)+" ; Nruns (software) "+ str(count)
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
