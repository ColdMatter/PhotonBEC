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

#include "stdafx.h"
#include "FlyCap2_MFC.h"
#include "ImageRecordingPage.h"

const unsigned int MAX_COMBO_STRING = 64;

const char ImageFormatList[][MAX_COMBO_STRING] =
{
	"PGM",
	"PPM",
	"BMP",
	"JPEG",
	"JPEG2000",
	"TIFF",
	"PNG",
	"RAW"
};

const char TIFFCompressionList[][MAX_COMBO_STRING] =
{
	"None",
	"Packbits",
	"Deflate",
	"Adobe Deflate", 
	"CCITTFAX3",
	"CCITTFAX4",
	"LZW",
	"JPEG"
};

// ImageRecordingPage dialog

IMPLEMENT_DYNAMIC(ImageRecordingPage, CDialog)

ImageRecordingPage::ImageRecordingPage(CWnd* pParent /*=NULL*/)
	: CDialog(ImageRecordingPage::IDD, pParent)
{

}

ImageRecordingPage::~ImageRecordingPage()
{
}

void ImageRecordingPage::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_COMBO_IMAGE_RECORD_TYPE, m_combo_ImageFormat);
	DDX_Control(pDX, IDC_COMBO_TIFF_COMPRESSION_METHOD, m_combo_TiffCompressionMethod);
	DDX_Control(pDX, IDC_GROUP_TIFF_OPTIONS, m_grp_tiffOptions);
	DDX_Control(pDX, IDC_STATIC_TIFF_COMPRESSION, m_static_tiffCompressionMethod);
	DDX_Control(pDX, IDC_GROUP_PNG_OPTIONS, m_grp_pngOptions);
	DDX_Control(pDX, IDC_CHECK_PNG_INTERLEAVED, m_chk_pngInterleaved);
	DDX_Control(pDX, IDC_STATIC_PNG_COMPRESSION, m_static_pngCompressionLevel);
	DDX_Control(pDX, IDC_COMBO_PNG_COMPRESSION_LEVEL, m_combo_pngCompressionLevel);
	DDX_Control(pDX, IDC_GROUP_JPEG_OPTIONS, m_grp_jpegOptions);
	DDX_Control(pDX, IDC_CHECK_JPEG_SAVE_PROGRESSIVE, m_chk_jpegProgressive);
	DDX_Control(pDX, IDC_STATIC_JPEG_COMPRESSION, m_static_jpegCompression);
	DDX_Control(pDX, IDC_EDIT_JPEG_COMPRESSION, m_edit_jpegCompression);
	DDX_Control(pDX, IDC_SPIN_JPEG_COMPRESSION, m_spin_jpegCompression);
	DDX_Control(pDX, IDC_GROUP_PGM_PPM_OPTIONS, m_grp_pxmOptions);
	DDX_Control(pDX, IDC_CHECK_PXM_SAVE_AS_BINARY, m_chk_pxmSaveAsBinary);
	DDX_Control(pDX, IDC_GRP_JPEG2K_OPTIONS, m_grp_jpeg2kOptions);
	DDX_Control(pDX, IDC_STATIC_JPEG2K_COMPRESSION_LEVEL, m_static_jpeg2kCompressionLevel);
	DDX_Control(pDX, IDC_EDIT_JPEG2K_COMPRESSION_LEVEL, m_edit_jpg2kCompressionLevel);
	DDX_Control(pDX, IDC_SPIN_JPEG2K_COMPRESSION_LEVEL, m_spin_jpeg2kCompressionLevel);
	DDX_Control(pDX, IDC_GROUP_BMP_OPTIONS, m_grp_bmpOptions);
	DDX_Control(pDX, IDC_CHECK_BMP_8BIT_INDEXED_COLOR, m_chk_8bitColorIndexed);
}

BEGIN_MESSAGE_MAP(ImageRecordingPage, CDialog)
	ON_CBN_SELCHANGE(IDC_COMBO_IMAGE_RECORD_TYPE, &ImageRecordingPage::OnCbnSelchangeComboImageRecordType)
	ON_BN_CLICKED(IDOK, &ImageRecordingPage::OnBnClickedOk)
    ON_BN_CLICKED(IDCANCEL, &ImageRecordingPage::OnBnClickedCancel)
