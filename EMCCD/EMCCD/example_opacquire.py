import time
import matplotlib.pyplot as plt

from EMCCD_backend import EMCCD, OpAcquire

opacquire = OpAcquire(VERBOSE=True)

FLAG, message, n_modes = opacquire.OA_Initialize()

FLAG, message, n_modes = opacquire.OA_GetNumberOfPreSetModes()
print("Number of OpAcquire modes is ", n_modes)

FLAG, message, modes = opacquire.OA_GetPreSetModeNames()
print("\n\nAvailable modes are:")
[print(mode) for mode in modes]

FLAG, message, n_params = opacquire.OA_GetNumberOfAcqParams(mode_name=modes[0])
print("Number of parameters:", n_params)

print("\n\n")
FLAG, message, params = opacquire.OA_GetModeAcqParams(mode_name=modes[0])
print("Parameters:")
print(params)

for i in range(0, n_params):
	print("Parameter", i)
	FLAG, message, param_value = opacquire.GetParamValue(mode_name=modes[0], param_name=params[i])
	print("Parameter: "+params[i]+" "+str(param_value))

mode = modes[9]
print("\n\n\nSetting mode to:")
FLAG, message = opacquire.OA_EnableMode(mode_name=mode)


FLAG, message = opacquire.SetImage(hbin=1, vbin=1, hstart=1, hend=opacquire.xpixels, vstart=1, vend=opacquire.ypixels)
FLAG, message = opacquire.StartAcquisition()
ACQUISITION_COMPLETE = False
while not ACQUISITION_COMPLETE:
	FLAG, message, info = opacquire.GetStatus()
	if info == "DRV_IDLE":
		ACQUISITION_COMPLETE = True
	time.sleep(0.5)
print(info)
FLAG, message, image = opacquire.GetAcquiredData()
print("Getting acquired data")
print(FLAG)
print(message)
print("-----------------")
plt.imshow(image)
plt.colorbar()
plt.show()