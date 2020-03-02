import ctypes
from ctypes import pointer, c_char, sizeof, c_ushort, c_ubyte
from ctypes import c_bool, c_short, c_uint, c_int8
from ctypes import c_double, c_int, Structure, c_uint32, c_float

#Define the custom Avantes data types. This is not a comprehensive list. See AS5216 documentation for more.
class DarkCorrectionType(Structure):
	_pack_ = 1
	_fields_ = [
		("m_Enable", c_ubyte),
		("m_ForgetPercentage", c_ubyte)]

class SmoothingType(Structure):
	_pack_ = 1
	_fields_ = [
		("m_SmoothPix", c_ushort),
		("m_SmoothModel", c_ubyte)]

class TriggerType(Structure):
	_pack_ = 1
	_fields_ = [
		("m_Mode", c_ubyte),
		("m_Source", c_ubyte),
		("m_SourceType", c_ubyte)]

class ControlSettingsType(Structure):
	_pack_ = 1
	_fields_ = [
		("m_StrobeControl", c_ushort),
		("m_LaserDelay", c_uint),
		("m_LaserWidth", c_uint),
		("m_LaserWaveLength", c_float),
		("m_StoreToRam", c_ushort)]

class avs_id(Structure):
	_pack_ = 1
	_fields_=  [
		("m_aSerialId",c_char*10),
		("m_aUserFriendlyId",c_char*64),
		("m_Status",c_int8)]

class detector_type(Structure):
	_pack_ = 1
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
	_pack_ = 1
	_fields_ = [
		("m_StartPixel", c_ushort),
		("m_StopPixel", c_ushort),
		("m_IntegrationTime", c_float),
		("m_IntegrationDelay", c_uint),
		("m_NrAverages", c_uint),
		("m_CorDynDark", DarkCorrectionType),
		("m_Smoothing", SmoothingType),
		("m_SaturationDetection", c_ubyte),
		("m_Trigger", TriggerType),
		("m_Control", ControlSettingsType)]	