END_MESSAGE_MAP()

// ImageRecordingPage message handlers
BOOL ImageRecordingPage::OnInitDialog()
{
	CDialog::OnInitDialog();

	for (int i = 0; i < NUM_IMAGE_FORMATS; i++)
	{
		m_combo_ImageFormat.AddString(ImageFormatList[i]);
	}
	m_combo_ImageFormat.SetCurSel(PGM);
	m_validFormats.set();
	OnCbnSelchangeComboImageRecordType();

	// TIFF Controls
	for (int i = 0; i < TIFFOption::JPEG; i++)
	{
		m_combo_TiffCompressionMethod.AddString(TIFFCompressionList[i]);
	}
	m_combo_TiffCompressionMethod.SetCurSel(0);
		
	// JPEG Controls
	m_chk_jpegProgressive.SetCheck(FALSE);
	m_edit_jpegCompression.SetWindowText("75");
	m_spin_jpegCompression.SetRange(1, 100);
	m_spin_jpegCompression.SetBuddy(GetDlgItem(IDC_EDIT_JPEG_COMPRESSION));

	// JPEG2000 Controls
	m_edit_jpg2kCompressionLevel.SetWindowText("16");
	m_spin_jpeg2kCompressionLevel.SetRange(1, 512);
	m_spin_jpeg2kCompressionLevel.SetBuddy(GetDlgItem(IDC_EDIT_JPEG2K_COMPRESSION_LEVEL));

	// PNG Controls
	char temp[MAX_COMBO_STRING];
	for (int i = 0; i < 10; i++)
	{
		sprintf(temp, "%d", i);
		m_combo_pngCompressionLevel.AddString(temp);		
	}
	m_combo_pngCompressionLevel.SetCurSel(6);
	m_chk_pngInterleaved.SetCheck(FALSE);
	
	// PxM Controls
	m_chk_pxmSaveAsBinary.SetCheck(FALSE);

	return TRUE;
}

void ImageRecordingPage::GetSettings( ImageSettings* imageSettings )
{
	void* formatSettings = NULL;

	BOOL binaryFile;
	unsigned int quality;
	BOOL progressive;
	TIFFOption::CompressionMethod compressionMethod;
	BOOL interlaced;
	unsigned int compression;
	BOOL indexedColor;

	switch (GetValidImageFormatSelection())
	{
	case PGM:
		imageSettings->imageFormat = PGM;
		strcpy(imageSettings->fileExtension, "pgm");

		GetPxMBinaryFile(&binaryFile);
		imageSettings->pgmOption.binaryFile = (binaryFile != 0);
		break;
	case PPM:
		imageSettings->imageFormat = PPM;
		strcpy(imageSettings->fileExtension, "ppm");


		GetPxMBinaryFile(&binaryFile);
		imageSettings->ppmOption.binaryFile = (binaryFile != 0);
		
		break;
	case BMP:
		imageSettings->imageFormat = BMP;
		strcpy(imageSettings->fileExtension, "bmp");

		GetBMP8bitIndexedColor(&indexedColor);
		imageSettings->bmpOption.indexedColor_8bit = (indexedColor != 0);
		break;

	case JPEG:
		imageSettings->imageFormat = JPEG;
		strcpy(imageSettings->fileExtension, "jpg");

		GetJPEGQuality(&quality);
		GetJPEGProgressive(&progressive);
		imageSettings->jpgOption.quality = quality;
		imageSettings->jpgOption.progressive = (progressive != 0);
		break;
	case JPEG2000:
		imageSettings->imageFormat = JPEG2000;
		strcpy(imageSettings->fileExtension, "jpg");

		GetJPEG2KQuality(&quality);
		imageSettings->jpg2Option.quality = quality;
		break;
	case TIFF:
		imageSettings->imageFormat = TIFF;
		strcpy(imageSettings->fileExtension, "tif");

		GetTIFFCompression(&compressionMethod);
		imageSettings->tiffOption.compression = (TIFFOption::CompressionMethod)compressionMethod;
		break;
	case PNG:
		imageSettings->imageFormat = PNG;
		strcpy(imageSettings->fileExtension, "png");

		GetPNGInterlaced(&interlaced);
		GetPNGCompression(&compression);
		imageSettings->pngOption.compressionLevel = compression;
		imageSettings->pngOption.interlaced = (interlaced != 0);
		break;
	case RAW:
		imageSettings->imageFormat = RAW;
		strcpy(imageSettings->fileExtension, "raw");
		break;
	default:
		imageSettings->imageFormat = RAW;
		strcpy(imageSettings->fileExtension, "raw");
		break;
	}
}

