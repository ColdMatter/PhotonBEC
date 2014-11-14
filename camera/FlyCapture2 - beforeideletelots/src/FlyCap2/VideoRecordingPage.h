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

#pragma once
#include "afxwin.h"
#include "afxcmn.h"

using namespace FlyCapture2;

// VideoRecordingPage dialog
class VideoRecordingPage : public CDialog
{
	DECLARE_DYNAMIC(VideoRecordingPage)

public:

	enum VideoFormatTypes
	{
		UNCOMPRESSED,
		MJPEG,
		H264,
		NUM_VIDEO_FORMATS
	};

	struct VideoSettings
	{
		char filename[MAX_PATH];
		VideoFormatTypes videoFormat;
		AVIOption aviOption;
		MJPGOption mjpgOption;
		H264Option h264Option;
		char fileExtension[MAX_PATH];
	};

	VideoRecordingPage(CWnd* pParent = NULL);   // standard constructor
	virtual ~VideoRecordingPage();

	virtual BOOL OnInitDialog();

	void GetSettings( VideoSettings* videoSettings );
	void ValidateSettings( CString* errorList );
	void EnableControls(BOOL enable);
	void StoreCameraPtr( CameraBase* m_pCamera );

// Dialog Data
	enum { IDD = IDD_TABPAGE_VIDEO_RECORD };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	
	DECLARE_MESSAGE_MAP()
	afx_msg void OnCbnSelchangeComboVideoRecordType();
	afx_msg void OnBnClickedBtnSetFrameRate();
	afx_msg void OnBnClickedOk();
	afx_msg void OnBnClickedCancel();

	BOOL GetCurrentCameraResolution( unsigned int* width, unsigned int* height );
	BOOL GetBitrate(unsigned int* bitrate);
	void GetFilePath( char* filename );
	BOOL GetQuality( unsigned int* quality );
	BOOL GetFramerate( float* framerate );

	void DisplayMJPEGOptions(BOOL display);
	void DisplayH264Options(BOOL display);

	BOOL ConvertToInt(CString* text, unsigned int* integer );
	
protected:
	CComboBox m_combo_VideoFormat;
	
	CEdit m_edit_frameRate;
	CButton m_btn_setFrameRate;

	CEdit m_edit_h264Bitrate;
	CSpinButtonCtrl m_spin_h264Bitrate;
	CStatic m_group_h264Options;
	CStatic m_static_h264Bitrate;

	CEdit m_edit_mjpegCompressionLevel;
	CSpinButtonCtrl m_spin_mjpegCompressionLevel;
	CStatic m_group_mjpegOptions;
	CStatic m_static_mjpegCompressionLevel;

	CameraBase* m_pCameraVid;

	static const unsigned int  MJPEG_QUALITY_MIN = 1;
	static const unsigned int MJPEG_QUALITY_MAX = 100;
	static const CString MJPEG_QUALITY_DEF;

	static const unsigned int H264_BITRATE_MIN = 1000;
	static const unsigned int H264_BITRATE_MAX = 1000000000;
	static const CString H264_BITRATE_DEF;

	static const float VIDEO_FRAMERATE_MAX;
	static const float VIDEO_FRAMERATE_MIN;
	static const CString VIDEO_FRAMERATE_DEF;
};
