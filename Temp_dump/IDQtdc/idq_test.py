from IDQCorrelator import *
sys.path.append("D:/Control/PythonPackages/")
import pbec_analysis

#Parameters
expo_time = 0.5
channel_mask = 1+2+8 #7
buffer_size = 2e5

##auto_col_channel=1
elec_trig_ch=0
optical_trig_ch=1
signal_ch=3

#Setup the correlator device: seems to be needed each time we retrieve the timestamps
correlator = CorrelatorControl()
correlator.setExposureTime(expo_time) #1 second exposure
correlator.enableChannels(channel_mask) #channels 1,2, and 3
correlator.setTimestampBufferSize(int(buffer_size))
timebase=correlator._getTimebase_()

#Acquire the data
timestamps, channels = correlator.getLastTimeStamps(expo_time/1.3) #there's something dodgy here...
correlator.close()


pbec_ts = pbec_analysis.make_timestamp()
ts_ch = zip(timestamps,channels)
#Put the data into a Data object
corr_data = CorrelatorData(pbec_ts)
corr_data.setData((timestamps, channels))

#For checking the optical trigger
tmin, tmax=1945.5e-9, 1947e-9
corr_data.plotHistogram(1*timebase,tmin,tmax,elec_trig_ch,optical_trig_ch,fignum=432)

#Checking signal channel
#tmin, tmax=1945e-9, 1948e-9
corr_data.plotHistogram(1*timebase,tmin,tmax,elec_trig_ch,signal_ch,fignum=433)

#corr_data.plotAutoCorrelation(10*timebase,tmin,tmax,auto_col_channel)
#corr_data.plotCoincidences()

#This will fail massively
#####corr_data.saveData()

'''
ex = pbec_analysis.ExperimentalDataSet(pbec_ts)
ex.dataset = {"correlation_data":corr_data}
ex.meta.comments="Still testing"
ex.meta.parameters={"expo_time":expo_time, "channel_mask":channel_mask, "buffer_size":buffer_size,"timebase":timebase, "Output Amplitude":output_amplitude, "Amplifier Control Value":amplifier_control_value, "Output Repetition Rate":output_repetition_rate}
ex.saveAllData()
'''