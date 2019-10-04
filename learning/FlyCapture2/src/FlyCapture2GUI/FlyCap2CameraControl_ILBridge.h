//=============================================================================
// Copyright © 2010 Point Grey Research, Inc. All Rights Reserved.
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

#pragma once
#pragma managed
#include <vcclr.h>


#ifdef _DEBUG
#ifdef _WIN64
#pragma message("Using ILBridge_CameraControlDialog - x64|Debug")
#if (_MSC_VER == 1600)  
#using <..\\..\\bin64\\FlyCap2CameraControld_v100.dll>
#using <..\\..\\bin64\\FlyCapture2Managedd_v100.dll>
#elif (_MSC_VER == 1500)
#using <..\\..\\bin64\\FlyCap2CameraControld_v90.dll>
#using <..\\..\\bin64\\FlyCapture2Managedd_v90.dll>
#else					
#using <..\\..\\bin64\\FlyCap2CameraControld.dll>
#using <..\\..\\bin64\\FlyCapture2Managedd.dll>
#endif 
#else					
#pragma message("Using ILBridge_CameraControlDialog - x86|Debug")
#if (_MSC_VER == 1600)	
#using <..\\..\\bin\\FlyCap2CameraControld_v100.dll>
#using <..\\..\\bin\\FlyCapture2Managedd_v100.dll>
#elif (_MSC_VER == 1500)
#using <..\\..\\bin\\FlyCap2CameraControld_v90.dll>
#using <..\\..\\bin\\FlyCapture2Managedd_v90.dll>
#else					
#using <..\\..\\bin\\FlyCap2CameraControld.dll>
#using <..\\..\\bin\\FlyCapture2Managedd.dll>
#endif 
#endif 
#else					
#ifdef _WIN64
#pragma message("Using ILBridge_CameraControlDialog - x64|Release")
#if (_MSC_VER == 1600)
#using <..\\..\\bin64\\FlyCap2CameraControl_v100.dll>
#using <..\\..\\bin64\\FlyCapture2Managed_v100.dll>
#elif (_MSC_VER == 1500)
#using <..\\..\\bin64\\FlyCap2CameraControl_v90.dll>
#using <..\\..\\bin64\\FlyCapture2Managed_v90.dll>
#else
#using <..\\..\\bin64\\FlyCap2CameraControl.dll>
#using <..\\..\\bin64\\FlyCapture2Managed.dll>
#endif 
#else
#pragma message("Using ILBridge_CameraControlDialog - x86|Release")
#if (_MSC_VER == 1600)
#using <..\\..\\bin\\FlyCap2CameraControl_v100.dll>
#using <..\\..\\bin\\FlyCapture2Managed_v100.dll>
#elif (_MSC_VER == 1500)
#using <..\\..\\bin\\FlyCap2CameraControl_v90.dll>
#using <..\\..\\bin\\FlyCapture2Managed_v90.dll>
#else
#using <..\\..\\bin\\FlyCap2CameraControl.dll>
#using <..\\..\\bin\\FlyCapture2Managed.dll>
#endif
#endif
#endif // _DEBUG

namespace FlyCapture2
{
    class CameraBase;
}

namespace FlyCapture2_ILBridge
{
	class ILBridge_CameraControlDialog 
	{	
	public:
		ILBridge_CameraControlDialog();
        ~ILBridge_CameraControlDialog() {}

		void Connect(FlyCapture2::CameraBase* pCamera);
		void Disconnect();
		void Hide();
		void Show();
        void Show(void* pParent);
		void ShowModal();
        void ShowModal(void* pParent);
		bool IsVisible();
		void SetTitle(const wchar_t* title);

    private:
        gcroot<FlyCapture2Managed::Gui::CameraControlDialog^> m_pCamCtrlDialog;
	};
}