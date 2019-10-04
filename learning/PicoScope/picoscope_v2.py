from picosdk import ps6000
import time
import ctypes

def print_status(status,prefix=""):
	try:
		print prefix+ ps.m.pico_tag(status)
	except:
		print prefix+"print_status: Something went wrong calling ps.m.picotag()"

#WE'RE MOST LIKELY TO WANT TO USE BLOCK MODE
#Section 2.5.2.1 of the manual might be most appropriate
#1. Open the oscilloscope using ps6000OpenUnit.
#2. Select channel ranges and AC/DC coupling using ps6000SetChannel.
#3. Set the number of memory segments equal to or greater than the number of captures required using ps6000MemorySegments. Use ps6000SetNoOfCaptures before each run to specify the number of waveforms to capture.
#4. Using ps6000GetTimebase, select timebases until the required nanoseconds per sample is located.
#5. Use the trigger setup functions ps6000SetTriggerChannelConditions, ps6000SetTriggerChannelDirections and ps6000SetTriggerChannelProperties to set up the trigger if required.
#6. Start the oscilloscope running using ps6000RunBlock.
#7. Wait until the oscilloscope is ready using the ps6000BlockReady callback.
#8. Use ps6000SetDataBufferBulk to tell the driver where your memory buffers are. Call the function once for each channel/segment combination for which you require data. For greater efficiency with multiple captures, you could do this outside the loop after step 5.
#9. Transfer the blocks of data from the oscilloscope using ps6000GetValuesBulk.
#10. Retrieve the time offset for each data segment using ps6000GetValuesTriggerTimeOffsetBulk64.
#11. Display the data.
#12. Repeat steps 6 to 11 if necessary.
#13. Stop the oscilloscope using ps6000Stop.
#14. Close the device using ps6000CloseUnit.

#1.
try:
	ps
except:
	ps = ps6000.Device() #optionally, we could specify the device serial number, if there are many devices

status = ps.open_unit()

#2.
channel = ps.m.Channels.A
stateA = ps.m.ChannelState()
stateA.enabled=True
stateA.coupling = ps.m.Couplings.dc50 #AC or plain DC seem wrong
stateA.range = ps.m.Ranges.r100mv
stateA.offset = 0
stateA.overvoltaged = False
status = ps.set_channel(channel, stateA) 
print_status(status,"set channel:\t")

#3.
segments = 1 #between 1 and 1 million
status, samples_per_segment = ps.set_memory_segments(segments) #what does mem_value do?
print_status(status,"set memory segments:\t")

#4. 
time_unit = 200e-12 #I think the unit is 200ps
timebase=2**10 #because why not
status,interval_value = ps.get_basic_interval(timebase) #what are timebase and interval_value?
print_status(status,"get interval:\t")

#5.
enabled, source, threshold, direction = True, channel, 0.5, 0
status = ps.set_simple_trigger(enabled,source,threshold,direction,delay=0,waitfor=0)
print_status(status,"set trigger:\t")

#6. I DON'T THINK THIS IS HOW THE PROGRAM WAS SUPPOSED TO BE USED, WITH SEMI-PRIVATE METHODS
pretrig = 100 #number of pre-trigger samples
posttrig = 1000 #number of post-trigger samples
timebase = timebase#20 #2**timebase * 200ps for time unit
oversample = 1 #1 means no oversampling. 256 is max.
ref_time = ctypes.c_int16(1000)#time in ms 'scope spends acquiring data
segment = 0 #something to do with internal memory management
ref_cb = None #can be used for low-level callback functions
ref_cb_param = None #parameters for low-level callback functions
status = ps._run_block(pretrig, posttrig, timebase, oversample, ctypes.byref(ref_time), segment, None, None)

print_status(status,"run_block:\t")

#7. 
time.sleep(1.5) #Can be fixed by using a callback function to block until the oscilloscope has finished acquiring

#8.  HELP! I DON'T REALLY KNOW HOW TO SET UP THE BUFFER
mode = ps.m.RatioModes.raw
segment = segment #see above
num_samples=1100
status, index = ps.locate_buffer(channel=channel, samples=num_samples, segment=segment, mode=mode, downsample=1)
print_status(status,"locate buffer:\t")

line=ps._buffers[index].channel
my_buffer_array = empty(num_samples, dtype = ctypes.c_int16)
my_buffer_ctype = (ctypes.c_int16 * len(my_buffer_array))(*my_buffer_array)
buffer_min = None
bufflen =  len(my_buffer_array)
argument_ignored="this argument is ignored, and I don't care why"
status = ps._set_data_buffers(line, ctypes.byref(my_buffer_ctype), buffer_min, bufflen, argument_ignored, mode)
print_status(status,"setting data buffers:\t")

#9. TRANSFER THE DATA [HELP!]
start = 100
samples_array = empty(num_samples-start,dtype=ctypes.c_int) #probably smaller than the number available
samples_ctype = (ctypes.c_int * len(samples_array))(*samples_array)
ratio = 1 #don't downsample
mode = mode
segment = segment
overflow = 0
overflow_ctype = ctypes.c_int16(overflow)
status = ps._get_values(start, ctypes.byref(samples_ctype), ratio, mode, segment, ctypes.byref(overflow_ctype))
print_status(status,"getting values:\t")

#10. RETRIEVE DATA FROM BUFFER [HELP!]
#status, data = ps.get_buffer_volts(index=index) #because the relevant buffer.data is None
status, data = ps.get_buffer_data(index=index) #because the relevant buffer.data is None
print_status(status,"retrieving data from buffer:\t")

#11. Display data: that's the easy bit
figure(1),clf()
plot(my_buffer_array)
show()

#12.
#NOT NECESSARY TO REPEAT FOR NOW

#13.
status = ps.stop()
print_status(status,"stopping:\t")

#14.
#status = ps.close_unit()
#print_status(status)
