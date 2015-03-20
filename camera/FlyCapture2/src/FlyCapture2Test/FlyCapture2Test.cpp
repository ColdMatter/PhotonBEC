//=============================================================================
// Copyright © 2008 Point Grey Research, Inc. All Rights Reserved.
//
// This software is the confidential and proprietary information of Point
// Grey Research, Inc. ("Confidential Information").  You shall not
// disclose such Confidential Information and shall use it only in
// accordance with the terms of the license agreement you entered into
// with PGR.
//
// PGR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
// SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
// IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
// PURPOSE, OR NON-INFRINGEMENT. PGR SHALL NOT BE LIABLE FOR ANY DAMAGES
// SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
// THIS SOFTWARE OR ITS DERIVATIVES.
//=============================================================================
//=============================================================================
// $Id: FlyCapture2Test.cpp,v 1.19 2010-03-11 22:58:37 soowei Exp $
//=============================================================================

#include "stdafx.h"

#include "FlyCapture2.h"

#include <Windows.h>
#include <cstdlib>

//compiler arguments which make the function be exported
#define DLLFUN extern "C" __declspec(dllexport)

using namespace FlyCapture2;
/*
void PrintBuildInfo()
{
    FC2Version fc2Version;
    Utilities::GetLibraryVersion( &fc2Version );
    char version[128];
    sprintf( 
        version, 
        "FlyCapture2 library version: %d.%d.%d.%d\n", 
        fc2Version.major, fc2Version.minor, fc2Version.type, fc2Version.build );

    printf( version );

    char timeStamp[512];
    sprintf( timeStamp, "Application build date: %s %s\n\n", __DATE__, __TIME__ );

    printf( timeStamp );
}
*/

void PrintCameraInfo( CameraInfo* pCamInfo )
{
	printf("FlyCap2Test.dll compiled on " __DATE__ " " __TIME__ "\n");
    printf(
        "\n*** CAMERA INFORMATION ***\n"
        "Serial number - %u\n"
        "Camera model - %s\n"
        "Camera vendor - %s\n"
        "Sensor - %s\n"
        "Resolution - %s\n"
        "Firmware version - %s\n"
        "Firmware build time - %s\n\n",
        pCamInfo->serialNumber,
        pCamInfo->modelName,
        pCamInfo->vendorName,
        pCamInfo->sensorInfo,
        pCamInfo->sensorResolution,
        pCamInfo->firmwareVersion,
        pCamInfo->firmwareBuildTime );
}

/*
*** CAMERA INFORMATION ***
Serial number - 12350594
Camera model - Chameleon CMLN-13S2C
Camera vendor - Point Grey Research
Sensor - Sony ICX445AQ (1/3" 1296x964 CCD)
Resolution - 1296x964
Firmware version - 1.11.3.0
Firmware build time - Fri Feb 24 20:06:07 2012
*/

void PrintError( Error error )
{
	error.PrintErrorTrace();
}


//unsigned char* GetCameraImage(unsigned int* dataLen, int* row, int* col, int* bitsPerPixel) {
	//PrintBuildInfo();
	/*
	printf("changed 1543\n");

	*dataLen = 5;
	*row = 3;
	*col = 5;
	*bitsPerPixel = 8;
	char* h = new char[65];
	strcpy(h, "qwertyuiopasdfghjkl");
	return (unsigned char*)h;
	*/
	
#define MAX_CAM_COUNT 256
static Camera cams[MAX_CAM_COUNT];
static Image convertedImages[MAX_CAM_COUNT];
static int nextHandle = 0;

bool check_cam_handle(unsigned int handle) {
	return handle >= 0 && handle < MAX_CAM_COUNT;
}

