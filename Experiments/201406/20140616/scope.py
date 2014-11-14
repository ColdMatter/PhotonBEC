#------------------
#execfile("scope.py")
from pbec_analysis import *
from pbec_data_format import DataFormat
import tektronix
tek = tektronix.tek
t_data,channel_data = tek.getData()

channel_to_plot=1
figure(1),clf()
plot(t_data,channel_data[channel_to_plot-1])
xlabel("time (s)")
ylabel("Channel "+str(channel_to_plot)+" signal (V)")
show()

ts = make_timestamp()
df = DataFormat(ts, t_data,{"Ch"+str(channel_to_plot):channel_data[channel_to_plot-1]},comments = "testing")
df.parameters={"z":22.5}
df.saveData()

#EoF
