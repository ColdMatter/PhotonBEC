import sys
import ctypes
import ctypes.wintypes
import struct
import globals
from PyQt5.QtCore import *

AVS_SERIAL_LEN = 10
USER_ID_LEN = 64
WM_MEAS_READY = 0x8001

class AvsIdentityType(ctypes.Structure):
  _pack_ = 1
  _fields_ = [("SerialNumber", ctypes.c_char * AVS_SERIAL_LEN),
              ("UserFriendlyName", ctypes.c_char * USER_ID_LEN),
              ("Status", ctypes.c_char)]

class MeasConfigType(ctypes.Structure):
  _pack_ = 1
  _fields_ = [("m_StartPixel", ctypes.c_uint16),
              ("m_StopPixel", ctypes.c_uint16),
              ("m_IntegrationTime", ctypes.c_float),
              ("m_IntegrationDelay", ctypes.c_uint32),
              ("m_NrAverages", ctypes.c_uint32),
              ("m_CorDynDark_m_Enable", ctypes.c_uint8), # nesting of types does NOT work!!
              ("m_CorDynDark_m_ForgetPercentage", ctypes.c_uint8),
              ("m_Smoothing_m_SmoothPix", ctypes.c_uint16),
              ("m_Smoothing_m_SmoothModel", ctypes.c_uint8),
              ("m_SaturationDetection", ctypes.c_uint8),
              ("m_Trigger_m_Mode", ctypes.c_uint8),
              ("m_Trigger_m_Source", ctypes.c_uint8),
              ("m_Trigger_m_SourceType", ctypes.c_uint8),
              ("m_Control_m_StrobeControl", ctypes.c_uint16),
              ("m_Control_m_LaserDelay", ctypes.c_uint32),
              ("m_Control_m_LaserWidth", ctypes.c_uint32),
              ("m_Control_m_LaserWaveLength", ctypes.c_float),
              ("m_Control_m_StoreToRam", ctypes.c_uint16)]

