import ctypes

dll_path="C:/Program Files (x86)/Point Grey Research/FlyCapture2/bin/"
FlyCapDLL = ctypes.CDLL(dll_path+"FlyCapture2_C.dll") #Loads DLL into memory. Needs 32-bit C-API version.

#A challenge: get the FlyCapture2.dll version number fc2Version fc2Context
FlyCapDLL.fc2GetLibraryVersion()
FlyCapDLL.fc2GetNumOfCameras() #returns 7!

#temp=12
#FlyCapDLL.fc2CreateContext(ctypes.c_void_p(temp))

###fc2CreateContext (fc2Context pContext)

#Another challenge: get the number of cameras using "fc2GetNumOfCameras"
####FlyCapDLL.fc2Version

#EOF
