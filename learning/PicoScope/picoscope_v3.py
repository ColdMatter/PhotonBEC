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

def time_per_sample(timebase):
	'''
	Go look in the programmer's manual, p17 for the explanation
	'''
	if 0 <= timebase <= 4:
		sample_interval = 2**timebase / 5.0e9
	elif 5 <= timebase < 2**32:
		#INCONSISTENT DOCUMENTATION: maybe they mean 2**30 NOT 2**32
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
	print "Setting up the device... (wait 6 seconds)...",
	unit_is_open = False
	unit_was_open = False
	
status = ps.open_unit()
if status == ps.m.PICO_STATUS["PICO_OK"]:
	unit_is_open = True

if not(unit_was_open):
	time.sleep(6)#be patient
	unit_was_open=True
	print "... done"
else:
	print "Device already set up"

#SET THE CHANNEL(S)
channel = ps.m.Channels.A
stateA = ps.m.ChannelState()
stateA.enabled=True
stateA.coupling = ps.m.Couplings.dc50 #AC or plain DC seem wrong
stateA.range = ps.m.Ranges.r100mv
status = ps.set_channel(channel, stateA) 
print_status(status,"set channel:\t")

#SET THE BUFFER
segments = 1 #between 1 and 1 million
segment = 0
samples = int(1e5) #transfer gets slow when you reach 10 million samples or more. 
#Also, in 32 bit python more than ~3e7 float samples breaks memory
timebase=2 #at least "2" please. Must be integer
#Why are timebase=1 or 0 "INVALID?" Because less than 350 ps.
#ERROR: Therefore, we cannot access sample times less than 800 ps (at least 400 ps should be available)
status, index = ps.locate_buffer(channel,samples,segment,mode=ps.m.RatioModes.raw,downsample=0)
returned_index = index

#SET UP THE TRIGGER: OPTIONAL
enabled, source, threshold, direction = True, channel, +0.0, 0 #threshold is as fraction of signal range
tatus = ps.set_simple_trigger(enabled,source,threshold,direction,delay=0,waitfor=0)
print_status(status,"set trigger:\t")


#USE BLOCK MODE WITH THE "collect_segment" METHOD
interval = time_per_sample(timebase) * samples * 1e9 #in nanoseconds
status = ps.collect_segment(segment, interval, timebase=timebase)
print_status(status,"collect segment:\t")

#RETRIEVE DATA FROM BUFFER
status, data = ps.get_buffer_volts(index=index) #because the relevant buffer.data is None
print_status(status,"retrieving data from buffer:\t")
#How do I get the time axis?

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
time_axis = linspace(tmin,tmax,samples)

figure(1),clf()
plot(1e9*time_axis,1e3*data,".--")
xlabel("time (ns)")
ylabel("signal (mV)")
xlim(0,500)
grid(1)
savefig("temp.png")

#EoF