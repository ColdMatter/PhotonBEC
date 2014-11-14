
#include "Python.h"
#include "numpy/arrayobject.h"

#include <Windows.h>
#include <cstdio>

static HMODULE avs_spectro = NULL;
static long hDevice = 0;

typedef int (*SA1)(long*, unsigned short*);
typedef int (*GL)(long, double*);
typedef int (*SA2)(long, unsigned short, unsigned short, float, unsigned int, short);
typedef int (*RAS)(long, double*, unsigned int*, long);
typedef int (*CA)(long);
static SA1 fSetupAVS1 = NULL;
static SA2 fSetupAVS2 = NULL;
static GL fGetLambda = NULL;
static RAS fReadAVSSpectrum = NULL;
static CA fCloseAVS = NULL;

//http://www.tutorialspoint.com/python/python_further_extensions.htm
//https://docs.python.org/2/extending/extending.html
//http://dan.iel.fm/posts/python-c-extensions/
static PyObject* pyspectro_helloworld(PyObject* self, PyObject* args) {
	printf("compiled on %s %s\n", __DATE__, __TIME__);
	
	PyObject *doublearr_obj, *intarr_obj;
	if(PyArg_ParseTuple(args, "OO", &doublearr_obj, &intarr_obj) == 0) {
		printf("error!\n");
		return NULL;
	}
	PyObject* doublearr = PyArray_FROM_OTF(doublearr_obj, NPY_DOUBLE, NPY_OUT_ARRAY);
	PyObject* intarr = PyArray_FROM_OTF(intarr_obj, NPY_UINT8, NPY_OUT_ARRAY);
	if(!doublearr || !intarr) {
		Py_XDECREF(doublearr);
		Py_XDECREF(intarr);
		return NULL;
	}
	int dN = (int)PyArray_DIM(doublearr, 0);
	int iN = (int)PyArray_DIM(intarr, 0);
	double* c_doublearr = (double*)PyArray_DATA(doublearr);
	unsigned char* c_intarr = (unsigned char*)PyArray_DATA(intarr);
	if(c_intarr[0] == 1) {
		PyErr_SetString(PyExc_IOError, "hello");
		return NULL;
	}
	for(int i = 0; i < dN; i++)
		c_doublearr[i] = dN - i;
	for(int i = 0; i < iN; i++)
		c_intarr[i] = dN - i;
	Py_DECREF(doublearr);
	Py_DECREF(intarr);
	Py_RETURN_NONE;
}

