from picosdk import ps6000
import time
import ctypes

#--------------------------
#UTILITIES
#--------------------------
def print_status(status,prefix=""):
	try:
		print prefix+ ps.m.pico_tag(status)
	except:
		print prefix+"print_status: Something went wrong calling ps.m.picotag()"

def is_open(ps):
	return ps._handle != 0

def time_per_sample(timebase):
	'''
	Go look in the programmer's manual, p17 for the explanation
	REMAINING ISSUE: timebase<2 gives PICO_INVALID_TIMEBASE error
	That means the minimum sample interval is 800 ps NOT the 350 ps we were expecting.
	'''
	if 0 <= timebase <= 4:
		sample_interval = 2**timebase / 5.0e9
	elif 5 <= timebase < 2**32:
		#INCONSISTENT DOCUMENTATION: maybe they mean 2**30 NOT 2**32 for the limit
		sample_interval = (timebase-4.0) / 156250000
	else:
		sample_interval = nan
	return sample_interval

#--------------------------
#NOW RUN THE THING
#--------------------------
#OPEN THE DEVICE
try:
	ps
except:
	ps = ps6000.Device() #optionally, we could specify the device serial number, if there are many devices
	print "Setting up the device..."# (wait 6 seconds)...",
	
if not(is_open(ps)):
	status = ps.open_unit()
	#time.sleep(0.06)#no need to be patient
	print "... done"
else:
	print "Device already set up"
 
#SET THE CHANNEL(S)
channel_1 = ps.m.Channels.A
stateA = ps.m.ChannelState()
stateA.enabled=True
stateA.coupling = ps.m.Couplings.dc50 #AC or plain DC seem wrong
stateA.range = ps.m.Ranges.r100mv
status = ps.set_channel(channel_1, stateA) 
print_status(status,"set channel_1:\t")

#Now set a second channel
channel_2 = ps.m.Channels.B
stateB = ps.m.ChannelState()
stateB.enabled=True
stateB.coupling = ps.m.Couplings.dc50 #AC or plain DC seem wrong
stateB.range = ps.m.Ranges.r100mv
status = ps.set_channel(channel_2, stateB) 
print_status(status,"set channel_2:\t")

#SET THE BUFFER
segments = 1 #between 1 and 1 million. Right now, we need one per channel, I think
samples = int(1e5) #transfer gets slow when you reach 10 million samples or more. 
timebase=2 #at least "2" please. Must be integer.
#Also, in 32 bit python more than ~3e7 float samples breaks memory

segment = 0 #just choose the first
status, index_1 = ps.locate_buffer(channel_1,samples,segment,mode=ps.m.RatioModes.raw,downsample=0)
status, index_2 = ps.locate_buffer(channel_2,samples,segment,mode=ps.m.RatioModes.raw,downsample=0)

nchannels = len(ps._channel_set) #dodgy code!

#SET UP THE TRIGGER: OPTIONAL, from channel_1
enabled, source, threshold, direction = True, channel_1, +0.0, 0 #threshold is as fraction of signal range
status = ps.set_simple_trigger(enabled,source,threshold,direction,delay=0,waitfor=0)
print_status(status,"set trigger:\t")


#----START LOOPING HERE IF YOU NEED TO-----
#USE BLOCK MODE WITH THE "collect_segment" METHOD
all_data_1 = []
for i in range(1): #don't loop for now
	interval = time_per_sample(timebase) * samples * 1e9  #in nanoseconds
	status = ps.collect_segment(segment, interval, timebase=timebase)
	print_status(status,"collect segment for channel 1:\t")

	#RETRIEVE DATA FROM BUFFER
	status, data_1 = ps.get_buffer_volts(index=index_1) #because the relevant buffer.data is None
	status, data_2 = ps.get_buffer_volts(index=index_2) #because the relevant buffer.data is None
	print_status(status,"retrieved data from buffer:\t")
	
	all_data_1.append(copy(data_1))
#----STOP LOOPING HERE IF YOU NEED TO-----

#STOP THE DEVICE
status = ps.stop()
print_status(status,"stopping:\t")

#You might also need to close it
#status = ps.close_unit()
#print_status(status)

#--------------------------
#DISPLAY AND POST-PROCESSING
#--------------------------
tmin = 0 #trigger offsets may need to be handled properly at some point
tmax = tmin + samples*time_per_sample(timebase)
time_axis = linspace(tmin,tmax,samples,dtype=float32)

figure(1),clf()
plot(1e9*time_axis,1e3*data_1,".--")
plot(1e9*time_axis,1e3*data_2,".--")
xlabel("time (ns)")
ylabel("signal (mV)")
xlim(0,500)
grid(1)
savefig("temp.png")

#EoF