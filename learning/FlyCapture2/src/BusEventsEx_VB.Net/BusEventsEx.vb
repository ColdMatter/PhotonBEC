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
Imports System.Collections
Imports FlyCapture2Managed

Namespace BusEventsEx_VB
    Class Program

        Shared Sub PrintBuildInfo()
            Dim version As FC2Version = ManagedUtilities.libraryVersion
            Dim newStr As StringBuilder = New StringBuilder()
            newStr.AppendFormat("FlyCapture2 library version: {0}.{1}.{2}.{3}" & vbNewLine, _
                                version.major, version.minor, version.type, version.build)
            Console.WriteLine(newStr)
        End Sub

        Sub OnBusReset(ByVal ptr As IntPtr, ByVal serialNumber As UInteger)
            Console.WriteLine("{0} - *** BUS RESET ***", DateTime.Now.ToString())
        End Sub

        Sub OnBusArrival(ByVal ptr As IntPtr, ByVal serialNumber As UInteger)
            Console.WriteLine("{0} - *** BUS ARRIVAL ({1})***", DateTime.Now.ToString(), serialNumber)
        End Sub

        Sub OnBusRemoval(ByVal ptr As IntPtr, ByVal serialNumber As UInteger)
            Console.WriteLine("{0} - *** BUS REMOVAL ({1})***", DateTime.Now.ToString(), serialNumber)
        End Sub

        Sub BusResetLoop()

            Dim busMgr As ManagedBusManager = New ManagedBusManager()
            Dim callbackHandles As List(Of IntPtr) = New List(Of IntPtr)()

            ' Register bus events
            Dim busResetHandle As IntPtr = busMgr.RegisterCallback(AddressOf OnBusReset, ManagedCallbackType.BusReset, IntPtr.Zero)
            Dim busArrivalHandle As IntPtr = busMgr.RegisterCallback(AddressOf OnBusArrival, ManagedCallbackType.Arrival, IntPtr.Zero)
            Dim busRemovalHandle As IntPtr = busMgr.RegisterCallback(AddressOf OnBusRemoval, ManagedCallbackType.Removal, IntPtr.Zero)

            callbackHandles.Add(busResetHandle)
            callbackHandles.Add(busArrivalHandle)
            callbackHandles.Add(busRemovalHandle)

            ' Prevent exit if CTL+C is pressed.
            Console.TreatControlCAsInput = True

            Console.WriteLine("Press any key to exit..." & vbNewLine)
            Dim cki As ConsoleKeyInfo = Console.ReadKey()

            ' Unregister bus events
            For Each currHandle As IntPtr In callbackHandles
                busMgr.UnregisterCallback(currHandle)
            Next
        End Sub

        Shared Sub Main()
            PrintBuildInfo()

            Dim program As Program = New Program()
            program.BusResetLoop()

            Console.WriteLine("Done! Press any key to exit...")
            Console.ReadKey()
        End Sub

    End Class
End Namespace