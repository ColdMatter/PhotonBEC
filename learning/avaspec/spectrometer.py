#exec(open("spectrometer.py").read())
from ctypes import *

dll_file = "C:\\Program Files (x86)\\AvaSoft8\\AS5216.dll"
avaspec = WinDLL(dll_file)

a_port = c_short(0) #0 means USB, in ctypes c_short format
#Initialise and find out number of devices
ndevices = avaspec.AVS_Init(a_port) 


"""
class AvsIdentityType(Structure):
	'''
	A C struct to pass arguments to 
	'''
	def __init__(self, id = None, user_friendly_id = None, status=None):
		self.m_aSerialId = c_char_p*10(id)
		self.m_aUserFriendlyId = DeviceStatus(user_friendly_id)
		self.m_Status = c_uint(status)
	#
"""
class AvsIdentityType(Structure):
	"""
	A C struct to pass arguments to 
	"""
	#_fields_=[("m_aSerialId",c_char_p),("m_aUserFriendlyId",c_char_p),("m_Status",c_uint)]
	_fields_=[("m_aSerialId",c_char_p),("m_aUserFriendlyId",c_char_p),("m_Status",c_char)]

def buffer2AvsID(buf):
	m_aS = buf.raw[:10] #serial id takes 10 bytes
	m_aU = buf.raw[10:74] #user-friendly serial id takes 64 bytes
	#m_S = c_uint(ord(buf.raw[74])) #status should be a single integer.
	m_S = c_char(buf.raw[74]) #status should be a single integer.
	return AvsIdentityType(m_aS,m_aU,m_S)
	
#---------------
nbytes = 80
a_ListSize = c_uint(nbytes) #number of bytes for storing list data
a_pRequiredSize = c_uint(ndevices*nbytes) #number of bytes needed to store information

buf = c_buffer(a_pRequiredSize.value)
avs_list_num_devices = avaspec.AVS_GetList(a_ListSize,a_pRequiredSize,buf)
avs_ident = buffer2AvsID(buf)
p_avs_ident = pointer(avs_ident)


#---------------
#Activate chosen spectrometer
#avs_handle = avaspec.AVS_Activate(p_avs_ident) #returns "1000"
avs_handle = avaspec.AVS_Activate(c_char_p(avs_ident.m_aSerialId)) #returns "1"


#---------------------------
#Now do something with the spectrometer
num_pixels=c_uint()
#err = avaspec.AVS_GetNumPixels(p_avs_ident,num_pixels)
lam_buf = c_buffer(4000)
#err = avaspec.AVS_GetLambda(p_avs_ident,lam_buf)

#EOF
