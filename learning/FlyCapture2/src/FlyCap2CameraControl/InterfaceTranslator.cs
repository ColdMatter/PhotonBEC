//=============================================================================
// Copyright © 2011 Point Grey Research, Inc. All Rights Reserved.
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

using System;
using System.Collections.Generic;
using System.Text;

using FlyCapture2Managed;

namespace FlyCap2CameraControl
{
    internal class InterfaceTranslator
    {
        public static string GetInterfaceString(InterfaceType interfaceType)
        {
            switch (interfaceType)
            {
                case InterfaceType.Ieee1394: return "IEEE-1394";
                case InterfaceType.Usb2: return "USB 2.0";
                case InterfaceType.Usb3: return "USB 3.0";
                case InterfaceType.GigE: return "GigE";
                default: return "Unknown interface";
            }
        }
    }
}
