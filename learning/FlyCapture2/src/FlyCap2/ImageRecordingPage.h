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
#include <bitset>

using namespace FlyCapture2;

// ImageRecordingPage dialog
class ImageRecordingPage : public CDialog
{
	DECLARE_DYNAMIC(ImageRecordingPage)

public:

	enum ImageFormatTypes
	{
		PGM,
		PPM,
		BMP,
		JPEG,
		JPEG2000,
		TIFF,
		PNG,
		RAW,
		NUM_IMAGE_FORMATS
	};

	struct ImageSettings
	{
		char filename[MAX_PATH];
		ImageFormatTypes imageFormat;
		PGMOption pgmOption;
		PPMOption ppmOption;
		JPEGOption jpgOption;
		JPG2Option jpg2Option;
		TIFFOption tiffOption;
		PNGOption pngOption;
		BMPOption bmpOption;
		char fileExtension[MAX_PATH];
	};

	ImageRecordingPage(CWnd* pParent = NULL);   // standard constructor
	virtual ~ImageRecordingPage();

	virtual BOOL OnInitDialog();
	void GetSettings( ImageSettings* imageSettings );
	void ValidateSettings( CString* errorList );
	void EnableControls(BOOL enable);
	void BuildSupportedOutputFormats(PixelFormat pixelFormat);

// Dialog Data
	enum { IDD = IDD_TABPAGE_IMAGE_RECORD };

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

	DECLARE_MESSAGE_MAP()
	afx_msg void OnCbnSelchangeComboImageRecordType();
	afx_msg void OnBnClickedOk();
	afx_msg void OnBnClickedCancel();

	void GetFilePath( char* filename );
	BOOL GetPxMBinaryFile( BOOL* binaryFile );
	BOOL GetJPEGQuality( unsigned int* quality );
	BOOL GetTIFFCompression( TIFFOption::CompressionMethod* compression );
	BOOL GetPNGInterlaced( BOOL* interlaced );
	BOOL GetPNGCompression( unsigned int* compression );
	BOOL GetJPEGProgressive( BOOL* progressive );
	BOOL GetJPEG2KQuality( unsigned int* quality );
	BOOL GetBMP8bitIndexedColor(BOOL* indexedColor);

	void DisplayTIFFOptions(BOOL display);
	void DisplayPNGOptions(BOOL display);
	void DisplayJPEGOptions(BOOL display);
	void DisplayJPG2kOptions(BOOL display);
	void DisplayPxMOptions(BOOL display);
	void DisplayBMPOptions(BOOL display);

	BOOL ConvertToInt(CString* text, unsigned int* integer );

	unsigned int GetValidImageFormatSelection();

protected:

	unsigned int GetBppFromPixelFormat( PixelFormat pixelFormat );
	CComboBox m_combo_ImageFormat;
	
	CComboBox m_combo_TiffCompressionMethod;
	CStatic m_grp_tiffOptions;
	CStatic m_static_tiffCompressionMethod;
	
	CStatic m_grp_pngOptions;
	CButton m_chk_pngInterleaved;
	CStatic m_static_pngCompressionLevel;
	CComboBox m_combo_pngCompressionLevel;
	
	CStatic m_grp_jpegOptions;
	CButton m_chk_jpegProgressive;
	CStatic m_static_jpegCompression;
	CEdit m_edit_jpegCompression;
	CSpinButtonCtrl m_spin_jpegCompression;

	CStatic m_grp_pxmOptions;
	CButton m_chk_pxmSaveAsBinary;
	
	CStatic m_grp_jpeg2kOptions;
	CStatic m_static_jpeg2kCompressionLevel;
	CEdit m_edit_jpg2kCompressionLevel;
	CSpinButtonCtrl m_spin_jpeg2kCompressionLevel;

	std::bitset<NUM_IMAGE_FORMATS> m_validFormats;

	PixelFormat m_currPixelFormat;
public:
	CStatic m_grp_bmpOptions;
	CButton m_chk_8bitColorIndexed;
};