//serialNumber = 0 if you just want the first/any one
//all strings you pass to must have length sk_maxStringLength = 512
DLLFUN int SetupFlyCap(unsigned int serialNumber, char* modelName, char* vendorName, char* sensorInfo,
						char* sensorResolution, char* firmwareVersion, char* firmwareBuildTime) {

    Error error;

    BusManager busMgr;
    unsigned int numCameras;
    error = busMgr.GetNumOfCameras(&numCameras);
    if (error != PGRERROR_OK)
    {
        PrintError( error );
        return -1;
    }

    if(numCameras == 0) {
		printf("No cameras detected\n");
		return -2;
	}

	bool connected = false;
	for(unsigned int i = 0; i < numCameras; i++) {
		PGRGuid guid;
		error = busMgr.GetCameraFromIndex(i, &guid);
		if (error != PGRERROR_OK)
		{
			PrintError( error );
			return -3;
		}

		// Connect to a camera
		error = cams[nextHandle].Connect(&guid);
		if (error != PGRERROR_OK)
		{
			PrintError( error );
			return -4;
		}
		connected = true;

		// Get the camera information
		CameraInfo camInfo;
		error = cams[nextHandle].GetCameraInfo(&camInfo);
		if (error != PGRERROR_OK)
		{
			PrintError( error );
			return -5;
		}

		if(serialNumber == 0 || serialNumber == camInfo.serialNumber) {
			//PrintCameraInfo(&camInfo);
			strncpy(modelName, camInfo.modelName, sk_maxStringLength);
			strncpy(vendorName, camInfo.vendorName, sk_maxStringLength);
			strncpy(sensorInfo, camInfo.sensorInfo, sk_maxStringLength);
			strncpy(sensorResolution, camInfo.sensorResolution, sk_maxStringLength);
			strncpy(firmwareVersion, camInfo.firmwareVersion, sk_maxStringLength);
			strncpy(firmwareBuildTime, camInfo.firmwareBuildTime, sk_maxStringLength);
			break;
		} else {
			error = cams[nextHandle].Disconnect();
			if (error != PGRERROR_OK)
			{
				PrintError( error );
				return -6;
			}
			connected = false;
		}
	}
	if(!connected) {
		printf("serial number not found\n");
		return -7;
	}

	// Start capturing images
    error = cams[nextHandle].StartCapture();
    if (error != PGRERROR_OK)
    {
        PrintError( error );
        return -8;
    }

	int ret = nextHandle;
	nextHandle++;
	if(nextHandle == MAX_CAM_COUNT) {
		printf("REACHED THE LIMIT OF CAMERA ALLOCATION\n");
	}
	return ret;
}

static PropertyType PROPERTY_TYPE_INTEGER_MAPPING[] = {BRIGHTNESS, AUTO_EXPOSURE, SHARPNESS, WHITE_BALANCE, HUE,
	SATURATION, GAMMA, IRIS, FOCUS, ZOOM, PAN, TILT, SHUTTER, GAIN, TRIGGER_MODE, TRIGGER_DELAY, FRAME_RATE, TEMPERATURE};

DLLFUN int GetFlyCapProperty(unsigned int handle, int type, bool* present, bool* absControl, bool* onePush, bool* onOff,
							 bool* autoManualMode, int* valueA, int* valueB, float* absValue) {

	if(!check_cam_handle(handle)) {
		return -1; //bad handle
	}

	Property prop;
	memset(&prop, 0, sizeof(prop));
	prop.type = PROPERTY_TYPE_INTEGER_MAPPING[type];
	Error error = cams[handle].GetProperty(&prop);
	if (error != PGRERROR_OK)
	{
		PrintError( error );
		return -2;
	}
	*present = prop.present;
	*absControl = prop.absControl;
	*onePush = prop.onePush;
	*onOff = prop.onOff;
	*autoManualMode = prop.autoManualMode;
	*valueA = prop.valueA;
	*valueB = prop.valueB;
	*absValue = prop.absValue;

	return 0;
}

DLLFUN int SetFlyCapProperty(unsigned int handle, int type, bool present, bool absControl, bool onePush, bool onOff,
							 bool autoManualMode, int valueA, int valueB, float absValue) {
	if(!check_cam_handle(handle)) {
		return -1; //bad handle
	}
	Property prop;
	memset(&prop, 0, sizeof(prop));
	prop.type = PROPERTY_TYPE_INTEGER_MAPPING[type];
	prop.present = present;
	prop.absControl = absControl;
	prop.onePush = onePush;
	prop.onOff = onOff;
	prop.autoManualMode = autoManualMode;
	prop.valueA = valueA;
	prop.valueB = valueB;
	prop.absValue = absValue;

	Error error = cams[handle].SetProperty(&prop);
	if (error != PGRERROR_OK)
	{
		PrintError( error );
		return -2;
	}
	return 0;
}