BOOL ImageRecordingPage::ConvertToInt(CString* text, unsigned int* integer )
{
	errno = 0;
	*integer = _ttoi(text->GetBuffer());
	return ((errno == 0) || (*integer != 0));
}

BOOL ImageRecordingPage::GetPxMBinaryFile( BOOL* binaryFile )
{
	*binaryFile = m_chk_pxmSaveAsBinary.GetCheck();
	return TRUE;
}

BOOL ImageRecordingPage::GetBMP8bitIndexedColor( BOOL* indexedColor )
{
	*indexedColor = m_chk_8bitColorIndexed.GetCheck();
	return TRUE;
}

BOOL ImageRecordingPage::GetTIFFCompression( TIFFOption::CompressionMethod* compression )
{
	*compression = (TIFFOption::CompressionMethod)(m_combo_TiffCompressionMethod.GetCurSel()+1);
	return TRUE;
}

BOOL ImageRecordingPage::GetPNGInterlaced( BOOL* interlaced )
{
	*interlaced = m_chk_pngInterleaved.GetCheck();
	return TRUE;
}

BOOL ImageRecordingPage::GetPNGCompression( unsigned int* compression )
{
	*compression = m_combo_pngCompressionLevel.GetCurSel();
	return TRUE;
}

BOOL ImageRecordingPage::GetJPEGQuality( unsigned int* quality )
{
	CString qualityTxt;
	m_edit_jpegCompression.GetWindowText(qualityTxt);
	return (!(qualityTxt.IsEmpty()) && ConvertToInt(&qualityTxt, quality));
}

BOOL ImageRecordingPage::GetJPEGProgressive( BOOL* progressive )
{
	*progressive = m_chk_jpegProgressive.GetCheck();	
	return TRUE;
}

BOOL ImageRecordingPage::GetJPEG2KQuality( unsigned int* quality )
{
	CString qualityTxt;
	m_edit_jpg2kCompressionLevel.GetWindowText(qualityTxt);
	return (!(qualityTxt.IsEmpty()) && ConvertToInt(&qualityTxt, quality));
}

void ImageRecordingPage::DisplayTIFFOptions(BOOL display)
{
	m_grp_tiffOptions.ShowWindow(display);
	m_static_tiffCompressionMethod.ShowWindow(display);
	m_combo_TiffCompressionMethod.ShowWindow(display);
}

void ImageRecordingPage::DisplayPNGOptions(BOOL display)
{
	m_grp_pngOptions.ShowWindow(display);
	m_chk_pngInterleaved.ShowWindow(display);
	m_static_pngCompressionLevel.ShowWindow(display);
	m_combo_pngCompressionLevel.ShowWindow(display);
}

void ImageRecordingPage::DisplayJPEGOptions(BOOL display)
{
	m_grp_jpegOptions.ShowWindow(display);
	m_chk_jpegProgressive.ShowWindow(display);
	m_static_jpegCompression.ShowWindow(display);
	m_edit_jpegCompression.ShowWindow(display);
	m_spin_jpegCompression.ShowWindow(display);
}

void ImageRecordingPage::DisplayJPG2kOptions(BOOL display)
{
	m_grp_jpeg2kOptions.ShowWindow(display);
	m_static_jpeg2kCompressionLevel.ShowWindow(display);
	m_edit_jpg2kCompressionLevel.ShowWindow(display);
	m_spin_jpeg2kCompressionLevel.ShowWindow(display);
}

void ImageRecordingPage::DisplayPxMOptions(BOOL display)
{
	m_grp_pxmOptions.ShowWindow(display)	;
	m_chk_pxmSaveAsBinary.ShowWindow(display);
}

