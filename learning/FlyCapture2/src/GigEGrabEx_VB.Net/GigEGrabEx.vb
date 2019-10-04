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
'=============================================================================\

Imports System
Imports System.Text
Imports System.Drawing
Imports System.IO
Imports FlyCapture2Managed

Namespace GigEGrabEx_VB
    Class Program

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
            newStr.AppendFormat("Firmware version - {0}" & vbNewLine, camInfo.firmwareVersion)
            newStr.AppendFormat("Firmware build time - {0}" & vbNewLine, camInfo.firmwareBuildTime)
            newStr.AppendFormat("GigE version - {0}.{1}" & vbNewLine, camInfo.gigEMajorVersion, camInfo.gigEMinorVersion)
            newStr.AppendFormat("User defined name - {0}" & vbNewLine, camInfo.userDefinedName)
            newStr.AppendFormat("XML URL 1 - {0}" & vbNewLine, camInfo.xmlURL1)
            newStr.AppendFormat("XML URL 2 - {0}" & vbNewLine, camInfo.xmlURL2)
            newStr.AppendFormat("MAC address - {0}" & vbNewLine, camInfo.macAddress.ToString())
            newStr.AppendFormat("IP address - {0}" & vbNewLine, camInfo.ipAddress.ToString())
            newStr.AppendFormat("Subnet mask - {0}" & vbNewLine, camInfo.subnetMask.ToString())
            newStr.AppendFormat("Default gateway - {0}" & vbNewLine, camInfo.defaultGateway.ToString())

            Console.WriteLine(newStr)

        End Sub

        Shared Sub PrintStreamChannelInfo(ByVal streamChannelInfo As GigEStreamChannel)

            Dim newStr As StringBuilder = New StringBuilder()
            newStr.Append(vbNewLine & "*** STREAM CHANNEL INFORMATION ***" & vbNewLine)
            newStr.AppendFormat("Network interface - {0}" & vbNewLine, streamChannelInfo.networkInterfaceIndex)
            newStr.AppendFormat("Host post - {0}" & vbNewLine, streamChannelInfo.hostPost)
            newStr.AppendFormat("Do not fragment bit - {0}" & vbNewLine, IIf(streamChannelInfo.doNotFragment, "Enabled", "Disabled"))
            newStr.AppendFormat("Packet size - {0}" & vbNewLine, streamChannelInfo.packetSize)
            newStr.AppendFormat("Inter packet delay - {0}" & vbNewLine, streamChannelInfo.interPacketDelay)
            newStr.AppendFormat("Destination IP address - {0}" & vbNewLine, streamChannelInfo.destinationIpAddress)
            newStr.AppendFormat("Source port (on camera) - {0}" & vbNewLine & vbNewLine, streamChannelInfo.sourcePort)

            Console.WriteLine(newStr)
        End Sub

        Sub RunSingleCamera(ByVal guid As ManagedPGRGuid)

            Const k_numImages As Integer = 10

            Dim cam As ManagedGigECamera = New ManagedGigECamera()

            ' Connect to a camera
            cam.Connect(guid)

            ' Get the camera information
            Dim camInfo As CameraInfo = cam.GetCameraInfo()
            PrintCameraInfo(camInfo)

            Dim numStreamChannels As UInteger = cam.GetNumStreamChannels()
            For i As UInteger = 0 To (numStreamChannels - 1)
                PrintStreamChannelInfo(cam.GetGigEStreamChannelInfo(i))
            Next

            Dim imageSettingsInfo As GigEImageSettingsInfo = cam.GetGigEImageSettingsInfo()

            Dim imageSettings As GigEImageSettings = New GigEImageSettings()
            imageSettings.offsetX = 0
            imageSettings.offsetY = 0
            imageSettings.height = imageSettingsInfo.maxHeight
            imageSettings.width = imageSettingsInfo.maxWidth
            imageSettings.pixelFormat = PixelFormat.PixelFormatMono8

            cam.SetGigEImageSettings(imageSettings)

            ' Get embedded image info from camera
            Dim embeddedInfo As EmbeddedImageInfo = cam.GetEmbeddedImageInfo()

            ' Enable timestamp collection	
            If (embeddedInfo.timestamp.available) Then
                embeddedInfo.timestamp.onOff = True
            End If

            ' Set embedded image info to camera
            cam.SetEmbeddedImageInfo(embeddedInfo)

            ' Start capturing images
            cam.StartCapture()

            Dim rawImage As ManagedImage = New ManagedImage()
            For imageCnt As Integer = 0 To (k_numImages - 1)

                ' Retrieve an image
                cam.RetrieveBuffer(rawImage)

                ' Get the timestamp
                Dim timeStamp As TimeStamp = rawImage.timeStamp

                Console.WriteLine( _
                   "Grabbed image {0} - {1} {2} {3}", _
                   imageCnt, _
                   timeStamp.cycleSeconds, _
                   timeStamp.cycleCount, _
                   timeStamp.cycleOffset)

                ' Create a converted image
                Dim convertedImage As ManagedImage = New ManagedImage()

                ' Convert the raw image
                rawImage.Convert(PixelFormat.PixelFormatBgr, convertedImage)

                ' Create a unique filename
                Dim filename As String = String.Format( _
                   "GigEGrabEx_CSharp-{0}-{1}.bmp", _
                   camInfo.serialNumber, _
                   imageCnt)

                ' Get the Bitmap object. Bitmaps are only valid if the
                ' pixel format of the ManagedImage is RGB or RGBU.
                Dim bitmap As Bitmap = convertedImage.bitmap

                ' Save the image
                bitmap.Save(filename)
            Next

            ' Stop capturing images
            cam.StopCapture()

            ' Disconnect the camera
            cam.Disconnect()
        End Sub

        Shared Sub Main()
            PrintBuildInfo()

            Dim program As Program = New Program()

            ' Since this application saves images in the current folder
            ' we must ensure that we have permission to write to this folder.
            ' If we do not have permission, fail right away.
            Dim fileStream As FileStream

            Try
                fileStream = New FileStream("test.txt", FileMode.Create)
                fileStream.Close()
                File.Delete("test.txt")
            Catch ex As Exception
                Console.WriteLine("Failed to create file in current folder.  Please check permissions." & vbNewLine)
                Return
            End Try

            Dim busMgr As ManagedBusManager = New ManagedBusManager()

            Dim camInfos As CameraInfo() = ManagedBusManager.DiscoverGigECameras()
            Console.WriteLine("Number of cameras discovered: {0}", camInfos.Length)
            For Each camInfo As CameraInfo In camInfos
                PrintCameraInfo(camInfo)
            Next

            Dim numCameras As UInteger = busMgr.GetNumOfCameras()
            Console.WriteLine("Number of cameras enumerated: {0}", numCameras)

            For i As UInteger = 0 To (numCameras - 1)
                Dim guid As ManagedPGRGuid = busMgr.GetCameraFromIndex(i)
                If (busMgr.GetInterfaceTypeFromGuid(guid) <> InterfaceType.GigE) Then
                    Continue For
                End If

                Try
                    program.RunSingleCamera(guid)
                Catch ex As FC2Exception

                    Console.WriteLine( _
                        String.Format( _
                        "Error running camera {0}. Error: {1}", _
                        i, ex.Message))
                End Try
            Next

            Console.WriteLine("Done! Press any key to exit...")
            Console.ReadKey()
        End Sub

    End Class
End Namespace