//the char arrays should have length sk_maxStringLength = 512
DLLFUN int GetFlyCapPropertyInfo(unsigned int handle, int type, bool* present, bool* autoSupported, bool* manualSupported,
							bool* onOffSupported, bool* onePushSupported, bool* absValSupported,
							bool* readOutSupported, unsigned int* min, unsigned int* max, float* absMin,
							float* absMax, char* pUnits, char* pUnitAbbr) {
	if(!check_cam_handle(handle)) {
		return -1; //bad handle
	}
	PropertyInfo info;
	info.type = PROPERTY_TYPE_INTEGER_MAPPING[type];
	Error error = cams[handle].GetPropertyInfo(&info);
	if (error != PGRERROR_OK)
	{
		PrintError( error );
		return -1;
	}
	*present = info.present;
	*autoSupported = info.autoSupported;
	*manualSupported = info.manualSupported;
	*onOffSupported = info.onOffSupported;
	*onePushSupported = info.onePushSupported;
	*absValSupported = info.absValSupported;
	*readOutSupported = info.readOutSupported;
	*min = info.min;
	*max = info.max;
	*absMin = info.absMin;
	*absMax = info.absMax;
	strcpy(pUnits, info.pUnits);
	strcpy(pUnitAbbr, info.pUnitAbbr);
	return 0;
}

DLLFUN int GetFlyCapImage(unsigned int handle, unsigned int* dataLen, int* row, int* col, int* bitsPerPixel) {

	if(!check_cam_handle(handle)) {
		return -1; //bad handle
	}
    Image rawImage; 
    // Retrieve an image
    Error error = cams[handle].RetrieveBuffer( &rawImage );
    if (error != PGRERROR_OK)
    {
        PrintError( error );
        return -2;
    }

	// Create a converted image
    //Image convertedImage;

    // Convert the raw image
    //put another pixel format here to probably get 16bit images
    error = rawImage.Convert( PIXEL_FORMAT_RGB8, &convertedImages[handle] );
    if (error != PGRERROR_OK) //PIXEL_FORMAT_MONO8
    {
        PrintError( error );
        return -3;
    }

	*row = convertedImages[handle].GetRows();
	*col = convertedImages[handle].GetCols();
	//printf("row, col = %d, %d\n", row, col);
	*dataLen = convertedImages[handle].GetDataSize();
	*bitsPerPixel = convertedImages[handle].GetBitsPerPixel();
	return 0;
}

DLLFUN int GetFlyCapData(unsigned int handle, unsigned char* data, unsigned int dataLen) {
	
	unsigned char* imageData = convertedImages[handle].GetData();
	memcpy(data, imageData, dataLen);
	
	return 0;
	//look in ExtendedShutterEx.cpp to make the shutter 3000msec
	
	//NOT WORKING
	/*
	TimeStamp ts;
	ts = rawImage.GetTimeStamp();
	printf("timestamp = %u, %u\n", ts.seconds, ts.microSeconds);
	ImageMetadata imd;
	imd = rawImage.GetMetadata();
	//contains timestamp, shutter, gain, brightness, exposure, lots of good stuff
	printf("metadata ts=%u gain=%u shutter=%u bright=%u exp=%u wb=%u fc=%u sp=%u\n", 
		imd.embeddedTimeStamp, imd.embeddedGain, imd.embeddedShutter, imd.embeddedBrightness,
		imd.embeddedExposure, imd.embeddedWhiteBalance, imd.embeddedFrameCounter, imd.embeddedStrobePattern);
	*/
}

