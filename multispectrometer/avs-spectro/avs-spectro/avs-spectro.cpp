// avs-spectro.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"

#include "as5216.h"

#include <Windows.h>

#include <cstdio>

#include <typeinfo>

#include <list>

typedef struct
{
    AvsIdentityType            spec1;
    AvsIdentityType            spec2;
 } PairofSpecs;

//function to set up, function which blocks and gets data, function to clean up

#define DLLFUN extern "C" __declspec(dllexport)

DLLFUN int helloworld(int h) {
	return printf("hello world from avs-spectro\n");
}

//0 = success
//read the source to get different error codes
//hDevice is the handle of the device
//pixelNum is the number of pixels in the CCD array, an important number
DLLFUN int SetupAVS1(long* hDevice, unsigned short* pixelNum) {
	long ret = AVS_Init(0);
	if (ret < 0) {
		fprintf(stderr, "AVS_Init(): %d\n", ret);
		return 1;
	}

	int deviceCount = AVS_GetNrOfDevices();
	printf("device count = %d\n", deviceCount);
	//if(deviceCount > 1) {
	//	printf("sorry, this library was not yet coded for more than one AvaSoft"
	//		" spectrometer\nedit the library to dynamically allocate memory here"
	//		" for AvsIdentityType\n~jakov\n");
	//	return 2;
	//}
	if (deviceCount == 0) {
		fprintf(stderr, "no devices found\n");
		return 3;
	}


	int max_num_spectrometers = 10;
	//Ideally would pass max_num_spectrometers as a variable to determine the length of avsID_list, but can't
	//do this. Sorry.
	AvsIdentityType avsID_list[10];

	AvsIdentityType avsID;
	unsigned int idSize = sizeof(AvsIdentityType);
	unsigned int idSize_all = idSize*10;
	int err = AVS_GetList(10*sizeof(AvsIdentityType), &idSize_all, avsID_list);
	//printf("idsize = %d\n", idSize);

	for (int i = 0; i < deviceCount; ++i) {
		avsID = avsID_list[i];
		
		printf("avsID (serial number, user friendly name, status) = (%s, %s, %d)\n",
			avsID.SerialNumber, avsID.UserFriendlyName, avsID.Status);
		AvsHandle handle = AVS_Activate(&avsID);
		printf("hDevice = %lu\n", handle);
	}

	if(err <= 0) {
		fprintf(stderr, "AVS_GetList(): %d\n", err);
		return 4;
	}
	
	
	
	//I think these checks get too complicated with multiple spectrometers. BTW 20170424
	//switch(avsID.Status) {
	//	case UNKNOWN:
	//	case IN_USE_BY_APPLICATION:
	//	case IN_USE_BY_OTHER:
	//		fprintf(stderr, "spectrometer not found or not available, %d\n", avsID.Status);
	//		return 5;
	//	case AVAILABLE:
	//		//fprintf(stderr, "spectrometer found and available\n");
	//		break;
	//	default:
	//		fprintf(stderr, "what the hell?!\n");
	//		return 6;
	//}
	
	//*hDevice = AVS_Activate(&avsID);
	//printf("hDevice = %lu\n",hDevice);
	//if(*hDevice == INVALID_AVS_HANDLE_VALUE) {
	//	fprintf(stderr, "bad AVS_Activate\n");
	//	return 7;
	//}
	
	//if((err = AVS_GetNumPixels(*hDevice, pixelNum)) != ERR_SUCCESS) {
	//	fprintf(stderr, "GetNumPixel(): %d\n", err);
	//	return 8;
	//}
	//printf("pixelNum = %d\n", pixelNum);

	//if((err = AVS_UseHighResAdc(*hDevice, true)) != ERR_SUCCESS) {
	//	fprintf(stderr, "UseHighResAdc(): %d\n", err);
	//	return 9;
	//}
	return 0;
}

//0 = success
//lambda is a mapping from pixel number of wavelength, should be length pixelNum
DLLFUN int GetLambda(long hDevice, double* lambda) {
	int err;
	if((err = AVS_GetLambda(hDevice, lambda)) != ERR_SUCCESS) {
		fprintf(stderr, "GetLambda(): %d\n", err);
		return 1;
	}
	return 0;
}

//0 = success
//read the source to get different error codes
//start- and stopPixel define the length of the array you must pass o ReadAVSSpectrum()
//nMeasure is number of measurements after which ReadAVSSpectrum will block forever, or -1 for infinite
DLLFUN int SetupAVS2(long hDevice,
					 unsigned short startPixel,
					 unsigned short stopPixel,
					 float intTime,
					 unsigned int nAverages,
					 short nMeasure) {
	int err;

	MeasConfigType measureConfig;
	//the default for most stuff is zero which is convienant
	memset(&measureConfig, 0, sizeof(measureConfig));
	measureConfig.m_StartPixel = startPixel;
	measureConfig.m_StopPixel = stopPixel;
	measureConfig.m_IntegrationTime = intTime;
	measureConfig.m_IntegrationDelay = 1;
	measureConfig.m_NrAverages = nAverages;
	if((err = AVS_PrepareMeasure(hDevice, &measureConfig)) != ERR_SUCCESS) {
		fprintf(stderr, "PrepareMeasure(): %d\n", err);
		return 1;
	}

	if((err = AVS_Measure(hDevice, NULL, -1)) != ERR_SUCCESS)
		return printf("Measure(): %d\n", err);

	return 0;
}

//0 = success
//read the source to get different error codes
//hDevice is the handle of the device
//spectrum is where the data goes
//the timestamp is stored in timestamp by the spectrometer down to 10 microsecond precision
// read the manual for GetScopeData()
//function blocks but times out after timeout, this is mostly as insurance in case
// you've called it more times than nMeasure in SetupAVS2(), set to a couple of seconds
// to prevent ugly killing of the app
DLLFUN int ReadAVSSpectrum(long hDevice,
						   double* spectrum,
						   unsigned int* timestamp,
						   long timeout) {
	long st = GetTickCount();
	long et;
	int err;
	bool timedout = false;
	do {
		err = AVS_PollScan(hDevice);
		if(err != 0 && err != 1) {
			printf("PollScan(): %d\n", err);
			return 1;
		}
		Sleep(2);

		et = GetTickCount();
		//i didnt code an option for infinite timeout
		// because i hope people always use a finite one
		// set to 0x7fffffff if you really really need a long timeout
		timedout = et - st > timeout;
	} while(!timedout && err == 0);
	if(timedout) {
		fprintf(stderr, "timed out\n");
		return 2;
	}


	if((err = AVS_GetScopeData(hDevice, timestamp, spectrum)) != ERR_SUCCESS) {
		fprintf(stderr, "GetScopeData(): %d\n", err);
		return 3;
	}
	return 0;
}

DLLFUN int StopMeasure(long hDevice) {
	int err;
	printf("Inside avs-spectro\n");
	if((err = AVS_StopMeasure(hDevice)) != ERR_SUCCESS) {
		fprintf(stderr, "StopMeasure(): %d\n", err);
		return 1;
	}
	return 0;
}

DLLFUN int CloseAVS(long hDevice) {
	AVS_StopMeasure(hDevice);
	AVS_Deactivate(hDevice);
	AVS_Done(); //btw if you dont call these you have to restart the spectrometer after!
	return 0; //should error check all these, meh
}