void ImageRecordingPage::DisplayBMPOptions(BOOL display)
{
	if (display &&
		(m_currPixelFormat == PIXEL_FORMAT_BGR  ||
		 m_currPixelFormat == PIXEL_FORMAT_RGB8  ||
		 m_currPixelFormat == PIXEL_FORMAT_BGRU  ||
		 m_currPixelFormat == PIXEL_FORMAT_RGBU))
	{
		m_grp_bmpOptions.ShowWindow(TRUE);
		m_chk_8bitColorIndexed.ShowWindow(TRUE);
	}
	else
	{
		m_grp_bmpOptions.ShowWindow(FALSE);
		m_chk_8bitColorIndexed.ShowWindow(FALSE);
	}
}

void ImageRecordingPage::OnCbnSelchangeComboImageRecordType()
{
	switch (GetValidImageFormatSelection())
	{
	case PGM:
	case PPM:
		DisplayJPEGOptions(FALSE);
		DisplayJPG2kOptions(FALSE);
		DisplayPNGOptions(FALSE);
		DisplayTIFFOptions(FALSE);
		DisplayBMPOptions(FALSE);
		DisplayPxMOptions(TRUE);
		break;
	case BMP:
		DisplayJPEGOptions(FALSE);
		DisplayJPG2kOptions(FALSE);
		DisplayPNGOptions(FALSE);
		DisplayTIFFOptions(FALSE);
		DisplayPxMOptions(FALSE);
		DisplayBMPOptions(TRUE);
		break;
	case RAW:
		DisplayJPEGOptions(FALSE);
		DisplayJPG2kOptions(FALSE);
		DisplayPNGOptions(FALSE);
		DisplayTIFFOptions(FALSE);
		DisplayPxMOptions(FALSE);
		DisplayBMPOptions(FALSE);
		break;
	case JPEG:
		DisplayJPG2kOptions(FALSE);
		DisplayPNGOptions(FALSE);
		DisplayTIFFOptions(FALSE);
		DisplayPxMOptions(FALSE);
		DisplayBMPOptions(FALSE);
		DisplayJPEGOptions(TRUE);
		break;
	case JPEG2000:
		DisplayJPEGOptions(FALSE);
		DisplayPNGOptions(FALSE);
		DisplayTIFFOptions(FALSE);
		DisplayPxMOptions(FALSE);
		DisplayBMPOptions(FALSE);
		DisplayJPG2kOptions(TRUE);
		break;
	case TIFF:
		DisplayJPEGOptions(FALSE);
		DisplayPNGOptions(FALSE);
		DisplayPxMOptions(FALSE);
		DisplayJPG2kOptions(FALSE);
		DisplayBMPOptions(FALSE);
		DisplayTIFFOptions(TRUE);
		break;
	case PNG:
		DisplayJPEGOptions(FALSE);
		DisplayPxMOptions(FALSE);
		DisplayJPG2kOptions(FALSE);
		DisplayTIFFOptions(FALSE);
		DisplayBMPOptions(FALSE);
		DisplayPNGOptions(TRUE);
		break;
	default:
		break;
	}
}

void ImageRecordingPage::ValidateSettings( CString* errorList )
{
	unsigned int quality;
	switch(GetValidImageFormatSelection())
	{
	case JPEG:
		if((!GetJPEGQuality(&quality)) || (quality < 1) || (quality > 100))
		{
			errorList->Append("Invalid JPEG Quality value specified.\n");
		}
		break;
	case JPEG2000:
		if ((!GetJPEG2KQuality(&quality)) || (quality < 1) || (quality > 512))
		{
			errorList->Append("Invalid JPEG2000 Quality value specified.\n");
		}
		break;
	default:
		break;
	}
}

void ImageRecordingPage::EnableControls(BOOL enable)
{
	m_combo_ImageFormat.EnableWindow(enable);

	m_chk_jpegProgressive.EnableWindow(enable);
	m_edit_jpegCompression.EnableWindow(enable);
	m_spin_jpegCompression.EnableWindow(enable);

	m_edit_jpg2kCompressionLevel.EnableWindow(enable);
	m_spin_jpeg2kCompressionLevel.EnableWindow(enable);

	m_combo_pngCompressionLevel.EnableWindow(enable);
	m_chk_pngInterleaved.EnableWindow(enable);

	m_chk_pxmSaveAsBinary.EnableWindow(enable);

	m_combo_TiffCompressionMethod.EnableWindow(enable);
}

