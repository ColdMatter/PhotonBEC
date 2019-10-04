#ipython --pylab=qt
#execfile("picoscope.py")
from picosdk import ps6000
import time


'''
ps = ps6000.Device()
status = ps.open_unit() #This temporarily opens a little message box display
if status == ps.m.pico_num("PICO_OK"):
	s, state = ps.get_channel_state(channel=ps.m.Channels.A)
	state.enabled = True	#Fails, because "state" is "None"
	state.range = ps.m.Ranges.r5v
	status = ps.set_channel(channel=ps.m.Channels.A, state=state)
	if status == ps.m.pico_num("PICO_OK"):
		s, index = ps.locate_buffer(channel=ps.m.Channels.A,
									samples=1000,
									segment=0,
									mode=ps.m.RatioModes.raw,
									downsample=0)
		status = ps.collect_segment(segment=0, interval=1000)
		if status == ps.m.pico_num("PICO_OK"):
			status, data = ps.get_buffer_volts(index=index)
			print data
			exit(0)
print ps.m.pico_tag(status)
'''

def print_status(status):
	print ps.m.pico_tag(status)

#WE'RE MOST LIKELY TO WANT TO USE BLOCK MODE
#Here, we'll try something simple, but section 2.5.2.1 of the manual might be more appropriate
#0. Open the scope unit
#1. Set up the input channels with the required voltage ranges and coupling type.
#2. Set up triggering.
#3. Start capturing data. (See Sampling modes, where programming is discussed in more detail.)
#4. Wait until the scope unit is ready.
#5. Stop capturing data.
#6. Copy data to a buffer.
#7. Close the scope unit.

#0.
ps = ps6000.Device() #optionally, we could specify the device serial number, if there are many devices
status = ps.open_unit()

#Extra optional bit...
s, state = ps.get_channel_state(channel=ps.m.Channels.A)

#1. [SKIP THIS STEP]
#ps.set_channel(channel,state) 
#It turns out that our 6407 device only does a fixed voltage range, and AC coupled, I think

#2.
enabled,source,threshold,direction = True, 0, +0.5, 1
ps.set_simple_trigger(enabled,source,threshold,direction,delay=0,waitfor=0)

#3.
pretrig = 100 #number of pre-trigger samples
posttrig = 1000 #number of post-trigger samples
timebase = 20 #2**timebase * 200ps for time unit
oversample = 1 #1 means no oversampling. 256 is max.
ref_time = None #a null pointer would probably be best if we can manage it
segment = 0 #something to do with internal memory management
ref_cb = None #can be used for low-level callback functions
ref_cb_param = None #parameters for low-level callback functions?
ps._run_block(pretrig, posttrig, timebase, oversample, ref_time, segment, ref_cb, ref_cb_param)

#4. 
#later on we can wait the right amount of time by using a simple callback function. Probably
time.sleep(1) 

#5.
ps.stop()

#6.
#ps._get_values(start, ref_samples, ratio, mode, segment, ref_overflow)
#ps._get_values_bulk(ref_samples, start_segment, stop_segment, ratio, mode, ref_overflow)
dump = ps.get_buffer_volts(index=0) #no, I don't know what I'm doing
print dump

#7.
print_status(status)
status = ps.close_unit()

#execfile("picoscope.py")
#EoF