class DeviceConfigType(ctypes.Structure):
  _pack_ = 1
  _fields_ = [("m_Len", ctypes.c_uint16),
              ("m_ConfigVersion", ctypes.c_uint16),
              ("m_aUserFriendlyId", ctypes.c_char * USER_ID_LEN),
              ("m_Detector_m_SensorType", ctypes.c_uint8),                      
              ("m_Detector_m_NrPixels", ctypes.c_uint16),
              ("m_Detector_m_aFit", ctypes.c_float * 5),
              ("m_Detector_m_NLEnable", ctypes.c_bool),
              ("m_Detector_m_aNLCorrect", ctypes.c_double * 8),
              ("m_Detector_m_aLowNLCounts", ctypes.c_double),
              ("m_Detector_m_aHighNLCounts", ctypes.c_double),
              ("m_Detector_m_Gain", ctypes.c_float * 2),
              ("m_Detector_m_Reserved", ctypes.c_float),
              ("m_Detector_m_Offset", ctypes.c_float * 2),
              ("m_Detector_m_ExtOffset", ctypes.c_float),
              ("m_Detector_m_DefectivePixels", ctypes.c_uint16 * 30),
              ("m_Irradiance_m_IntensityCalib_m_Smoothing_m_SmoothPix", ctypes.c_uint16),
              ("m_Irradiance_m_IntensityCalib_m_Smoothing_m_SmoothModel", ctypes.c_uint8),
              ("m_Irradiance_m_IntensityCalib_m_CalInttime", ctypes.c_float),
              ("m_Irradiance_m_IntensityCalib_m_aCalibConvers", ctypes.c_float * 4096),
              ("m_Irradiance_m_CalibrationType", ctypes.c_uint8),
              ("m_Irradiance_m_FiberDiameter", ctypes.c_uint32),  
              ("m_Reflectance_m_Smoothing_m_SmoothPix", ctypes.c_uint16),
              ("m_Reflectance_m_Smoothing_m_SmoothModel", ctypes.c_uint8),
              ("m_Reflectance_m_CalInttime", ctypes.c_float),
              ("m_Reflectance_m_aCalibConvers", ctypes.c_float * 4096),
              ("m_SpectrumCorrect", ctypes.c_float * 4096),
              ("m_StandAlone_m_Enable", ctypes.c_bool),
              ("m_StandAlone_m_Meas_m_StartPixel", ctypes.c_uint16),
              ("m_StandAlone_m_Meas_m_StopPixel", ctypes.c_uint16),
              ("m_StandAlone_m_Meas_m_IntegrationTime", ctypes.c_float),
              ("m_StandAlone_m_Meas_m_IntegrationDelay", ctypes.c_uint32),
              ("m_StandAlone_m_Meas_m_NrAverages", ctypes.c_uint32),
              ("m_StandAlone_m_Meas_m_CorDynDark_m_Enable", ctypes.c_uint8), 
              ("m_StandAlone_m_Meas_m_CorDynDark_m_ForgetPercentage", ctypes.c_uint8),
              ("m_StandAlone_m_Meas_m_Smoothing_m_SmoothPix", ctypes.c_uint16),
              ("m_StandAlone_m_Meas_m_Smoothing_m_SmoothModel", ctypes.c_uint8),
              ("m_StandAlone_m_Meas_m_SaturationDetection", ctypes.c_uint8),
              ("m_StandAlone_m_Meas_m_Trigger_m_Mode", ctypes.c_uint8),
              ("m_StandAlone_m_Meas_m_Trigger_m_Source", ctypes.c_uint8),
              ("m_StandAlone_m_Meas_m_Trigger_m_SourceType", ctypes.c_uint8),
              ("m_StandAlone_m_Meas_m_Control_m_StrobeControl", ctypes.c_uint16),
              ("m_StandAlone_m_Meas_m_Control_m_LaserDelay", ctypes.c_uint32),
              ("m_StandAlone_m_Meas_m_Control_m_LaserWidth", ctypes.c_uint32),
              ("m_StandAlone_m_Meas_m_Control_m_LaserWaveLength", ctypes.c_float),
              ("m_StandAlone_m_Meas_m_Control_m_StoreToRam", ctypes.c_uint16),
              ("m_StandAlone_m_Nmsr", ctypes.c_int16),
              ("m_StandAlone_m_Reserved", ctypes.c_uint8 * 12), # SD Card, do not use
              ("m_Temperature_1_m_aFit", ctypes.c_float * 5),
              ("m_Temperature_2_m_aFit", ctypes.c_float * 5),
              ("m_Temperature_3_m_aFit", ctypes.c_float * 5),
              ("m_TecControl_m_Enable", ctypes.c_bool),
              ("m_TecControl_m_Setpoint", ctypes.c_float),
              ("m_TecControl_m_aFit", ctypes.c_float * 2),
              ("m_ProcessControl_m_AnalogLow", ctypes.c_float * 2),
              ("m_ProcessControl_m_AnalogHigh", ctypes.c_float * 2),
              ("m_ProcessControl_m_DigitalLow", ctypes.c_float * 10),
              ("m_ProcessControl_m_DigitalHigh", ctypes.c_float * 10),
              ("m_Reserved", ctypes.c_uint8 * 13832)]

def AVS_Init(x):
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int)
    paramflags = (1, "port",),
    AVS_Init = prototype(("AVS_Init", lib), paramflags)
    ret = AVS_Init(x) 
    return ret 

def AVS_GetNrOfDevices():
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int)
    AVS_GetNrOfDevices = prototype(("AVS_GetNrOfDevices", lib),)
    ret = AVS_GetNrOfDevices()
    return ret

def AVS_GetList(listsize, requiredsize, IDlist):
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(AvsIdentityType))
    paramflags = (1, "listsize",), (2, "requiredsize",), (2, "IDlist",),
    AVS_GetList = prototype(("AVS_GetList", lib), paramflags)
    ret = AVS_GetList(listsize)
    # looks like you only pass the '1' parameters here
    # the '2' parameters are returned in 'ret' !!!
    return ret

def AVS_Activate(deviceID):
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.POINTER(AvsIdentityType))
    paramflags = (1, "deviceId",),
    AVS_Activate = prototype(("AVS_Activate", lib), paramflags)
    ret = AVS_Activate(deviceID)
    return ret