DLLFUN int GetFlyCapFormat7Info(unsigned int handle, int* maxWidth, int* maxHeight, int* offsetHStepSize, int* offsetVStepSize,
								int* imageHStepSize, int* imageVStepSize, int* packetSize, int* minPacketSize,
								int* maxPacketSize) {
	if(!check_cam_handle(handle)) {
		return -1; //bad handle
	}
	Format7Info f7info;
	bool sup;
	f7info.mode = MODE_0; //temporary guess! if this function doesnt work this might be why
	Error error = cams[handle].GetFormat7Info(&f7info, &sup);
    if (error != PGRERROR_OK || !sup)
    {
        PrintError( error );
        return -2;
    }
	*maxWidth = f7info.maxWidth;
	*maxHeight = f7info.maxHeight;
	*offsetHStepSize = f7info.offsetHStepSize;
	*offsetVStepSize = f7info.offsetVStepSize;
	*imageHStepSize = f7info.imageHStepSize;
	*imageVStepSize = f7info.imageVStepSize;
	*packetSize = f7info.packetSize;
	*minPacketSize = f7info.minPacketSize;
	*maxPacketSize = f7info.maxPacketSize;
	/*
	printf("maxWidth=%u maxHeight=%u offsetHStepSize=%u offsetVStepSize=%u imageHStepSize=%u "
		"imageVStepSize=%u pixelFormatBitField=0x%08x vendorPixelFormatBitField=0x%08x "
		"packetSize=%u minPacketSize=%u maxPacketSize=%u percentage=%f\n", f7info.maxWidth,
		f7info.maxHeight, f7info.offsetHStepSize, f7info.offsetVStepSize, f7info.imageHStepSize,
		f7info.imageVStepSize, f7info.pixelFormatBitField, f7info.vendorPixelFormatBitField,
		f7info.packetSize, f7info.minPacketSize, f7info.maxPacketSize, f7info.percentage);
	*/
	return 0;
}

DLLFUN int GetFlyCapFormat7Configuration(unsigned int handle, int* offsetX, int* offsetY,
										int* width, int* height, int* pixelFormat, int* packetSize) {

	if(!check_cam_handle(handle)) {
		return -1; //bad handle
	}
	Format7ImageSettings f7imageSettings; 
	float pSizePercent;
	Error error = cams[handle].GetFormat7Configuration(&f7imageSettings, (unsigned int*)packetSize, &pSizePercent);
	if (error != PGRERROR_OK)
    {
        PrintError( error );
        return -2;
    }
	//printf("offsetX=%d offsetY=%d width=%d height=%d\n", f7imageSettings.offsetX,
	//	f7imageSettings.offsetY, f7imageSettings.width, f7imageSettings.height);
	*offsetX = f7imageSettings.offsetX;
	*offsetY = f7imageSettings.offsetY;
	*width = f7imageSettings.width;
	*height = f7imageSettings.height;
	*pixelFormat = (int)f7imageSettings.pixelFormat;

	return 0;
}

	
DLLFUN int SetFlyCapFormat7Configuration(unsigned int handle, int offsetX, int offsetY, int width, int height, int pixelFormat) {

	if(!check_cam_handle(handle)) {
		return -1; //bad handle
	}
	Format7ImageSettings f7imageSettings;
	f7imageSettings.offsetX = offsetX;
	f7imageSettings.offsetY = offsetY;
	f7imageSettings.width = width;
	f7imageSettings.height = height;
	f7imageSettings.pixelFormat = (PixelFormat)pixelFormat;

	bool settingsValid;
	Format7PacketInfo f7packetInfo;
	Error error = cams[handle].ValidateFormat7Settings(&f7imageSettings, &settingsValid, &f7packetInfo);
    if (error != PGRERROR_OK || !settingsValid)
    {
        PrintError( error );
        return -2;
    }
	//printf("validated=%d recommendedBytesPerPacket=%u maxBytesPerPacket=%u unitBytesPerPacket=%u\n",
	//	settingsValid, f7packetInfo.recommendedBytesPerPacket, f7packetInfo.maxBytesPerPacket,
	//	f7packetInfo.unitBytesPerPacket);


	error = cams[handle].StopCapture();
    if (error != PGRERROR_OK)
    {
        PrintError( error );
        return -3;
    }

	cams[handle].SetFormat7Configuration(&f7imageSettings, f7packetInfo.recommendedBytesPerPacket);

	error = cams[handle].StartCapture();
    if (error != PGRERROR_OK)
    {
        PrintError( error );
        return -4;
    }
	return 0;
}


