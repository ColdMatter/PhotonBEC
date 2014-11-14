#ipython --pylab
#execfile("main.py")
from pylab import *
sys.path.append("D:\Control\PythonPackages")
from SingleChannelAO import *
from pbec_analysis import *
from pbec_data_format import *
from tektronix import *

laser_power= 70
nd_filter = 1
timebase=5e-6
micrometer_posn_mm = 3.0
parameter_extra = {"micrometer_posn_mm":micrometer_posn_mm}

Navg=1
parameters = {"laser power":laser_power,\
	"Navg scope":Navg,\
	"ND filter":nd_filter}
parameters.update(parameter_extra)

		
tek.setAverages(Navg)
tek.setTimeBase(timebase)
tek.setActiveChannels([1,2])
tek.stopAcquisition()
tek.startAcquisition(run_once=1)
t_data,(ch1_data,ch2_data)=tek.getData()

comments="Ringdown measurement, example signal, single run, no averaging"
ts = TimeStamp()
df = DataFormat(ts, indep_variable = t_data,\
	dep_variables={"APD output":ch1_data,"Scmitt trigger":ch2_data},\
	comments = comments,\
	parameters = parameters,\
	links={})


figure(1),clf()
plot(1e6*t_data,0.2*1e3*ch2_data,label="0.2 *Trigger")
plot(1e6*t_data,    1e3*ch1_data,label="APD output")
legend()
xlabel("t / $\mu$s")
ylabel("Signal / mV")
grid(1)
subplots_adjust(top=0.87)
font_size=9
title(comments+"; "+df.timestamp, fontsize= font_size)

savefig("dump"+".png")
savefig(TimeStampToFileName(ts,file_end=".png"))
df.saveData()

#EOF
