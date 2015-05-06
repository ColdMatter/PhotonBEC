//modified by LZ to have dll directory passed to setup flycap function as argument by pbec_experiment

#include "Python.h"
#include "numpy/arrayobject.h"

#include <windows.h>

static HMODULE flycap = NULL;
typedef unsigned char* (*GCI)(unsigned int*, int*, int*, int*);

typedef int (*SFC)(unsigned int, char*, char*, char*, char*, char*, char*);
typedef int (*GFCI)(unsigned int, unsigned int*, int*, int*, int*);
typedef int (*GFCD)(unsigned int, unsigned char*, unsigned int);
typedef int (*CFC)(unsigned int);

typedef int (*GFCP)(unsigned int, int, bool*, bool*, bool*, bool*, bool*, int*, int*, float*);
typedef int (*SFCP)(unsigned int, int, bool, bool, bool, bool, bool, int, int, float);
typedef int (*GFCPI)(unsigned int, int, bool*, bool*, bool*, bool*, bool*, bool*, bool*,
	unsigned int*, unsigned int*, float*, float*, char*, char*);

typedef int (*GFCF7I)(unsigned int, int*, int*, int*, int*, int*, int*, int*, int*, int*);
typedef int (*GFCF7C)(unsigned int, int*, int*, int*, int*, int*, int*);
typedef int (*SFCF7C)(unsigned int, int, int, int, int, int);

typedef int (*STM)(unsigned int, bool, bool);
typedef int (*WFTR)(unsigned int);
typedef int (*FST)(unsigned int);

static SFC fSetupFlyCap = NULL;
static GFCI fGetFlyCapImage = NULL;
static GFCD fGetFlyCapData = NULL;
static CFC fCloseFlyCap = NULL;

static GFCP fGetFlyCapProperty = NULL;
static SFCP fSetFlyCapProperty = NULL;
static GFCPI fGetFlyCapPropertyInfo = NULL;

static GFCF7I fGetFlyCapFormat7Info = NULL;
static GFCF7C fGetFlyCapFormat7Configuration = NULL;
static SFCF7C fSetFlyCapFormat7Configuration = NULL;

static STM fSetTriggerMode = NULL;
static WFTR fWaitForTriggerReady = NULL;
static FST fFireSoftwareTrigger = NULL;

//http://www.tutorialspoint.com/python/python_further_extensions.htm
//https://docs.python.org/2/extending/extending.html
//http://dan.iel.fm/posts/python-c-extensions/
static PyObject* pyflycap_helloworld(PyObject* self, PyObject* args) {
	printf("compiled on " __DATE__ " " __TIME__ "\n");
	Py_RETURN_NONE;
}

//if you change the error codes in FlyCapture2Test.cpp you'll have to change stuff here too
//array which maps from error code to string explaination
const char* ERRORS_SETUPFLYCAP[] = {"Success", "bad handle", "GetNumOfCameras() failed",
	"No cameras detected", "GetCameraFromIndex() failed", "cam.Connect() failed",
	"cam.GetCameraInfo() failed", "cam.Disconnect() failed", "Serial number not found",
	"cam.StartCapture() failed"};
const char* ERRORS_GETFLYCAPIMAGE[] = {"Success", "bad handle", "cam.RetrieveBuffer() failed",
	"image.Convert() failed"};