DLLFUN int CloseFlyCap(unsigned int handle) {
	if(!check_cam_handle(handle)) {
		return -1; //bad handle
	}
    // Stop capturing images
    Error error = cams[handle].StopCapture();
    if (error != PGRERROR_OK)
    {
        PrintError( error );
        return -2;
    }      
	
    // Disconnect the camera
    error = cams[handle].Disconnect();
    if (error != PGRERROR_OK)
    {
        PrintError( error );
        return -3;
    }
    return 0;
}


//all errors sent to stdout
/*
int main(int argc, char** argv)
{
	
	char modelName[512];
	char vendorName[512];
	char sensorInfo[512];
	char sensorResolution[512];
	char firmwareVersion[512];
	char firmwareBuildTime[512];
	int err;
	if((err = SetupFlyCap(12350594, modelName, vendorName, sensorInfo,
			sensorResolution, firmwareVersion, firmwareBuildTime)) != 0)
		return printf("SetupFlyCap(): %d\n", err);

	unsigned int dataLen = 0;
	int row, col, bitsPerPixel;
	unsigned char* data = NULL;

	for(int i = 0; i < 1; i++) {

		int offsetX, offsetY, width, height, pixelFormat, packetSize;
		if((err = GetFlyCapFormat7Configuration(&offsetX, &offsetY, &width, &height, &pixelFormat, &packetSize)) != 0)
			return printf("GetFlyCapFormat7Configuration(): %d\n", err);

		width = 320;
		height = 400;

		if((err = SetFlyCapFormat7Configuration(offsetX, offsetY, width, height, pixelFormat)) != 0)
			return printf("SetFlyCapFormat7Configuration(): %d\n", err);

		
		//12 = shutter, 13 = gain
		bool present, absControl, onePush, onOff, autoManualMode;
		int valueA, valueB;
		float absValue;
		if((err = GetFlyCapProperty(12, &present, &absControl, &onePush,
			&onOff, &autoManualMode, &valueA, &valueB, &absValue)) != 0)
			return printf("GetFlyCapProperty(): %d\n", err);

		printf("present=%d, absControl=%d, onePush=%d, onOff=%d\n"
			"autoManualMode=%d, valueA=%u valueB=%u, absValue=%f\n",
			present, absControl, onePush, onOff,
			autoManualMode, valueA, valueB, absValue);

		absValue = 30.0 + i*5.0;
		if((err = SetFlyCapProperty(12, present, absControl, onePush,
			onOff, autoManualMode, valueA, valueB, absValue)) != 0)
			return printf("SetFlyCapProperty(): %d\n", err);
		

		if((err = GetFlyCapImage(&dataLen, &row, &col, &bitsPerPixel)) != 0)
			return printf("GetFlyCapImage(): %d\n", err);
		if(!data) {
			data = (unsigned char*)malloc(dataLen);
			printf("datalen=%d row=%d col=%d bpp=%d\n", dataLen, row, col, bitsPerPixel);
		}

		if((err = GetFlyCapData(data, dataLen)) != 0)
			return printf("GetFlyCapData(): %d\n", err);

		char filename[256];
		sprintf(filename, "FlyCapture2S-img-%d.ppm", i);
		FILE* fd = fopen(filename, "w");
		fprintf(fd, "P3\n%d %d\n255\n", col, row);
		for(unsigned int i = 0; i < dataLen;)
			for(int j = 0; j < 24; j++)
				fprintf(fd, "%d ", data[i++]);
			fprintf(fd, "\n");
		fclose(fd);

		
		printf("printing out the first 10 pixels\n");
		int bytesPerPixel = bitsPerPixel / 8;
		for(int p = 0; p < 10; p++) {
			printf("pixel[%d] ", p);
			for(int b = 0; b < bytesPerPixel; b++) {
				printf("% 2d,", data[p*bytesPerPixel + b]);
			}
			printf("\n");
		}
		

		Sleep(100);
	}
	CloseFlyCap();

	printf("end\n");
	getchar();
	
    return 0;
}
*/