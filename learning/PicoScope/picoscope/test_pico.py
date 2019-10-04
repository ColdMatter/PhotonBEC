import picoscope
scope = picoscope.Picoscope6407(open_device=True)
scope.set_active_channels(["A","B","C"])
scope.set_trigger("C",0.3) #trigger-channel label and fractional trigger value
scope.initialise_measurement(samples=int(1e3))
scope.acquire_and_readout(timebase=2) #see documentation for meaning of timebase. Small means short.

figure(1),clf()
for c in sorted(scope.active_channels):
	plot(1e9*scope.time_axis,1e3*scope.data[c],".--",label=c)

xlabel("time (ns)"),ylabel("signal (mV)")
xlim(0,500),grid(1),legend()
