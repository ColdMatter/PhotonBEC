# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EMCCD_frontend_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1234, 761)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox_CameraAcquisition = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_CameraAcquisition.setGeometry(QtCore.QRect(10, 10, 431, 541))
        self.groupBox_CameraAcquisition.setObjectName("groupBox_CameraAcquisition")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.groupBox_CameraAcquisition)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 450, 411, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_AcquisitionButtons = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_AcquisitionButtons.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_AcquisitionButtons.setObjectName("horizontalLayout_AcquisitionButtons")
        self.pushButton_StartAcquisition = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_StartAcquisition.setObjectName("pushButton_StartAcquisition")
        self.horizontalLayout_AcquisitionButtons.addWidget(self.pushButton_StartAcquisition)
        self.pushButton_StopAcquisition = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_StopAcquisition.setObjectName("pushButton_StopAcquisition")
        self.horizontalLayout_AcquisitionButtons.addWidget(self.pushButton_StopAcquisition)
        self.pushButton_Undock = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_Undock.setObjectName("pushButton_Undock")
        self.horizontalLayout_AcquisitionButtons.addWidget(self.pushButton_Undock)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.groupBox_CameraAcquisition)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 30, 411, 411))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_CameraAcquisition = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_CameraAcquisition.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_CameraAcquisition.setObjectName("verticalLayout_CameraAcquisition")
        self.label_LostFrames = QtWidgets.QLabel(self.groupBox_CameraAcquisition)
        self.label_LostFrames.setGeometry(QtCore.QRect(10, 510, 91, 17))
        self.label_LostFrames.setObjectName("label_LostFrames")
        self.lineEdit_LostFrames = QtWidgets.QLineEdit(self.groupBox_CameraAcquisition)
        self.lineEdit_LostFrames.setGeometry(QtCore.QRect(100, 504, 113, 31))
        self.lineEdit_LostFrames.setReadOnly(True)
        self.lineEdit_LostFrames.setObjectName("lineEdit_LostFrames")
        self.groupBox_CameraMessage = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_CameraMessage.setGeometry(QtCore.QRect(10, 560, 431, 151))
        self.groupBox_CameraMessage.setObjectName("groupBox_CameraMessage")
        self.textBrowser_CameraMessage = QtWidgets.QTextBrowser(self.groupBox_CameraMessage)
        self.textBrowser_CameraMessage.setGeometry(QtCore.QRect(10, 30, 411, 111))
        self.textBrowser_CameraMessage.setObjectName("textBrowser_CameraMessage")
        self.groupBox_Temperature = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_Temperature.setGeometry(QtCore.QRect(450, 10, 251, 151))
        self.groupBox_Temperature.setObjectName("groupBox_Temperature")
        self.label_TemperatureSetpoint = QtWidgets.QLabel(self.groupBox_Temperature)
        self.label_TemperatureSetpoint.setGeometry(QtCore.QRect(10, 30, 67, 17))
        self.label_TemperatureSetpoint.setObjectName("label_TemperatureSetpoint")
        self.lineEdit_TemperatureSetPoint = QtWidgets.QLineEdit(self.groupBox_Temperature)
        self.lineEdit_TemperatureSetPoint.setGeometry(QtCore.QRect(10, 50, 91, 31))
        self.lineEdit_TemperatureSetPoint.setObjectName("lineEdit_TemperatureSetPoint")
        self.label_TemperatureReal = QtWidgets.QLabel(self.groupBox_Temperature)
        self.label_TemperatureReal.setGeometry(QtCore.QRect(120, 30, 67, 17))
        self.label_TemperatureReal.setObjectName("label_TemperatureReal")
        self.textBrowser_TemperatureReal = QtWidgets.QTextBrowser(self.groupBox_Temperature)
        self.textBrowser_TemperatureReal.setGeometry(QtCore.QRect(120, 50, 91, 31))
        self.textBrowser_TemperatureReal.setObjectName("textBrowser_TemperatureReal")
        self.pushButton_UpdateTemperature = QtWidgets.QPushButton(self.groupBox_Temperature)
        self.pushButton_UpdateTemperature.setGeometry(QtCore.QRect(10, 110, 201, 25))
        self.pushButton_UpdateTemperature.setObjectName("pushButton_UpdateTemperature")
        self.groupBox_Shutter = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_Shutter.setGeometry(QtCore.QRect(710, 10, 391, 151))
        self.groupBox_Shutter.setObjectName("groupBox_Shutter")
        self.label_ClosingTime = QtWidgets.QLabel(self.groupBox_Shutter)
        self.label_ClosingTime.setGeometry(QtCore.QRect(10, 60, 141, 17))
        self.label_ClosingTime.setObjectName("label_ClosingTime")
        self.label_OpeningTime = QtWidgets.QLabel(self.groupBox_Shutter)
        self.label_OpeningTime.setGeometry(QtCore.QRect(10, 90, 141, 17))
        self.label_OpeningTime.setObjectName("label_OpeningTime")
        self.label_OutputTTLSignal = QtWidgets.QLabel(self.groupBox_Shutter)
        self.label_OutputTTLSignal.setGeometry(QtCore.QRect(10, 120, 141, 17))
        self.label_OutputTTLSignal.setObjectName("label_OutputTTLSignal")
        self.lineEdit_ClosingTime = QtWidgets.QLineEdit(self.groupBox_Shutter)
        self.lineEdit_ClosingTime.setGeometry(QtCore.QRect(150, 60, 113, 25))
        self.lineEdit_ClosingTime.setObjectName("lineEdit_ClosingTime")
        self.lineEdit_OpeningTime = QtWidgets.QLineEdit(self.groupBox_Shutter)
        self.lineEdit_OpeningTime.setGeometry(QtCore.QRect(150, 90, 113, 25))
        self.lineEdit_OpeningTime.setObjectName("lineEdit_OpeningTime")
        self.comboBox_OutputTTLSignal = QtWidgets.QComboBox(self.groupBox_Shutter)
        self.comboBox_OutputTTLSignal.setGeometry(QtCore.QRect(150, 120, 111, 25))
        self.comboBox_OutputTTLSignal.setObjectName("comboBox_OutputTTLSignal")
        self.pushButton_UpdateShutter = QtWidgets.QPushButton(self.groupBox_Shutter)
        self.pushButton_UpdateShutter.setGeometry(QtCore.QRect(270, 120, 113, 25))
        self.pushButton_UpdateShutter.setObjectName("pushButton_UpdateShutter")
        self.label_ShutterType = QtWidgets.QLabel(self.groupBox_Shutter)
        self.label_ShutterType.setGeometry(QtCore.QRect(10, 30, 131, 17))
        self.label_ShutterType.setObjectName("label_ShutterType")
        self.comboBox_ShutterMode = QtWidgets.QComboBox(self.groupBox_Shutter)
        self.comboBox_ShutterMode.setGeometry(QtCore.QRect(150, 30, 231, 25))
        self.comboBox_ShutterMode.setObjectName("comboBox_ShutterMode")
        self.groupBox_ImageFormat = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_ImageFormat.setGeometry(QtCore.QRect(450, 170, 251, 241))
        self.groupBox_ImageFormat.setObjectName("groupBox_ImageFormat")
        self.label_HorizontalBinning = QtWidgets.QLabel(self.groupBox_ImageFormat)
        self.label_HorizontalBinning.setGeometry(QtCore.QRect(10, 30, 141, 17))
        self.label_HorizontalBinning.setObjectName("label_HorizontalBinning")
        self.label_VerticalBinning = QtWidgets.QLabel(self.groupBox_ImageFormat)
        self.label_VerticalBinning.setGeometry(QtCore.QRect(10, 60, 141, 17))
        self.label_VerticalBinning.setObjectName("label_VerticalBinning")
        self.label_HorizontalStart = QtWidgets.QLabel(self.groupBox_ImageFormat)
        self.label_HorizontalStart.setGeometry(QtCore.QRect(10, 90, 141, 17))
        self.label_HorizontalStart.setObjectName("label_HorizontalStart")
        self.label_HorizontalEnd = QtWidgets.QLabel(self.groupBox_ImageFormat)
        self.label_HorizontalEnd.setGeometry(QtCore.QRect(10, 120, 141, 17))
        self.label_HorizontalEnd.setObjectName("label_HorizontalEnd")
        self.label_VerticalStart = QtWidgets.QLabel(self.groupBox_ImageFormat)
        self.label_VerticalStart.setGeometry(QtCore.QRect(10, 150, 141, 17))
        self.label_VerticalStart.setObjectName("label_VerticalStart")
        self.label_VerticalEnd = QtWidgets.QLabel(self.groupBox_ImageFormat)
        self.label_VerticalEnd.setGeometry(QtCore.QRect(10, 180, 141, 17))
        self.label_VerticalEnd.setObjectName("label_VerticalEnd")
        self.lineEdit_HorizontalBinning = QtWidgets.QLineEdit(self.groupBox_ImageFormat)
        self.lineEdit_HorizontalBinning.setGeometry(QtCore.QRect(170, 30, 71, 25))
        self.lineEdit_HorizontalBinning.setObjectName("lineEdit_HorizontalBinning")
        self.lineEdit_VerticalBinning = QtWidgets.QLineEdit(self.groupBox_ImageFormat)
        self.lineEdit_VerticalBinning.setGeometry(QtCore.QRect(170, 60, 71, 25))
        self.lineEdit_VerticalBinning.setObjectName("lineEdit_VerticalBinning")
        self.lineEdit_HorizontalStart = QtWidgets.QLineEdit(self.groupBox_ImageFormat)
        self.lineEdit_HorizontalStart.setGeometry(QtCore.QRect(170, 90, 71, 25))
        self.lineEdit_HorizontalStart.setObjectName("lineEdit_HorizontalStart")
        self.lineEdit_HorizontalEnd = QtWidgets.QLineEdit(self.groupBox_ImageFormat)
        self.lineEdit_HorizontalEnd.setGeometry(QtCore.QRect(170, 120, 71, 25))
        self.lineEdit_HorizontalEnd.setObjectName("lineEdit_HorizontalEnd")
        self.lineEdit_VerticalStart = QtWidgets.QLineEdit(self.groupBox_ImageFormat)
        self.lineEdit_VerticalStart.setGeometry(QtCore.QRect(170, 150, 71, 25))
        self.lineEdit_VerticalStart.setObjectName("lineEdit_VerticalStart")
        self.lineEdit_VerticalEnd = QtWidgets.QLineEdit(self.groupBox_ImageFormat)
        self.lineEdit_VerticalEnd.setGeometry(QtCore.QRect(170, 180, 71, 25))
        self.lineEdit_VerticalEnd.setObjectName("lineEdit_VerticalEnd")
        self.pushButton_SetImageFormat = QtWidgets.QPushButton(self.groupBox_ImageFormat)
        self.pushButton_SetImageFormat.setGeometry(QtCore.QRect(20, 210, 211, 25))
        self.pushButton_SetImageFormat.setObjectName("pushButton_SetImageFormat")
        self.groupBox_Acquisition = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_Acquisition.setGeometry(QtCore.QRect(710, 170, 291, 241))
        self.groupBox_Acquisition.setObjectName("groupBox_Acquisition")
        self.label_ExposureTime = QtWidgets.QLabel(self.groupBox_Acquisition)
        self.label_ExposureTime.setGeometry(QtCore.QRect(10, 30, 201, 17))
        self.label_ExposureTime.setObjectName("label_ExposureTime")
        self.label_AccumulationCycleTime = QtWidgets.QLabel(self.groupBox_Acquisition)
        self.label_AccumulationCycleTime.setGeometry(QtCore.QRect(10, 60, 201, 17))
        self.label_AccumulationCycleTime.setObjectName("label_AccumulationCycleTime")
        self.label_NumberAccumulations = QtWidgets.QLabel(self.groupBox_Acquisition)
        self.label_NumberAccumulations.setGeometry(QtCore.QRect(10, 90, 201, 17))
        self.label_NumberAccumulations.setObjectName("label_NumberAccumulations")
        self.label_NumberKinetics = QtWidgets.QLabel(self.groupBox_Acquisition)
        self.label_NumberKinetics.setGeometry(QtCore.QRect(10, 120, 201, 17))
        self.label_NumberKinetics.setObjectName("label_NumberKinetics")
        self.label_KineticCycleTime = QtWidgets.QLabel(self.groupBox_Acquisition)
        self.label_KineticCycleTime.setGeometry(QtCore.QRect(10, 150, 201, 17))
        self.label_KineticCycleTime.setObjectName("label_KineticCycleTime")
        self.lineEdit_ExposureTime = QtWidgets.QLineEdit(self.groupBox_Acquisition)
        self.lineEdit_ExposureTime.setGeometry(QtCore.QRect(210, 30, 71, 25))
        self.lineEdit_ExposureTime.setObjectName("lineEdit_ExposureTime")
        self.lineEdit_AccumulationCycleTime = QtWidgets.QLineEdit(self.groupBox_Acquisition)
        self.lineEdit_AccumulationCycleTime.setGeometry(QtCore.QRect(210, 60, 71, 25))
        self.lineEdit_AccumulationCycleTime.setObjectName("lineEdit_AccumulationCycleTime")
        self.lineEdit_NumberAccumulations = QtWidgets.QLineEdit(self.groupBox_Acquisition)
        self.lineEdit_NumberAccumulations.setGeometry(QtCore.QRect(210, 90, 71, 25))
        self.lineEdit_NumberAccumulations.setObjectName("lineEdit_NumberAccumulations")
        self.lineEdit_NumberKinetics = QtWidgets.QLineEdit(self.groupBox_Acquisition)
        self.lineEdit_NumberKinetics.setGeometry(QtCore.QRect(210, 120, 71, 25))
        self.lineEdit_NumberKinetics.setObjectName("lineEdit_NumberKinetics")
        self.lineEdit_KineticCycleTime = QtWidgets.QLineEdit(self.groupBox_Acquisition)
        self.lineEdit_KineticCycleTime.setGeometry(QtCore.QRect(210, 150, 71, 25))
        self.lineEdit_KineticCycleTime.setObjectName("lineEdit_KineticCycleTime")
        self.pushButton_SetAcquisitionProperties = QtWidgets.QPushButton(self.groupBox_Acquisition)
        self.pushButton_SetAcquisitionProperties.setGeometry(QtCore.QRect(30, 210, 231, 25))
        self.pushButton_SetAcquisitionProperties.setObjectName("pushButton_SetAcquisitionProperties")
        self.groupBox_ReadOut = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_ReadOut.setGeometry(QtCore.QRect(1010, 170, 201, 241))
        self.groupBox_ReadOut.setObjectName("groupBox_ReadOut")
        self.label_HorizontalShiftSpeed = QtWidgets.QLabel(self.groupBox_ReadOut)
        self.label_HorizontalShiftSpeed.setGeometry(QtCore.QRect(10, 30, 161, 17))
        self.label_HorizontalShiftSpeed.setObjectName("label_HorizontalShiftSpeed")
        self.comboBox_HorizontalShiftSpeed = QtWidgets.QComboBox(self.groupBox_ReadOut)
        self.comboBox_HorizontalShiftSpeed.setGeometry(QtCore.QRect(10, 50, 181, 25))
        self.comboBox_HorizontalShiftSpeed.setObjectName("comboBox_HorizontalShiftSpeed")
        self.label_VerticalShiftSpeed = QtWidgets.QLabel(self.groupBox_ReadOut)
        self.label_VerticalShiftSpeed.setGeometry(QtCore.QRect(10, 80, 161, 17))
        self.label_VerticalShiftSpeed.setObjectName("label_VerticalShiftSpeed")
        self.comboBox_VerticalShiftSpeed = QtWidgets.QComboBox(self.groupBox_ReadOut)
        self.comboBox_VerticalShiftSpeed.setGeometry(QtCore.QRect(10, 100, 181, 25))
        self.comboBox_VerticalShiftSpeed.setObjectName("comboBox_VerticalShiftSpeed")
        self.pushButton_SetReadOut = QtWidgets.QPushButton(self.groupBox_ReadOut)
        self.pushButton_SetReadOut.setGeometry(QtCore.QRect(10, 150, 181, 25))
        self.pushButton_SetReadOut.setObjectName("pushButton_SetReadOut")
        self.checkBox_FrameTransferMode = QtWidgets.QCheckBox(self.groupBox_ReadOut)
        self.checkBox_FrameTransferMode.setGeometry(QtCore.QRect(10, 210, 181, 23))
        self.checkBox_FrameTransferMode.setObjectName("checkBox_FrameTransferMode")
        self.groupBox_Gain = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_Gain.setGeometry(QtCore.QRect(450, 430, 251, 281))
        self.groupBox_Gain.setObjectName("groupBox_Gain")
        self.label_PreAmpGain = QtWidgets.QLabel(self.groupBox_Gain)
        self.label_PreAmpGain.setGeometry(QtCore.QRect(10, 30, 101, 17))
        self.label_PreAmpGain.setObjectName("label_PreAmpGain")
        self.comboBox_PreAmpGain = QtWidgets.QComboBox(self.groupBox_Gain)
        self.comboBox_PreAmpGain.setGeometry(QtCore.QRect(120, 30, 121, 25))
        self.comboBox_PreAmpGain.setObjectName("comboBox_PreAmpGain")
        self.pushButton_SetGain = QtWidgets.QPushButton(self.groupBox_Gain)
        self.pushButton_SetGain.setGeometry(QtCore.QRect(20, 240, 211, 25))
        self.pushButton_SetGain.setObjectName("pushButton_SetGain")
        self.checkBox_AllowHighEMGain = QtWidgets.QCheckBox(self.groupBox_Gain)
        self.checkBox_AllowHighEMGain.setGeometry(QtCore.QRect(10, 60, 211, 23))
        self.checkBox_AllowHighEMGain.setObjectName("checkBox_AllowHighEMGain")
        self.label_EMCCDGainRange = QtWidgets.QLabel(self.groupBox_Gain)
        self.label_EMCCDGainRange.setGeometry(QtCore.QRect(10, 100, 141, 17))
        self.label_EMCCDGainRange.setObjectName("label_EMCCDGainRange")
        self.lineEdit_EMCCDGainRange = QtWidgets.QLineEdit(self.groupBox_Gain)
        self.lineEdit_EMCCDGainRange.setGeometry(QtCore.QRect(150, 100, 91, 25))
        self.lineEdit_EMCCDGainRange.setReadOnly(True)
        self.lineEdit_EMCCDGainRange.setObjectName("lineEdit_EMCCDGainRange")
        self.label_EMCCDGain = QtWidgets.QLabel(self.groupBox_Gain)
        self.label_EMCCDGain.setGeometry(QtCore.QRect(10, 140, 141, 17))
        self.label_EMCCDGain.setObjectName("label_EMCCDGain")
        self.lineEdit_EMCCDGain = QtWidgets.QLineEdit(self.groupBox_Gain)
        self.lineEdit_EMCCDGain.setGeometry(QtCore.QRect(150, 140, 91, 25))
        self.lineEdit_EMCCDGain.setObjectName("lineEdit_EMCCDGain")
        self.groupBox_Plotting = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_Plotting.setGeometry(QtCore.QRect(710, 430, 291, 141))
        self.groupBox_Plotting.setObjectName("groupBox_Plotting")
        self.label_signal_min = QtWidgets.QLabel(self.groupBox_Plotting)
        self.label_signal_min.setEnabled(True)
        self.label_signal_min.setGeometry(QtCore.QRect(10, 30, 71, 16))
        self.label_signal_min.setObjectName("label_signal_min")
        self.lineEdit_signal_min = QtWidgets.QLineEdit(self.groupBox_Plotting)
        self.lineEdit_signal_min.setGeometry(QtCore.QRect(10, 50, 81, 20))
        self.lineEdit_signal_min.setReadOnly(True)
        self.lineEdit_signal_min.setObjectName("lineEdit_signal_min")
        self.label_signal_max = QtWidgets.QLabel(self.groupBox_Plotting)
        self.label_signal_max.setGeometry(QtCore.QRect(10, 80, 71, 16))
        self.label_signal_max.setObjectName("label_signal_max")
        self.lineEdit_signal_max = QtWidgets.QLineEdit(self.groupBox_Plotting)
        self.lineEdit_signal_max.setGeometry(QtCore.QRect(10, 100, 81, 20))
        self.lineEdit_signal_max.setReadOnly(True)
        self.lineEdit_signal_max.setObjectName("lineEdit_signal_max")
        self.label_cmap_min = QtWidgets.QLabel(self.groupBox_Plotting)
        self.label_cmap_min.setEnabled(True)
        self.label_cmap_min.setGeometry(QtCore.QRect(110, 30, 71, 16))
        self.label_cmap_min.setObjectName("label_cmap_min")
        self.lineEdit_cmap_min = QtWidgets.QLineEdit(self.groupBox_Plotting)
        self.lineEdit_cmap_min.setGeometry(QtCore.QRect(110, 50, 81, 20))
        self.lineEdit_cmap_min.setReadOnly(False)
        self.lineEdit_cmap_min.setObjectName("lineEdit_cmap_min")
        self.label_signal_max_2 = QtWidgets.QLabel(self.groupBox_Plotting)
        self.label_signal_max_2.setGeometry(QtCore.QRect(110, 80, 71, 16))
        self.label_signal_max_2.setObjectName("label_signal_max_2")
        self.lineEdit_cmap_max = QtWidgets.QLineEdit(self.groupBox_Plotting)
        self.lineEdit_cmap_max.setGeometry(QtCore.QRect(110, 100, 81, 20))
        self.lineEdit_cmap_max.setReadOnly(False)
        self.lineEdit_cmap_max.setObjectName("lineEdit_cmap_max")
        self.pushButton_PlottingSet = QtWidgets.QPushButton(self.groupBox_Plotting)
        self.pushButton_PlottingSet.setGeometry(QtCore.QRect(210, 80, 61, 41))
        self.pushButton_PlottingSet.setObjectName("pushButton_PlottingSet")
        self.pushButton_Hist = QtWidgets.QPushButton(self.groupBox_Plotting)
        self.pushButton_Hist.setGeometry(QtCore.QRect(210, 20, 61, 21))
        self.pushButton_Hist.setObjectName("pushButton_Hist")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1234, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuCamera_Set_up = QtWidgets.QMenu(self.menubar)
        self.menuCamera_Set_up.setObjectName("menuCamera_Set_up")
        self.menuAcquisition_Mode = QtWidgets.QMenu(self.menuCamera_Set_up)
        self.menuAcquisition_Mode.setObjectName("menuAcquisition_Mode")
        self.menuOutput_Amplifier = QtWidgets.QMenu(self.menuCamera_Set_up)
        self.menuOutput_Amplifier.setObjectName("menuOutput_Amplifier")
        self.menuReadout_Mode = QtWidgets.QMenu(self.menuCamera_Set_up)
        self.menuReadout_Mode.setObjectName("menuReadout_Mode")
        self.menuTrigger_Mode = QtWidgets.QMenu(self.menuCamera_Set_up)
        self.menuTrigger_Mode.setObjectName("menuTrigger_Mode")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit_Camera = QtWidgets.QAction(MainWindow)
        self.actionExit_Camera.setObjectName("actionExit_Camera")
        self.actionSingle_Scan = QtWidgets.QAction(MainWindow)
        self.actionSingle_Scan.setObjectName("actionSingle_Scan")
        self.actionAccumulate = QtWidgets.QAction(MainWindow)
        self.actionAccumulate.setObjectName("actionAccumulate")
        self.actionKinetics = QtWidgets.QAction(MainWindow)
        self.actionKinetics.setObjectName("actionKinetics")
        self.actionFast_Kinetics = QtWidgets.QAction(MainWindow)
        self.actionFast_Kinetics.setObjectName("actionFast_Kinetics")
        self.actionRun_Till_Abort = QtWidgets.QAction(MainWindow)
        self.actionRun_Till_Abort.setObjectName("actionRun_Till_Abort")
        self.actionEMCCD = QtWidgets.QAction(MainWindow)
        self.actionEMCCD.setObjectName("actionEMCCD")
        self.actionCCD = QtWidgets.QAction(MainWindow)
        self.actionCCD.setObjectName("actionCCD")
        self.actionFull_Vertical_Binning = QtWidgets.QAction(MainWindow)
        self.actionFull_Vertical_Binning.setObjectName("actionFull_Vertical_Binning")
        self.actionMulti_Track = QtWidgets.QAction(MainWindow)
        self.actionMulti_Track.setObjectName("actionMulti_Track")
        self.actionRandom_Track = QtWidgets.QAction(MainWindow)
        self.actionRandom_Track.setObjectName("actionRandom_Track")
        self.actionSingle_Track = QtWidgets.QAction(MainWindow)
        self.actionSingle_Track.setObjectName("actionSingle_Track")
        self.actionImage = QtWidgets.QAction(MainWindow)
        self.actionImage.setObjectName("actionImage")
        self.actionFully_Auto = QtWidgets.QAction(MainWindow)
        self.actionFully_Auto.setObjectName("actionFully_Auto")
        self.actionPermanently_Open = QtWidgets.QAction(MainWindow)
        self.actionPermanently_Open.setObjectName("actionPermanently_Open")
        self.actionPermanently_Closed = QtWidgets.QAction(MainWindow)
        self.actionPermanently_Closed.setObjectName("actionPermanently_Closed")
        self.actionOpen_for_FVB_Series = QtWidgets.QAction(MainWindow)
        self.actionOpen_for_FVB_Series.setObjectName("actionOpen_for_FVB_Series")
        self.actionOpen_for_any_Series = QtWidgets.QAction(MainWindow)
        self.actionOpen_for_any_Series.setObjectName("actionOpen_for_any_Series")
        self.actionInternal = QtWidgets.QAction(MainWindow)
        self.actionInternal.setObjectName("actionInternal")
        self.actionExternal = QtWidgets.QAction(MainWindow)
        self.actionExternal.setObjectName("actionExternal")
        self.actionExternal_Start = QtWidgets.QAction(MainWindow)
        self.actionExternal_Start.setObjectName("actionExternal_Start")
        self.actionExternal_Exposure_bulb = QtWidgets.QAction(MainWindow)
        self.actionExternal_Exposure_bulb.setObjectName("actionExternal_Exposure_bulb")
        self.actionExternal_FVB_EM = QtWidgets.QAction(MainWindow)
        self.actionExternal_FVB_EM.setObjectName("actionExternal_FVB_EM")
        self.actionSoftware_Trigger = QtWidgets.QAction(MainWindow)
        self.actionSoftware_Trigger.setObjectName("actionSoftware_Trigger")
        self.actionExternal_Charge_Shifting = QtWidgets.QAction(MainWindow)
        self.actionExternal_Charge_Shifting.setObjectName("actionExternal_Charge_Shifting")
        self.menuFile.addAction(self.actionExit_Camera)
        self.menuAcquisition_Mode.addAction(self.actionSingle_Scan)
        self.menuAcquisition_Mode.addAction(self.actionAccumulate)
        self.menuAcquisition_Mode.addAction(self.actionKinetics)
        self.menuAcquisition_Mode.addAction(self.actionFast_Kinetics)
        self.menuAcquisition_Mode.addAction(self.actionRun_Till_Abort)
        self.menuOutput_Amplifier.addAction(self.actionEMCCD)
        self.menuOutput_Amplifier.addAction(self.actionCCD)
        self.menuReadout_Mode.addAction(self.actionFull_Vertical_Binning)
        self.menuReadout_Mode.addAction(self.actionMulti_Track)
        self.menuReadout_Mode.addAction(self.actionRandom_Track)
        self.menuReadout_Mode.addAction(self.actionSingle_Track)
        self.menuReadout_Mode.addAction(self.actionImage)
        self.menuTrigger_Mode.addAction(self.actionInternal)
        self.menuTrigger_Mode.addAction(self.actionExternal)
        self.menuTrigger_Mode.addAction(self.actionExternal_Start)
        self.menuTrigger_Mode.addAction(self.actionExternal_Exposure_bulb)
        self.menuTrigger_Mode.addAction(self.actionExternal_FVB_EM)
        self.menuTrigger_Mode.addAction(self.actionSoftware_Trigger)
        self.menuTrigger_Mode.addAction(self.actionExternal_Charge_Shifting)
        self.menuCamera_Set_up.addAction(self.menuAcquisition_Mode.menuAction())
        self.menuCamera_Set_up.addAction(self.menuOutput_Amplifier.menuAction())
        self.menuCamera_Set_up.addAction(self.menuReadout_Mode.menuAction())
        self.menuCamera_Set_up.addAction(self.menuTrigger_Mode.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuCamera_Set_up.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pbec lab EMCCD"))
        self.groupBox_CameraAcquisition.setTitle(_translate("MainWindow", "Camera Acquisition"))
        self.pushButton_StartAcquisition.setText(_translate("MainWindow", "Start Acquisition"))
        self.pushButton_StopAcquisition.setText(_translate("MainWindow", "Stop Acquisition"))
        self.pushButton_Undock.setText(_translate("MainWindow", "Undock"))
        self.label_LostFrames.setText(_translate("MainWindow", "Lost frames:"))
        self.groupBox_CameraMessage.setTitle(_translate("MainWindow", "Camera Message"))
        self.groupBox_Temperature.setTitle(_translate("MainWindow", "Temperature"))
        self.label_TemperatureSetpoint.setText(_translate("MainWindow", "Setpoint:"))
        self.label_TemperatureReal.setText(_translate("MainWindow", "Real:"))
        self.pushButton_UpdateTemperature.setText(_translate("MainWindow", "Update Temperature"))
        self.groupBox_Shutter.setTitle(_translate("MainWindow", "Shutter"))
        self.label_ClosingTime.setText(_translate("MainWindow", "Closing Time (ms)"))
        self.label_OpeningTime.setText(_translate("MainWindow", "Opening Time (ms)"))
        self.label_OutputTTLSignal.setText(_translate("MainWindow", "Output TTL Signal "))
        self.pushButton_UpdateShutter.setText(_translate("MainWindow", "Set"))
        self.label_ShutterType.setText(_translate("MainWindow", "Shutter Mode"))
        self.groupBox_ImageFormat.setTitle(_translate("MainWindow", "Image Format"))
        self.label_HorizontalBinning.setText(_translate("MainWindow", "Horizontal Binning:"))
        self.label_VerticalBinning.setText(_translate("MainWindow", "Vertical Binning:"))
        self.label_HorizontalStart.setText(_translate("MainWindow", "Horozontal Start:"))
        self.label_HorizontalEnd.setText(_translate("MainWindow", "Horizontal End:"))
        self.label_VerticalStart.setText(_translate("MainWindow", "Vertical Start:"))
        self.label_VerticalEnd.setText(_translate("MainWindow", "Vertical End:"))
        self.pushButton_SetImageFormat.setText(_translate("MainWindow", "Set Image Format"))
        self.groupBox_Acquisition.setTitle(_translate("MainWindow", "Acquisition"))
        self.label_ExposureTime.setText(_translate("MainWindow", "Exposure Time (s):"))
        self.label_AccumulationCycleTime.setText(_translate("MainWindow", "Accumulation Cycle Time (s):"))
        self.label_NumberAccumulations.setText(_translate("MainWindow", "Number of Accumulations:"))
        self.label_NumberKinetics.setText(_translate("MainWindow", "Number of Kinetics (Scans):"))
        self.label_KineticCycleTime.setText(_translate("MainWindow", "Kinetic Cycle Time (s):"))
        self.pushButton_SetAcquisitionProperties.setText(_translate("MainWindow", "Set Acquisition Properties"))
        self.groupBox_ReadOut.setTitle(_translate("MainWindow", "Read Out"))
        self.label_HorizontalShiftSpeed.setText(_translate("MainWindow", "Horizontal Shift Speed:"))
        self.label_VerticalShiftSpeed.setText(_translate("MainWindow", "Vertical Shift Speed:"))
        self.pushButton_SetReadOut.setText(_translate("MainWindow", "Set"))
        self.checkBox_FrameTransferMode.setText(_translate("MainWindow", "Frame Transfer Mode"))
        self.groupBox_Gain.setTitle(_translate("MainWindow", "Gain"))
        self.label_PreAmpGain.setText(_translate("MainWindow", "Pre-Amp gain:"))
        self.pushButton_SetGain.setText(_translate("MainWindow", "Set"))
        self.checkBox_AllowHighEMGain.setText(_translate("MainWindow", "Allow High EM Gain"))
        self.label_EMCCDGainRange.setText(_translate("MainWindow", "EMCCD Gain Range:"))
        self.label_EMCCDGain.setText(_translate("MainWindow", "EMCCD Gain:"))
        self.groupBox_Plotting.setTitle(_translate("MainWindow", "Plotting"))
        self.label_signal_min.setText(_translate("MainWindow", "Signal (min):"))
        self.label_signal_max.setText(_translate("MainWindow", "Signal (max):"))
        self.label_cmap_min.setText(_translate("MainWindow", "Cmap (min):"))
        self.label_signal_max_2.setText(_translate("MainWindow", "Cmap (max):"))
        self.pushButton_PlottingSet.setText(_translate("MainWindow", "Set"))
        self.pushButton_Hist.setText(_translate("MainWindow", "Hist"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuCamera_Set_up.setTitle(_translate("MainWindow", "Camera Set-up"))
        self.menuAcquisition_Mode.setTitle(_translate("MainWindow", "Acquisition Mode"))
        self.menuOutput_Amplifier.setTitle(_translate("MainWindow", "Output Amplifier"))
        self.menuReadout_Mode.setTitle(_translate("MainWindow", "Readout Mode"))
        self.menuTrigger_Mode.setTitle(_translate("MainWindow", "Trigger Mode"))
        self.actionExit_Camera.setText(_translate("MainWindow", "Exit Camera"))
        self.actionSingle_Scan.setText(_translate("MainWindow", "Single Scan"))
        self.actionAccumulate.setText(_translate("MainWindow", "Accumulate"))
        self.actionKinetics.setText(_translate("MainWindow", "Kinetics"))
        self.actionFast_Kinetics.setText(_translate("MainWindow", "Fast Kinetics"))
        self.actionRun_Till_Abort.setText(_translate("MainWindow", "Run Till Abort"))
        self.actionEMCCD.setText(_translate("MainWindow", "EMCCD"))
        self.actionCCD.setText(_translate("MainWindow", "CCD"))
        self.actionFull_Vertical_Binning.setText(_translate("MainWindow", "Full Vertical Binning"))
        self.actionMulti_Track.setText(_translate("MainWindow", "Multi-Track"))
        self.actionRandom_Track.setText(_translate("MainWindow", "Random-Track"))
        self.actionSingle_Track.setText(_translate("MainWindow", "Single-Track"))
        self.actionImage.setText(_translate("MainWindow", "Image"))
        self.actionFully_Auto.setText(_translate("MainWindow", "Fully Auto"))
        self.actionPermanently_Open.setText(_translate("MainWindow", "Permanently Open"))
        self.actionPermanently_Closed.setText(_translate("MainWindow", "Permanently Closed"))
        self.actionOpen_for_FVB_Series.setText(_translate("MainWindow", "Open for FVB Series"))
        self.actionOpen_for_any_Series.setText(_translate("MainWindow", "Open for any Series"))
        self.actionInternal.setText(_translate("MainWindow", "Internal"))
        self.actionExternal.setText(_translate("MainWindow", "External"))
        self.actionExternal_Start.setText(_translate("MainWindow", "External Start"))
        self.actionExternal_Exposure_bulb.setText(_translate("MainWindow", "External Exposure (bulb)"))
        self.actionExternal_FVB_EM.setText(_translate("MainWindow", "External FVB EM"))
        self.actionSoftware_Trigger.setText(_translate("MainWindow", "Software Trigger"))
        self.actionExternal_Charge_Shifting.setText(_translate("MainWindow", "External Charge Shifting"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
