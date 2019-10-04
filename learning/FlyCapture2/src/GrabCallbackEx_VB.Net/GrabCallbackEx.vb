'=============================================================================
' Copyright © 2011 Point Grey Research, Inc. All Rights Reserved.
'
' This software is the confidential and proprietary information of Point
' Grey Research, Inc. ("Confidential Information").  You shall not
' disclose such Confidential Information and shall use it only in
' accordance with the terms of the license agreement you entered into
' with PGR.
'
' PGR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
' SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
' IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
' PURPOSE, OR NON-INFRINGEMENT. PGR SHALL NOT BE LIABLE FOR ANY DAMAGES
' SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
' THIS SOFTWARE OR ITS DERIVATIVES.
'=============================================================================

Imports System
Imports System.Text
Imports System.IO
Imports System.Threading
Imports FlyCapture2Managed

Namespace GrabCallbackEx_VB
    Class Program

        Shared imageCnt As UInteger = 0

        Shared Sub PrintBuildInfo()

            Dim version As FC2Version = ManagedUtilities.libraryVersion
            Dim newStr As StringBuilder = New StringBuilder()
            newStr.AppendFormat("FlyCapture2 library version: {0}.{1}.{2}.{3}" & vbNewLine, _
                                version.major, version.minor, version.type, version.build)
            Console.WriteLine(newStr)

        End Sub

        Shared Sub PrintCameraInfo(ByVal camInfo As CameraInfo)

            Dim newStr As StringBuilder = New StringBuilder()
            newStr.Append(vbNewLine & "*** CAMERA INFORMATION ***" & vbNewLine)
            newStr.AppendFormat("Serial number - {0}" & vbNewLine, camInfo.serialNumber)
            newStr.AppendFormat("Camera model - {0}" & vbNewLine, camInfo.modelName)
            newStr.AppendFormat("Camera vendor - {0}" & vbNewLine, camInfo.vendorName)
            newStr.AppendFormat("Sensor - {0}" & vbNewLine, camInfo.sensorInfo)
            newStr.AppendFormat("Resolution - {0}" & vbNewLine, camInfo.sensorResolution)

            Console.WriteLine(newStr)

        End Sub

        Sub OnImageGrabbed(ByVal image As ManagedImage)
            Console.WriteLine("Grabbed image {0} - {1}.{2}", _
                imageCnt, _
                image.timeStamp.cycleSeconds, _
                image.timeStamp.cycleCount)
            imageCnt += 1
        End Sub

        Sub RunSingleCamera(ByVal guid As ManagedPGRGuid)

            Dim cam As ManagedCamera = New ManagedCamera()

            ' Connect to a camera
            cam.Connect(guid)

            ' Get the camera information
            Dim camInfo As CameraInfo = cam.GetCameraInfo()

            PrintCameraInfo(camInfo)

            ' Get embedded image info from camera
            Dim embeddedInfo As EmbeddedImageInfo = cam.GetEmbeddedImageInfo()

            ' Enable timestamp collection	
            If (embeddedInfo.timestamp.available) Then
                embeddedInfo.timestamp.onOff = True
            End If

            ' Set embedded image info to camera
            cam.SetEmbeddedImageInfo(embeddedInfo)

            ' Start capturing images
            cam.StartCapture(AddressOf OnImageGrabbed)

            Dim frameRateProp As CameraProperty = cam.GetProperty(PropertyType.FrameRate)

            While (imageCnt < 10)
                Dim millisecondsToSleep As Integer = (1000 / frameRateProp.absValue)
                Thread.Sleep(millisecondsToSleep)
            End While

            ' Stop capturing images
            cam.StopCapture()

            ' Disconnect the camera
            cam.Disconnect()
        End Sub

        Shared Sub Main()

            PrintBuildInfo()

            Dim program As Program = New Program()

            Dim busMgr As ManagedBusManager = New ManagedBusManager()
            Dim numCameras As UInteger = busMgr.GetNumOfCameras()

            Console.WriteLine("Number of cameras detected: {0}", numCameras)

            For i As UInteger = 0 To (numCameras - 1)
                Dim guid As ManagedPGRGuid = busMgr.GetCameraFromIndex(i)
                program.RunSingleCamera(guid)
            Next

            Console.WriteLine("Done! Press any key to exit...")
            Console.ReadKey()
        End Sub

    End Class
End Namespace