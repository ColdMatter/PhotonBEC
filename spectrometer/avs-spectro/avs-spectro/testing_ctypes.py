import ctypes
from ctypes import pointer, c_char, sizeof, c_ushort, c_double, c_int, Structure, c_uint32,c_float
from ctypes import c_bool, c_short, c_uint
from ctypes.wintypes import HWND
from time import sleep

dll = ctypes.WinDLL("D://Control/spectrometer/AS5216.dll")

class DarkCorrectionType(Structure):
	_fields_ = [
		("m_Enable", c_char),
		("m_ForgetPercentage", c_char)]

class SmoothingType(Structure):
	_fields_ = [
		("m_SmoothPix", c_ushort),
		("m_SmoothModel", c_char)]

class TriggerType(Structure):
	_fields_ = [
		("m_Mode", c_char),
		("m_Source", c_char),
		("m_Type", c_char)]

class ControlSettingsType(Structure):
	_fields_ = [
		("m_StrobeControl", c_ushort),
		("m_LaserDelay", c_uint32),
		("m_LaserWidth", c_uint32),
		("m_LaserWaveLength", c_float),
		("m_StoreToRam", c_ushort)]

class avs_id(Structure):
	_fields_=  [
		("m_aSerialId",c_char*10),
		("m_aUserFriendlyId",c_char*64),
		("m_Status",ctypes.c_int8)]

class detector_type(Structure):
	_fields_ = [
		("m_SensorType",c_char),
		("m_NrPixels",c_ushort),
		("m_aFit",c_float*5),
		("m_NLEnable",c_bool),
		("m_aNLCorrect",c_double*8),
		("m_aLowNLCounts",c_double),
		("m_aHighNLCounts",c_double),
		("m_Gain",c_float*2),
		("m_Reserved",c_float),
		("m_Offset",c_float*2),
		("m_ExtOffset",c_float),
		("m_DefectivePixels",c_ushort*30)]		
		
class meas_config_type(Structure):
		_fields_ = [
			("m_StartPixel", c_ushort),
			("m_StopPixel", c_ushort),
			("m_IntegrationTime", c_float),
			("m_IntegrationDelay", c_uint32),
			("m_NrAverages", c_uint32),
			("m_CorDynDark", DarkCorrectionType),
			("m_Smoothing", SmoothingType),
			("m_SaturationDetection", c_char),
			("m_Trigger", TriggerType),
			("m_Control", ControlSettingsType)]	


dll.AVS_Init(0)
n_devices = dll.AVS_GetNrOfDevices()
test_id = (avs_id * n_devices)()
ctypes.memset(ctypes.addressof(test_id), 0, ctypes.sizeof(test_id))

size = c_uint32(sizeof(avs_id))
total_size = c_uint32(sizeof(avs_id * n_devices))
print n_devices, " devices found"

dll.AVS_GetList(c_uint(n_devices*size.value),pointer(total_size),pointer(test_id))

handle_0 = dll.AVS_Activate(pointer(test_id[0]))
#dll.AVS_Deactivate(handle_0)
print "Handle for first spectrometer is ", handle_0

num_pixels = c_ushort()

dll.AVS_GetNumPixels(handle_0, pointer(num_pixels))
print "Spectrometer has ", num_pixels.value, " pixels"
lamb = (c_double*num_pixels.value)()
spec = (c_double*num_pixels.value)()
time_label = c_uint32()
dll.AVS_GetLambda(handle_0, pointer(lamb))
extracted_lambdas = [x for x in lamb] #To create a more pythonic list
print min(extracted_lambdas), max(extracted_lambdas)

measureConfig = meas_config_type()
ctypes.memset(ctypes.addressof(measureConfig), 0, ctypes.sizeof(measureConfig))

startPixel = c_ushort(0)
stopPixel = c_ushort(num_pixels.value - 1)
intTime = c_float(100)
nAverages = c_uint32(1)

measureConfig.m_StartPixel = startPixel
measureConfig.m_StopPixel = stopPixel
measureConfig.m_IntegrationTime = intTime
measureConfig.m_IntegrationDelay = 1
measureConfig.m_NrAverages = nAverages

n_measure = c_short(-1) #Number of measurements to make. -1 means infintity.

#windows_handle = HWND()

err_prepare = dll.AVS_PrepareMeasure(handle_0, pointer(measureConfig))
print err_prepare
err_measure = dll.AVS_Measure(handle_0, None, n_measure)
#dll.AVS_StopMeasure(handle_0)
print err_measure
sleep(0.5)
err_poll = dll.AVS_PollScan(handle_0)
print err_poll
err_data = dll.AVS_GetScopeData(handle_0,pointer(time_label),pointer(spec))
print err_data
extracted_spec = [x for x in spec] #To create a more pythonic list

figure(1),clf()
plot(extracted_lambdas,extracted_spec)

for i in range(n_devices):
	print test_id[i].m_aSerialId
	print test_id[i].m_Status

#	//the default for most stuff is zero which is convienant
	#memset(&measureConfig, 0, sizeof(measureConfig));
#	if((err = AVS_PrepareMeasure(hDevice, &measureConfig)) != ERR_SUCCESS) {
#		fprintf(stderr, "PrepareMeasure(): %d\n", err);
#		return 1;
#	}

#	if((err = AVS_Measure(hDevice, NULL, -1)) != ERR_SUCCESS)
#		return printf("Measure(): %d\n", err);

