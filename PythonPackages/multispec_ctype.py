import ctypes
from ctypes import pointer, c_char, sizeof, c_ushort
from ctypes import c_bool, c_short, c_uint, c_int8
from ctypes import c_double, c_int, Structure, c_uint32, c_float
from time import sleep
from avantes_datatypes import DarkCorrectionType, SmoothingType, TriggerType, ControlSettingsType, avs_id, detector_type, meas_config_type

#Get the DLL bought from Avantes
dll = ctypes.WinDLL("D://Control/spectrometer/AS5216.dll")


class multiSpectrometer(object):
	def __init__(self, do_setup=True):
		if do_setup:
			dll.AVS_Init(0)
			n_devices = dll.AVS_GetNrOfDevices()
			avs_id_list = (avs_id * n_devices)()
			ctypes.memset(ctypes.addressof(test_id), 0, ctypes.sizeof(test_id))

			size = c_uint32(sizeof(avs_id))
			total_size = c_uint32(sizeof(avs_id * n_devices))
			print n_devices, " devices found"

			dll.AVS_GetList(c_uint(n_devices*size.value),pointer(total_size),pointer(avs_id_list))
			
			self.serials = []
			self.device_mapping = {}
			self.statuses = []
			for i in range(n_devices):
				self.serials.append(avs_id_list[i].m_aSerialId)
				self.device_mapping.append({avs_id_list[i].m_aSerialId:i}
				self.statuses.append(avs_id_list[i].m_Status)
				
class ctypeSpectrometer(object):
	
				

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