def AVS_PrepareMeasure(handle, measconf):
    lib = ctypes.WinDLL("avaspecx64.dll")
    datatype = ctypes.c_byte * 41
    data = datatype()
    temp = datatype()
    temp = struct.pack("HHfIIBBHBBBBBHIIfH", measconf.m_StartPixel,
                                             measconf.m_StopPixel,
                                             measconf.m_IntegrationTime,
                                             measconf.m_IntegrationDelay,
                                             measconf.m_NrAverages,
                                             measconf.m_CorDynDark_m_Enable,
                                             measconf.m_CorDynDark_m_ForgetPercentage,
                                             measconf.m_Smoothing_m_SmoothPix,
                                             measconf.m_Smoothing_m_SmoothModel,
                                             measconf.m_SaturationDetection,
                                             measconf.m_Trigger_m_Mode,
                                             measconf.m_Trigger_m_Source,
                                             measconf.m_Trigger_m_SourceType,
                                             measconf.m_Control_m_StrobeControl,
                                             measconf.m_Control_m_LaserDelay,
                                             measconf.m_Control_m_LaserWidth,
                                             measconf.m_Control_m_LaserWaveLength,
                                             measconf.m_Control_m_StoreToRam )

# copy bytes from temp to data, otherwise you will get a typing error below
# why is this necessary?? they have the same type to start with ??
    x = 0
    while (x < 41): # 0 through 40
        data[x] = temp[x]
        x += 1
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_byte * 41)
    paramflags = (1, "handle",), (1, "measconf",),  
    AVS_PrepareMeasure = prototype(("AVS_PrepareMeasure", lib), paramflags)
    ret = AVS_PrepareMeasure(handle, data)
    return ret

def AVS_Measure(handle, windowhandle, nummeas):
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.HWND, ctypes.c_uint16)
    paramflags = (1, "handle",), (1, "windowhandle",), (1, "nummeas"),
    AVS_Measure = prototype(("AVS_Measure", lib), paramflags)
    ret = AVS_Measure(handle, windowhandle, nummeas) 
    return ret

class callbackclass(QObject):
    newdata = pyqtSignal()
    def __init__(self):
        QObject.__init__(self, parent)
        self.newdata.connect(PyQt5_demo.MainWindow.handle_newdata)
    def callback(self, handle, error):
        self.newdata.emit() # signal must be from a class !!

def AVS_MeasureCallback(handle, adres, nummeas):
    CBTYPE = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, CBTYPE, ctypes.c_uint16)
    paramflags = (1, "handle",), (1, "adres",), (1, "nummeas"),
    AVS_MeasureCallback = prototype(("AVS_MeasureCallback", lib), paramflags)
    ret = AVS_MeasureCallback(handle, CBTYPE(callbackclass.callback), nummeas)  # CRASHES python

def AVS_StopMeasure(handle):
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int)
    paramflags = (1, "handle",),
    AVS_StopMeasure = prototype(("AVS_StopMeasure", lib), paramflags)
    ret = AVS_StopMeasure(handle)
    return ret

def AVS_PollScan(handle):
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int)
    paramflags = (1, "handle",),
    AVS_PollScan = prototype(("AVS_PollScan", lib), paramflags)
    ret = AVS_PollScan(handle)
    return ret
    
def AVS_GetScopeData(handle, timelabel, spectrum):
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_double * 4096))
    paramflags = (1, "handle",), (2, "timelabel",), (2, "spectrum",),
    AVS_GetScopeData = prototype(("AVS_GetScopeData", lib), paramflags)
    ret = AVS_GetScopeData(handle)
    return ret

def AVS_GetParameter(handle, size, reqsize, deviceconfig):
    lib = ctypes.WinDLL("avaspecx64.dll")
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(DeviceConfigType))
    paramflags = (1, "handle",), (1, "size",), (2, "reqsize",), (2, "deviceconfig",),
    AVS_GetParameter = prototype(("AVS_GetParameter", lib), paramflags)
    ret = AVS_GetParameter(handle, size)
    return ret

