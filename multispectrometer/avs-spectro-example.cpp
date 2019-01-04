
#include <windows.h>

#include <cstdio>

int main(void) {
	
	HMODULE lib = LoadLibrary(".\\avs-spectro\\Release\\avs-spectro.dll");
	if(!lib)
		printf("first error LoadLibrary(): %d\n", GetLastError());
		lib = LoadLibrary("avs-spectro.dll");
		if(!lib)
			return printf("LoadLibrary(): %d\n", GetLastError());
	printf("loaded dll\n");

	/*	
	typedef int (*HW)(int);
	HW fhelloworld = (HW)GetProcAddress(lib, "helloworld");	
	if(fhelloworld)
		fhelloworld(5);
	*/

	typedef int (*SA1)(long*, unsigned short*);
	typedef int (*SA2)(long, unsigned short, unsigned short, float, unsigned int, short);
	typedef int (*GL)(long, double*);
	typedef int (*RAS)(long, double*, unsigned int*, long);
	typedef int (*CA)(long);
	SA1 fSetupAVS1 = (SA1)GetProcAddress(lib, "SetupAVS1");
	SA2 fSetupAVS2 = (SA2)GetProcAddress(lib, "SetupAVS2");	
	GL fGetLambda = (GL)GetProcAddress(lib, "GetLambda");
	RAS fReadAVSSpectrum = (RAS)GetProcAddress(lib, "ReadAVSSpectrum");
	CA fCloseAVS = (CA)GetProcAddress(lib, "CloseAVS");
	printf("obtained all procs\n");

	int err;
	long hDevice;
	unsigned short pixelNum;
	if((err = fSetupAVS1(&hDevice, &pixelNum)) != 0) {
		printf("SetupAVS(): %d\n", err);
		fCloseAVS(hDevice);
		return 0;
	}
	printf("have setupavs1\n");

	double* lambda = new double[pixelNum];
	if((err = fGetLambda(hDevice, lambda)) != 0) {
		printf("GetLambda(): %d\n", err);
		fCloseAVS(hDevice);
		return 0;
	}
	
	if((err = fSetupAVS2(hDevice, 0, pixelNum - 1, 200.0, 1, 1)) != 0) {
		printf("SetupAVS2(): %d\n", err);
		fCloseAVS(hDevice);
		return 0;
	}
	printf("have setupavs2\n");

	double* spectrum = new double[pixelNum];
	unsigned int timestamp = 0;
	if((err = fReadAVSSpectrum(hDevice, spectrum, &timestamp, 10000)) != 0) {
		printf("ReadAVSSpectrum(): %d\n", err);
		fCloseAVS(hDevice);
		return 0;
	}
	printf("have readavsspectrum\n");

	for(int i = 725; i < 735; i++)
		printf("spectrum[lambda = %f] = %f\n", lambda[i], spectrum[i]);

	fCloseAVS(hDevice);
	delete[] lambda;
	if(spectrum)
		delete[] spectrum;

	printf("ending\n");
	return 0;
}