static PyObject* pyflycap_setupflycap(PyObject* self, PyObject* args) {
	
	char *dllDirectory; 
	unsigned int serialNumber;
	if(PyArg_ParseTuple(args, "is", &serialNumber, &dllDirectory) == 0) {
		return NULL;
	}
	if(!flycap) {
		SetDllDirectory(dllDirectory);
		flycap = LoadLibrary("FlyCapture2Test.dll");
	}
	if(!flycap) {
		char line[512];
		snprintf(line, sizeof(line), "Couldnt load library: %d\n", GetLastError());
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	if(flycap) {
		fSetupFlyCap = (SFC)GetProcAddress(flycap, "SetupFlyCap");
		fGetFlyCapImage = (GFCI)GetProcAddress(flycap, "GetFlyCapImage");
		fGetFlyCapData = (GFCD)GetProcAddress(flycap, "GetFlyCapData"); 
		fCloseFlyCap = (CFC)GetProcAddress(flycap, "CloseFlyCap");
		fGetFlyCapProperty = (GFCP)GetProcAddress(flycap, "GetFlyCapProperty");
		fSetFlyCapProperty = (SFCP)GetProcAddress(flycap, "SetFlyCapProperty");
		fGetFlyCapPropertyInfo = (GFCPI)GetProcAddress(flycap, "GetFlyCapPropertyInfo");
		fGetFlyCapFormat7Info = (GFCF7I)GetProcAddress(flycap, "GetFlyCapFormat7Info");
		fGetFlyCapFormat7Configuration = (GFCF7C)GetProcAddress(flycap, "GetFlyCapFormat7Configuration");
		fSetFlyCapFormat7Configuration = (SFCF7C)GetProcAddress(flycap, "SetFlyCapFormat7Configuration");
		fSetTriggerMode = (STM)GetProcAddress(flycap, "SetTriggerMode");
		fWaitForTriggerReady = (WFTR)GetProcAddress(flycap, "WaitForTriggerReady");
		fFireSoftwareTrigger = (FST)GetProcAddress(flycap, "FireSoftwareTrigger");
		
		if(!fSetupFlyCap || !fGetFlyCapImage || !fGetFlyCapData || !fCloseFlyCap
		|| !fGetFlyCapProperty || !fSetFlyCapProperty || !fGetFlyCapPropertyInfo
		|| !fGetFlyCapFormat7Info || !fGetFlyCapFormat7Configuration || !fSetFlyCapFormat7Configuration
		|| !fSetTriggerMode || !fWaitForTriggerReady || !fFireSoftwareTrigger)
			printf("fail to get procedure: %d\n", (int)GetLastError());
	}

	char modelName[512];
	char vendorName[512];
	char sensorInfo[512];
	char sensorResolution[512];
	char firmwareVersion[512];
	char firmwareBuildTime[512];
	int handleErr;
	if((handleErr = fSetupFlyCap(serialNumber, modelName, vendorName, sensorInfo,
			sensorResolution, firmwareVersion, firmwareBuildTime)) < 0) {
		char line[512];
		snprintf(line, sizeof(line), "SetupFlyCap(): %s\n", ERRORS_SETUPFLYCAP[-handleErr]);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	return Py_BuildValue("(issssss)", handleErr, modelName, vendorName, sensorInfo,
			sensorResolution, firmwareVersion, firmwareBuildTime);
}

static PyObject* pyflycap_freelibrary(PyObject* self) {
	if(flycap) {
		FreeLibrary(flycap);
		flycap = NULL;
	}
	Py_RETURN_NONE;
}

//returns tuple with lots of information
//(datalength, row, col, bitsPerPixel)
static PyObject* pyflycap_getflycapimage(PyObject* self, PyObject* args) {

	int handle;
	if(PyArg_ParseTuple(args, "i", &handle) == 0) {
		return NULL;
	}

	unsigned int dataLen=0;
	int row=0, col=0, bitsPerPixel=0;
	int err;
	if((err = fGetFlyCapImage(handle, &dataLen, &row, &col, &bitsPerPixel)) != 0) {
		char line[512];
		snprintf(line, sizeof(line), "GetFlyCapImage(): %s\n", ERRORS_GETFLYCAPIMAGE[-err]);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	return Py_BuildValue("(iiii)", dataLen, row, col, bitsPerPixel);
}

static PyObject* pyflycap_getflycapdata(PyObject* self, PyObject* args) {

	int handle;
	PyObject *data_obj;
	if(PyArg_ParseTuple(args, "iO", &handle, &data_obj) == 0) {
		//printf("error!\n");
		return NULL;
	}
	PyObject* data = PyArray_FROM_OTF(data_obj, NPY_UINT8, NPY_OUT_ARRAY);
	if(!data) {
		Py_XDECREF(data);
		return NULL;
	}
	int dN = (int)PyArray_DIM(data, 0);
	unsigned char* c_data = (unsigned char*)PyArray_DATA(data);
	
	//note to self: GetFlyCapData() takes a unsigned char* but ive only worked out passing
	// int* with numpy, so play with that and make it work for unsigned char*
	//also be mindful of the option to select from multiple cameras
	
	int err; //there are no possible error codes in GetFlyCapData() so i wont bother with an error string list
	if((err = fGetFlyCapData(handle, c_data, dN)) != 0) {
		Py_DECREF(data);
		char line[512];
		snprintf(line, sizeof(line), "GetFlyCapData(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	
	Py_DECREF(data);
	Py_RETURN_NONE;
}

static PyObject* pyflycap_closeflycap(PyObject* self, PyObject* args) {
	int handle;
	if(PyArg_ParseTuple(args, "i", &handle) == 0) {
		return NULL;
	}
	fCloseFlyCap(handle);
	Py_RETURN_NONE;
}
/*
static GFCP fGetFlyCapProperty = NULL;
static SFCP fSetFlyCapProperty = NULL;
static GFCPI fGetFlyCapPropertyInfo = NULL;
*/
static PyObject* pyflycap_getproperty(PyObject* self, PyObject* args) {

	int handle;
	int type;
	if(PyArg_ParseTuple(args, "ii", &handle, &type) == 0) {
		return NULL;
	}
	
	int err;
	bool present, absControl, onePush, onOff, autoManualMode;
	int valueA, valueB;
	float absValue;
	if((err = fGetFlyCapProperty(handle, type, &present, &absControl, &onePush,
		&onOff, &autoManualMode, &valueA, &valueB, &absValue)) != 0) {
		
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "GetFlyCapProperty(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}

	return Py_BuildValue("[iiiiiiiif]", type, present, absControl,
		onePush, onOff, autoManualMode, valueA, valueB, absValue);
}

static PyObject* pyflycap_setproperty(PyObject* self, PyObject* args) {

	int err;
	int handle;
	int type;
	int present, absControl, onePush, onOff, autoManualMode;
	int valueA, valueB;
	float absValue;
	if(PyArg_ParseTuple(args, "i(iiiiiiiif)", &handle, &type, &present, &absControl,
		&onePush, &onOff, &autoManualMode, &valueA, &valueB, &absValue) == 0) {
		return NULL;
	}

	if((err = fSetFlyCapProperty(handle, type, present, absControl, onePush,
		onOff, autoManualMode, valueA, valueB, absValue)) != 0) {
		
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "SetFlyCapProperty(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}

	Py_RETURN_NONE;
}


static PyObject* pyflycap_getpropertyinfo(PyObject* self, PyObject* args) {

	int err;
	int handle;
	int type;
	if(PyArg_ParseTuple(args, "ii", &handle, &type) == 0) {
		return NULL;
	}

	bool present, autoSupported, manualSupported, onOffSupported, onePushSupported, absValSupported, readOutSupported;
	unsigned int min, max;
	float absMin, absMax;
	const int sk_maxStringLength = 512;
	char pUnits[sk_maxStringLength];
	char pUnitAbbr[sk_maxStringLength];
	if((err = fGetFlyCapPropertyInfo(handle, type, &present, &autoSupported, &manualSupported,
					&onOffSupported, &onePushSupported, &absValSupported,
					&readOutSupported, &min, &max, &absMin,
					&absMax, (char*)&pUnits, (char*)&pUnitAbbr)) != 0) {
		
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "GetFlyCapPropertyInfo(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	return Py_BuildValue("[iiiiiiiiiffss]", present, autoSupported, manualSupported,
					onOffSupported, onePushSupported, absValSupported,
					readOutSupported, min, max, absMin,
					absMax, pUnits, pUnitAbbr);
}

static PyObject* pyflycap_getformat7info(PyObject* self, PyObject* args) {
	int handle;
	if(PyArg_ParseTuple(args, "i", &handle) == 0) {
		return NULL;
	}
	int maxWidth, maxHeight, offsetHStepSize, offsetVStepSize, imageHStepSize;
	int imageVStepSize, packetSize, minPacketSize, maxPacketSize;

	int err;
	if((err = fGetFlyCapFormat7Info(handle, &maxWidth, &maxHeight, &offsetHStepSize, &offsetVStepSize,
		&imageHStepSize, &imageVStepSize, &packetSize, &minPacketSize, &maxPacketSize)) != 0) {
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "GetFlyCapFormat7Info(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	
	return Py_BuildValue("(iiiiiiiii)", maxWidth, maxHeight, offsetHStepSize,
		offsetVStepSize, imageHStepSize, imageVStepSize, packetSize, minPacketSize, maxPacketSize);
}

static PyObject* pyflycap_getformat7config(PyObject* self, PyObject* args) {
	int handle;
	if(PyArg_ParseTuple(args, "i", &handle) == 0) {
		return NULL;
	}
	int offsetX, offsetY, width, height, pixelFormat, packetSize;
	int err;
	if((err = fGetFlyCapFormat7Configuration(handle, &offsetX, &offsetY, &width, &height,
		&pixelFormat, &packetSize)) != 0) {
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "GetFlyCapFormat7Configuration(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	return Py_BuildValue("[iiiii]", offsetX, offsetY, width,
		height, pixelFormat);
}

static PyObject* pyflycap_setformat7config(PyObject* self, PyObject* args) {

	int handle;
	int offsetX, offsetY, width, height, pixelFormat;
	if(PyArg_ParseTuple(args, "i(iiiii)", &handle, &offsetX, &offsetY, &width,
		&height, &pixelFormat) == 0) {
		return NULL;
	}

	int err;
	if((err = fSetFlyCapFormat7Configuration(handle, offsetX, offsetY, width, height, pixelFormat)) != 0) {
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "SetFlyCapFormat7Configuration(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* pyflycap_settriggermode(PyObject* self, PyObject* args) {
	int handle;
	bool enabled, software;
	if(PyArg_ParseTuple(args, "iii", &handle, &enabled, &software) == 0) {
		return NULL;
	}
	int err;
	if((err = fSetTriggerMode(handle, enabled, software)) != 0) {
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "SetTriggerMode(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* pyflycap_waitfortriggerready(PyObject* self, PyObject* args) {
	int handle;
	if(PyArg_ParseTuple(args, "i", &handle) == 0) {
		return NULL;
	}
	int err;
	if((err = fWaitForTriggerReady(handle)) != 0) {
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "WaitForTriggerReady(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* pyflycap_firesoftwaretrigger(PyObject* self, PyObject* args) {
	int handle;
	if(PyArg_ParseTuple(args, "i", &handle) == 0) {
		return NULL;
	}
	int err;
	if((err = fFireSoftwareTrigger(handle)) != 0) {
		char line[512]; //TODO have a human-readable error string here
		snprintf(line, sizeof(line), "FireSoftwareTrigger(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyMethodDef pyflycap_funcs[] = {
	{"helloworld", (PyCFunction)pyflycap_helloworld, METH_VARARGS, "doc string here"},
	{"setupflycap", (PyCFunction)pyflycap_setupflycap, METH_VARARGS, "doc string here"},
	{"freelibrary", (PyCFunction)pyflycap_freelibrary, METH_NOARGS, "doc string here"},
	{"getflycapimage", (PyCFunction)pyflycap_getflycapimage, METH_VARARGS, "doc string here"},
	{"getflycapdata", (PyCFunction)pyflycap_getflycapdata, METH_VARARGS, "doc string here"},
	{"closeflycap", (PyCFunction)pyflycap_closeflycap, METH_VARARGS, "doc string here"},
	{"getproperty", (PyCFunction)pyflycap_getproperty, METH_VARARGS, "doc string here"},
	{"setproperty", (PyCFunction)pyflycap_setproperty, METH_VARARGS, "doc string here"},
	{"getpropertyinfo", (PyCFunction)pyflycap_getpropertyinfo, METH_VARARGS, "doc string here"},
	{"getformat7info", (PyCFunction)pyflycap_getformat7info, METH_VARARGS, "doc string here"},
	{"getformat7config", (PyCFunction)pyflycap_getformat7config, METH_VARARGS, "doc string here"},
	{"setformat7config", (PyCFunction)pyflycap_setformat7config, METH_VARARGS, "doc string here"},
	{"settriggermode", (PyCFunction)pyflycap_settriggermode, METH_VARARGS, "doc string here"},
	{"waitfortriggerready", (PyCFunction)pyflycap_waitfortriggerready, METH_VARARGS, "doc string here"},
	{"firesoftwaretrigger", (PyCFunction)pyflycap_firesoftwaretrigger, METH_VARARGS, "doc string here"},
	
    {NULL}
};


//load library and free library functions

PyMODINIT_FUNC initpyflycap(void)
{
    Py_InitModule3("pyflycap", pyflycap_funcs, "docstring here");
	import_array();
}