// Determine supported formats by saving temp images
void ImageRecordingPage::BuildSupportedOutputFormats(PixelFormat pixelFormat)
{
	m_currPixelFormat = pixelFormat;
	const unsigned int width = 40;
	const unsigned int height = 30;
	
	unsigned int bpp = GetBppFromPixelFormat(pixelFormat);
	float bytesPerPixel = ((float)bpp / 8.0);

	// create dummy image
	unsigned int bufferSize = ((float)(width * height)) * bytesPerPixel;
	unsigned char* dummyImage = new unsigned char[bufferSize];
	Image tempRaw(height, width, ((float)width) * bytesPerPixel, dummyImage, bufferSize, pixelFormat);

	Image* tempImage = &tempRaw;

	Image tempProcessed;
	if ((pixelFormat == PIXEL_FORMAT_RAW8)  || 
		(pixelFormat == PIXEL_FORMAT_RAW12) || 
		(pixelFormat == PIXEL_FORMAT_RAW16))
	{
		ColorProcessingAlgorithm colAlg = Image::GetDefaultColorProcessing();
		
		if (colAlg != NO_COLOR_PROCESSING)
		{
			if (tempRaw.Convert(PIXEL_FORMAT_BGR, &tempProcessed) == PGRERROR_OK)
			{
				tempImage = &tempProcessed;
			}
		}
	}
	
	TCHAR tempPath[MAX_PATH];
	TCHAR tempFile[MAX_PATH];
	const TCHAR* prefixString = "fc2";

	// clear combo box
	for (int i = m_combo_ImageFormat.GetCount()-1; i >= 0; i--)
	{
		m_combo_ImageFormat.DeleteString(i);
	}
	m_validFormats.reset();

	// for each output format
	for (unsigned int i = 0; i < NUM_IMAGE_FORMATS; i++)
	{
		// generate random file name
		DWORD retVal = GetTempPath(MAX_PATH, tempPath);
		UINT retVal2 = GetTempFileName(tempPath, prefixString, 0, tempFile);

		// save file
		Error error = tempImage->Save(tempFile, (ImageFileFormat)i);

		// if successful, flag it as supported
		if (error == PGRERROR_OK)
		{
			m_validFormats.set(i);
			m_combo_ImageFormat.AddString(ImageFormatList[i]);
		}
		DeleteFile(tempFile);
	}

	m_combo_ImageFormat.SetCurSel(0);
	OnCbnSelchangeComboImageRecordType();
	delete [] dummyImage; 
}

unsigned int ImageRecordingPage::GetBppFromPixelFormat( PixelFormat pixelFormat )
{
	switch(pixelFormat)
	{
	case PIXEL_FORMAT_MONO8:
	case PIXEL_FORMAT_RAW8:
		return 8;
		break;
	case PIXEL_FORMAT_411YUV8:
	case PIXEL_FORMAT_MONO12:
	case PIXEL_FORMAT_RAW12:
		return 12;
		break;
	case PIXEL_FORMAT_MONO16:
	case PIXEL_FORMAT_S_MONO16:
	case PIXEL_FORMAT_422YUV8:
	case PIXEL_FORMAT_RAW16:
		return 16;
		break;
	case PIXEL_FORMAT_444YUV8:
	case PIXEL_FORMAT_RGB8:
	case PIXEL_FORMAT_BGR:
		return 24;
		break;
	case PIXEL_FORMAT_BGRU:
	case PIXEL_FORMAT_RGBU:
		return 32;
		break;
	case PIXEL_FORMAT_S_RGB16:
	case PIXEL_FORMAT_RGB16:
	case PIXEL_FORMAT_BGR16:
		return 48;
		break;
	default:
		return 0;
		break;
	}
}

unsigned int ImageRecordingPage::GetValidImageFormatSelection()
{
	unsigned int selection = m_combo_ImageFormat.GetCurSel();
	unsigned int index = 0;

	for (unsigned int i = 0; i < NUM_IMAGE_FORMATS; i++)
	{
		if (m_validFormats.test(i))
		{
			if (index == selection)
			{
				index = i;
				break;
			}
			else
			{
				index++;
			}
		}
	}
	return index;
}

//Disable OnOK for Enter key
void ImageRecordingPage::OnBnClickedOk()
{
}

//Disable OnCancel for ESC key
void ImageRecordingPage::OnBnClickedCancel()
{
}