def AVS_SetParameter(handle, deviceconfig):
    lib = ctypes.WinDLL("avaspecx64.dll")
    datatype = ctypes.c_byte * 63484
    data = datatype()
    temp = datatype()
    temp = struct.pack("HH64B" +
                       "BH5f?8ddd2ff2ff30H" +      # Detector
                       "HBf4096fBI" +              # Irradiance
                       "HBf4096f" +                # Reflectance
                       "4096f" +                   # SpectrumCorrect
                       "?HHfIIBBHBBBBBHIIfHH12B" + # StandAlone 
                       "5f5f5f" +                  # Temperature
                       "?f2f" +                    # TecControl
                       "2f2f10f10f " +             # ProcessControl
                       "13832B",                   # Reserved
                       deviceconfig.mLen,
                       deviceconfig.m_ConfigVersion,
                       deviceconfig.m_aUserFriendlyId,
                       deviceconfig.m_Detector_m_SensorType,
                       deviceconfig.m_Detector_m_NrPixels,
                       deviceconfig.m_Detector_m_aFit,
                       deviceconfig.m_Detector_m_NLEnable,
                       deviceconfig.m_Detector_m_aNLCorrect,
                       deviceconfig.m_Detector_m_aLowNLCounts,
                       deviceconfig.m_Detector_m_aHighNLCounts,
                       deviceconfig.m_Detector_m_Gain,
                       deviceconfig.m_Detector_m_Reserved,
                       deviceconfig.m_Detector_m_Offset,
                       deviceconfig.m_Detector_m_ExtOffset,
                       deviceconfig.m_Detector_m_DefectivePixels,
                       deviceconfig.m_Irradiance_m_IntensityCalib_m_Smoothing_m_SmoothPix,
                       deviceconfig.m_Irradiance_m_IntensityCalib_m_Smoothing_m_SmoothModel,
                       deviceconfig.m_Irradiance_m_IntensityCalib_m_CalInttime,
                       deviceconfig.m_Irradiance_m_IntensityCalib_m_aCalibConvers,
                       deviceconfig.m_Irradiance_m_CalibrationType,
                       deviceconfig.m_Irradiance_m_FiberDiameter,
                       deviceconfig.m_Reflectance_m_Smoothing_m_SmoothPix,
                       deviceconfig.m_Reflectance_m_Smoothing_m_SmoothModel,
                       deviceconfig.m_Reflectance_m_CalInttime,
                       deviceconfig.m_Reflectance_m_aCalibConvers,
                       deviceconfig.m_SpectrumCorrect,
                       deviceconfig.m_StandAlone_m_Enable,
                       deviceconfig.m_StandAlone_m_Meas_m_StartPixel,
                       deviceconfig.m_StandAlone_m_Meas_m_StopPixel,
                       deviceconfig.m_StandAlone_m_Meas_m_IntegrationTime,
                       deviceconfig.m_StandAlone_m_Meas_m_IntegrationDelay,
                       deviceconfig.m_StandAlone_m_Meas_m_NrAverages,
                       deviceconfig.m_StandAlone_m_Meas_m_CorDynDark_m_Enable, 
                       deviceconfig.m_StandAlone_m_Meas_m_CorDynDark_m_ForgetPercentage,
                       deviceconfig.m_StandAlone_m_Meas_m_Smoothing_m_SmoothPix,
                       deviceconfig.m_StandAlone_m_Meas_m_Smoothing_m_SmoothModel,
                       deviceconfig.m_StandAlone_m_Meas_m_SaturationDetection,
                       deviceconfig.m_StandAlone_m_Meas_m_Trigger_m_Mode,
                       deviceconfig.m_StandAlone_m_Meas_m_Trigger_m_Source,
                       deviceconfig.m_StandAlone_m_Meas_m_Trigger_m_SourceType,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_StrobeControl,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_LaserDelay,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_LaserWidth,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_LaserWaveLength,
                       deviceconfig.m_StandAlone_m_Meas_m_Control_m_StoreToRam,
                       deviceconfig.m_StandAlone_m_Nmsr,
                       deviceconfig.m_StandAlone_m_Reserved,
                       deviceconfig.m_Temperature_1_m_aFit,
                       deviceconfig.m_Temperature_2_m_aFit,
                       deviceconfig.m_Temperature_3_m_aFit,
                       deviceconfig.m_TecControl_m_Enable,
                       deviceconfig.m_TecControl_m_Setpoint,
                       deviceconfig.m_TecControl_m_aFit,
                       deviceconfig.m_ProcessControl_m_AnalogLow,
                       deviceconfig.m_ProcessControl_m_AnalogHigh,
                       deviceconfig.m_ProcessControl_m_DigitalLow,
                       deviceconfig.m_ProcessControl_m_DigitalHigh,
                       deviceconfig.m_Reserved)
    x = 0
    while (x < 63484): # 0 through 63483
        data[x] = temp[x]
        x += 1
    prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_byte * 63484)
    paramflags = (1, "handle",), (1, "deviceconfig",),  
    AVS_SetParameter = prototype(("AVS_SetParameter", lib), paramflags)
    ret = AVS_SetParameter(handle, data)
    return ret