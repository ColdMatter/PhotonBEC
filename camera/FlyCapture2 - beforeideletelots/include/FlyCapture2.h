//=============================================================================
// Copyright © 2008 Point Grey Research, Inc. All Rights Reserved.
//
// This software is the confidential and proprietary information of Point
// Grey Research, Inc. ("Confidential Information").  You shall not
// disclose such Confidential Information and shall use it only in
// accordance with the terms of the license agreement you entered into
// with Point Grey Research, Inc. (PGR).
//
// PGR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
// SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
// PURPOSE, OR NON-INFRINGEMENT. PGR SHALL NOT BE LIABLE FOR ANY DAMAGES
// SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
// THIS SOFTWARE OR ITS DERIVATIVES.
//=============================================================================

//=============================================================================
// $Id: FlyCapture2.h 148656 2012-08-30 17:35:28Z rang $
//=============================================================================

#ifndef PGR_FC2_FLYCAPTURE2_H
#define PGR_FC2_FLYCAPTURE2_H

//=============================================================================
// Global header file for FlyCapture2. 
//
// By including this file, all required header files for full FlyCapture2 
// operation will be included automatically. It is recommended that this file 
// be used instead of manually including individual header files.
//=============================================================================

//=============================================================================
// Platform-specific definitions
//=============================================================================
#include "FlyCapture2Platform.h"

//=============================================================================
// Global definitions
//=============================================================================
#include "FlyCapture2Defs.h"

//=============================================================================
// PGR Error class
//=============================================================================
#include "Error.h"

//=============================================================================
// FlyCapture2 classes
//=============================================================================
#include "BusManager.h"
#include "Camera.h"
#include "GigECamera.h"
#ifdef GENICAM
#if _MSC_VER >= 1600
#include "GCCamera.h"
#endif
#endif
#include "Image.h"

//=============================================================================
// Utility classes
//=============================================================================
#include "Utilities.h"
#include "AVIRecorder.h"
#include "TopologyNode.h"
#include "ImageStatistics.h"

#endif // PGR_FC2_FLYCAPTURE2_H

