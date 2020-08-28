import time
import matplotlib.pyplot as plt

from EMCCD_backend import EMCCD

camera = EMCCD(VERBOSE=True)


FLAG, message = camera.SetTemperature(temperature=20)
#FLAG, message = camera.CoolerON()
#FLAG, message, temperature = camera.StabilizeTemperature()


FLAG, message = camera.SetAcquisitionMode(mode="single scan")
FLAG, message = camera.SetOutputAmplifier(mode="CCD")
FLAG, message = camera.SetReadMode(mode="image")
FLAG, message = camera.SetShutter(typ=1, mode='permanently open', closingtime=0, openingtime=0)
FLAG, message = camera.SetTriggerMode(mode="internal")
FLAG, message = camera.SetImage(hbin=1, vbin=1, hstart=1, hend=camera.xpixels, vstart=1, vend=camera.ypixels)


FLAG, message = camera.SetEMAdvanced(True)
FLAG, message, info = camera.GetEMGainRange()
FLAG, message = camera.SetEMCCDGain(gain=0)


FLAG, message = camera.SetExposureTime(time=0.01)
FLAG, message = camera.SetAccumulationCycleTime(time=0.001)
FLAG, message = camera.SetNumberAccumulations(number=10)
FLAG, message = camera.SetNumberKinetics(number=10)
FLAG, message = camera.SetKineticCycleTime(time=0.001)
FLAG, message, info = camera.GetAcquisitionTimings()
print(info)


FLAG, message = camera.SetHSSpeed(typ=1, index=0)
FLAG, message = camera.SetVSSpeed(index=1)



FLAG, message = camera.StartAcquisition()
ACQUISITION_COMPLETE = False
while not ACQUISITION_COMPLETE:
	FLAG, message, info = camera.GetStatus()
	if info == "DRV_IDLE":
		ACQUISITION_COMPLETE = True
	time.sleep(0.5)
print(info)





FLAG, message, image = camera.GetAcquiredData()
print("Getting acquired data")
print(FLAG)
print(message)
print("-----------------")
plt.imshow(image)
plt.colorbar()
plt.show()


#FLAG, message = camera.CoolerOFF()
FLAG, message = camera.ShutDown(temperature=20)