//returns pixelNum
static PyObject* pyspectro_setupavs1(PyObject* self) {

	SetDllDirectory("D:\\Control\\spectrometer\\");
	//AS5216.dll is called by avs-spectro.dll.
	avs_spectro = LoadLibrary("avs-spectro.dll");
	if(!avs_spectro) {
		printf("couldnt load library: %d\n", (int)GetLastError());
		return NULL;
	}
	fSetupAVS1 = (SA1)GetProcAddress(avs_spectro, "SetupAVS1");
	fGetLambda = (GL)GetProcAddress(avs_spectro, "GetLambda");
	fSetupAVS2 = (SA2)GetProcAddress(avs_spectro, "SetupAVS2");
	fReadAVSSpectrum = (RAS)GetProcAddress(avs_spectro, "ReadAVSSpectrum");
	fCloseAVS = (CA)GetProcAddress(avs_spectro, "CloseAVS");
	if(!fSetupAVS1 || !fSetupAVS2 || !fGetLambda || !fReadAVSSpectrum || !fCloseAVS)
		printf("fail to get procedure: %d\n", (int)GetLastError());

	int err;
	unsigned short pixelNum;
	if((err = fSetupAVS1(&hDevice, &pixelNum)) != 0) {
		char line[512];
		snprintf(line, sizeof(line), "SetupAVS1(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	return Py_BuildValue("i", pixelNum);
}

//takes a numpy array of doubles of size pixelNum
static PyObject* pyspectro_getlambda(PyObject* self, PyObject* args) {

	PyObject *lambda_obj;
	if(PyArg_ParseTuple(args, "O", &lambda_obj) == 0)
		return NULL;
	PyObject* lambda = PyArray_FROM_OTF(lambda_obj, NPY_DOUBLE, NPY_OUT_ARRAY);
	if(!lambda) {
		Py_XDECREF(lambda);
		return NULL;
	}
	
	double* c_lambda = (double*)PyArray_DATA(lambda);
	
	int err;
	if((err = fGetLambda(hDevice, c_lambda)) != 0) {
		Py_DECREF(lambda);
		char line[512];
		snprintf(line, sizeof(line), "GetLambda(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	
	//int N = (int)PyArray_DIM(lambda, 0);
	//for(int i = 0; i < N; i++)
	//	c_lambda[i] = 532.0;
	
	Py_DECREF(lambda);
	Py_RETURN_NONE;
}

//startPixel and stopPixel are passed as a tuple
//intTime is a float
static PyObject* pyspectro_setupavs2(PyObject* self, PyObject* args) {

	int startPixel, stopPixel, nAverages, nMeasure;
	float intTime;
	if(PyArg_ParseTuple(args, "(ii)fii", &startPixel, &stopPixel, &intTime, &nAverages, &nMeasure) == 0)
		return NULL;

	int err;
	if((err = fSetupAVS2(hDevice, startPixel, stopPixel, intTime, nAverages, nMeasure)) != 0) {
		char line[512];
		snprintf(line, sizeof(line), "SetupAVS2(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject* pyspectro_readavsspectrum(PyObject* self, PyObject* args) {
	PyObject *spectrum_obj;
	unsigned int timeout;
	if(PyArg_ParseTuple(args, "Oi", &spectrum_obj, &timeout) == 0)
		return NULL;
	PyObject* spectrum = PyArray_FROM_OTF(spectrum_obj, NPY_DOUBLE, NPY_OUT_ARRAY);
	if(!spectrum) {
		Py_XDECREF(spectrum);
		return NULL;
	}
	//int N = (int)PyArray_DIM(spectrum, 0);
	double* c_spectrum = (double*)PyArray_DATA(spectrum);

	int err;
	unsigned int timestamp = 0;
	if((err = fReadAVSSpectrum(hDevice, c_spectrum, &timestamp, timeout)) != 0) {
		Py_DECREF(spectrum);
		char line[512];
		snprintf(line, sizeof(line), "ReadAVSSpectrum(): %d\n", err);
		PyErr_SetString(PyExc_IOError, line);
		return NULL;
	}
	Py_DECREF(spectrum);
	return Py_BuildValue("i", timestamp);
}

static PyObject* pyspectro_closeavs(PyObject* self, PyObject* args) {
	if(hDevice) {
		fCloseAVS(hDevice);
		hDevice = 0;
	}
	if(avs_spectro) {
		FreeLibrary(avs_spectro);
		avs_spectro = NULL;
	}
	Py_RETURN_NONE;
}

static PyMethodDef pyspectro_funcs[] = {
    {"helloworld", (PyCFunction)pyspectro_helloworld, METH_VARARGS, "doc string here"},
	{"setupavs1", (PyCFunction)pyspectro_setupavs1, METH_NOARGS, "doc string here"},
	{"getlambda", (PyCFunction)pyspectro_getlambda, METH_VARARGS, "doc string here"},
	{"setupavs2", (PyCFunction)pyspectro_setupavs2, METH_VARARGS, "doc string here"},
	{"readavsspectrum", (PyCFunction)pyspectro_readavsspectrum, METH_VARARGS, "doc string here"},
	{"closeavs", (PyCFunction)pyspectro_closeavs, METH_VARARGS, "doc string here"},
    {NULL}
};

PyMODINIT_FUNC initpyspectro(void)
{
    Py_InitModule3("pyspectro", pyspectro_funcs, "docstring here");
	import_array();
}