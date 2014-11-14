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
// $Id:
//=============================================================================

using System;
using System.Collections.Generic;
using System.Text;

using FlyCapture2Managed;

namespace MultipleCameraEx_CSharp
{
    class Program
    {
        static void PrintBuildInfo()
        {
            FC2Version version = ManagedUtilities.libraryVersion;

            StringBuilder newStr = new StringBuilder();
            newStr.AppendFormat(
                "FlyCapture2 library version: {0}.{1}.{2}.{3}\n",
                version.major, version.minor, version.type, version.build);

            Console.WriteLine(newStr);
        }

        static void PrintCameraInfo(CameraInfo camInfo)
        {
            StringBuilder newStr = new StringBuilder();
            newStr.Append("\n*** CAMERA INFORMATION ***\n");
            newStr.AppendFormat("Serial number - {0}\n", camInfo.serialNumber);
            newStr.AppendFormat("Camera model - {0}\n", camInfo.modelName);
            newStr.AppendFormat("Camera vendor - {0}\n", camInfo.vendorName);
            newStr.AppendFormat("Sensor - {0}\n", camInfo.sensorInfo);
            newStr.AppendFormat("Resolution - {0}\n", camInfo.sensorResolution);

            Console.WriteLine(newStr);
        }

        void RunAllCameras(ManagedBusManager busMgr, uint numOfCameras)
        {
            const int k_numImages = 10;

            ManagedCamera[] cameras = new ManagedCamera[numOfCameras];

            // Connect to all detected cameras and attempt to set them to
            // a common video mode and frame rate
            for (uint i = 0; i < numOfCameras; i++)
            {
                cameras[i] = new ManagedCamera();

                ManagedPGRGuid guid = busMgr.GetCameraFromIndex(i);

                // Connect to a camera
                cameras[i].Connect(guid);

                // Get the camera information
                CameraInfo camInfo = cameras[i].GetCameraInfo();
                PrintCameraInfo(camInfo);

                // Set all cameras to a specific mode and frame rate so they
                // can be synchronized
                cameras[i].SetVideoModeAndFrameRate(VideoMode.VideoMode640x480Y8, FrameRate.FrameRate15);
            }

            // Put StartSyncCapture in a try-catch block in case
            // cameras failed to synchronize
            try
            {
                ManagedCamera.StartSyncCapture(numOfCameras, cameras);
            }
            catch (System.Exception ex)
            {
                Console.WriteLine("Error starting cameras.");
                Console.WriteLine("This example requires cameras to be able to set to 640x480 Y8 at 15fps.");
                Console.WriteLine("If your camera does not support this mode, please edit the source code and recompile the application.");
                Console.WriteLine("Press any key to exit.");
                Console.ReadKey();
                return;
            }

            ManagedImage tempImage = new ManagedImage();

            // Retrieve images from attached cameras
            for (int imageCnt = 0; imageCnt < k_numImages; imageCnt++)
            {
                for (int camCount = 0; camCount < numOfCameras; camCount++)
                {
                    // Retrieve an image
                    cameras[camCount].RetrieveBuffer(tempImage);

                    // Display the timestamps for all cameras to show that the
                    // captured image is synchronized for each camera
                    TimeStamp timeStamp = tempImage.timeStamp;
                    Console.Out.WriteLine("Cam {0} - Frame {1} - TimeStamp {2} {3}", camCount, imageCnt, timeStamp.cycleSeconds, timeStamp.cycleCount);
                }
            }

            for (uint i = 0; i < numOfCameras; i++)
            {
                // Stop capturing images
                cameras[i].StopCapture();
                // Disconnect the camera
                cameras[i].Disconnect();
            }
        }

        static void Main(string[] args)
        {
            PrintBuildInfo();

            Program program = new Program();

            // Create bus manager and find number of attached cameras
            ManagedBusManager busMgr = new ManagedBusManager();
            uint numCameras = busMgr.GetNumOfCameras();

            Console.WriteLine("Number of cameras detected: {0}", numCameras);

            if (numCameras < 1)
            {
                Console.WriteLine("Insufficient number of cameras... press any key to exit.");
                Console.ReadKey();
                return;
            }

            program.RunAllCameras(busMgr, numCameras);

            Console.WriteLine("Done! Press any key to exit...");
            Console.ReadKey();
        }
    }
}
