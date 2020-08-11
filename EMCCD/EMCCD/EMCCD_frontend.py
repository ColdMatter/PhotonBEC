from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import copy
import numpy as np
from functools import partial
import time
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from queue import Queue

from EMCCD_frontend_GUI import Ui_MainWindow
from EMCCD_backend import EMCCD


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)




class AcquisitionThread(QtCore.QThread):
	def __init__(self, data_queue, camera):
		super(AcquisitionThread, self).__init__()
		self.RUNNING = True
		self.ACQUIRING = False
		self.data_queue = data_queue
		self.camera = camera
	
	def run(self):
		while self.RUNNING:
			while self.ACQUIRING:
				self.acquisition()
				time.sleep(0.01)
			time.sleep(0.1)

	def acquisition(self):
		FLAG, message, info = self.camera.GetStatus(VERBOSE=False)
		if info == "DRV_IDLE" or info == "DRV_ACQUIRING":
			if info == "DRV_IDLE":
				self.ACQUIRING = False
			FLAG, message, image = self.camera.GetAcquiredData(VERBOSE=False)
			if type(image)==np.ndarray:
				self.data_queue.put(image)


				
			




class PlottingThread(QtCore.QThread):
	def __init__(self, canvas, data_queue, lineEdit_LostFrames):
		super(PlottingThread, self).__init__()
		self.RUNNING = True
		self.data_queue = data_queue
		self.canvas = canvas
		self.lineEdit_LostFrames = lineEdit_LostFrames
		self.canvas.axes.set_xticks([])
		self.canvas.axes.set_yticks([])
		self.canvas.show()
		self.lost_frames = 0

	def run(self):
		self.lineEdit_LostFrames.setText(str(self.lost_frames))
		while self.RUNNING:
			self.plot()
			time.sleep(0.01)
		self.quit()

	def plot(self):
		if not self.data_queue.empty():
			data = self.data_queue.get()
			while not self.data_queue.empty():
				dummy = self.data_queue.get()
				self.lost_frames += 1
				self.lineEdit_LostFrames.setText(str(self.lost_frames))
			if not hasattr(self, "image"):
				self.image = self.canvas.axes.imshow(data, cmap='gray')
			else:
				self.image.set_data(data)
			self.canvas.draw()



class EMCCD_frontend(Ui_MainWindow):


	def __init__(self):

		pass		



	def StartCameraSDK(self):

		self.camera = EMCCD(VERBOSE=True, frontend=self)


	def write_camera_message(self, message):
		self.textBrowser_CameraMessage.append(message)
		self.textBrowser_CameraMessage.moveCursor(QtGui.QTextCursor.End)





	def setup(self):

		# Menu: File
		self.actionExit_Camera.triggered.connect(self._Exit_Camera)

		# Menu: Camera Set-up / Acquisition Mode
		self.actions_Acquisition_Mode = {"single scan": self.actionSingle_Scan, "accumulate": self.actionAccumulate, "kinetics": self.actionKinetics, "fast kinetics": self.actionFast_Kinetics, "run till abort":self.actionRun_Till_Abort}
		[action.setCheckable(True) for action in self.actions_Acquisition_Mode.values()]
		[action.triggered.connect(partial(self._Acquisition_Mode, mode)) for mode, action in self.actions_Acquisition_Mode.items()]

		# Menu: Camera Set-up / Output Amplifier
		self.actions_OutputAmplifier = {"EMCCD": self.actionEMCCD, "CCD":self.actionCCD}
		[action.setCheckable(True) for action in self.actions_OutputAmplifier.values()]
		[action.triggered.connect(partial(self._Output_Amplifier_Mode, mode)) for mode, action in self.actions_OutputAmplifier.items()]

		# Menu: Camera Set-up / ReadOut Mode
		self.actions_ReadoutMode = {"full vertical binning": self.actionFull_Vertical_Binning, "multi-track": self.actionMulti_Track, "random-track": self.actionRandom_Track, "single-track": self.actionSingle_Track, "image": self.actionImage}
		[action.setCheckable(True) for action in self.actions_ReadoutMode.values()]
		[action.triggered.connect(partial(self._Readout_Mode, mode)) for mode, action in self.actions_ReadoutMode.items()]

		# Menu: Camera Set-up / Trigger Mode
		self.actions_TriggerMode = {"internal": self.actionInternal, "external": self.actionExternal, "external start": self.actionExternal_Start, "external exposure (bulb)": self.actionExternal_Exposure_bulb, "external FVB EM": self.actionExternal_FVB_EM, "software trigger": self.actionSoftware_Trigger, "external charge shifting": self.actionExternal_Charge_Shifting}
		[action.setCheckable(True) for action in self.actions_TriggerMode.values()]
		[action.triggered.connect(partial(self._Trigger_Mode, mode)) for mode, action in self.actions_TriggerMode.items()]

		# GroupBox: Temperature
		self.lineEdit_TemperatureSetPoint.setText(str(20))
		self.pushButton_UpdateTemperature.clicked.connect(self._Temperature)

		# GroupBox: Shutter
		self.comboBox_ShutterMode_modes = {"Fully Auto": "fully auto", "Permanently Open": "permanently open", "Permanently Closed": "permanently closed", "Open for FVB Series": "open for FVB series", "Open for any Series": "open for any series"}
		[self.comboBox_ShutterMode.addItem(mode) for mode in self.comboBox_ShutterMode_modes.keys()]
		self.comboBox_OutputTTLSignal_modes = {"Low":0, "High":1}
		[self.comboBox_OutputTTLSignal.addItem(mode) for mode in self.comboBox_OutputTTLSignal_modes.keys()]
		self.lineEdit_ClosingTime.setText(str(0))
		self.lineEdit_OpeningTime.setText(str(0))
		self.pushButton_UpdateShutter.clicked.connect(self._Shutter_Mode)

		# GroupBox: Image Format
		self.lineEdit_HorizontalBinning.setText(str(1))
		self.lineEdit_VerticalBinning.setText(str(1))
		self.lineEdit_HorizontalStart.setText(str(1))
		self.lineEdit_HorizontalEnd.setText(str(self.camera.xpixels))
		self.lineEdit_VerticalStart.setText(str(1))
		self.lineEdit_VerticalEnd.setText(str(self.camera.xpixels))
		self.pushButton_SetImageFormat.clicked.connect(self._Image_Format)

		# GroupBox: Acquisition
		self.lineEdit_ExposureTime.setText(str(0.001))
		self.lineEdit_AccumulationCycleTime.setText(str(0.001))
		self.lineEdit_NumberAccumulations.setText(str(10))
		self.lineEdit_NumberKinetics.setText(str(10))
		self.lineEdit_KineticCycleTime.setText(str(0.001))
		self.pushButton_SetAcquisitionProperties.clicked.connect(self._Acquisition)

		# GroupBox: Readout
		self.comboBox_OutputAmplificationModes = {"Conv./Extended NIR":1, "EM/Conv.":0}
		self.comboBox_HorizontalShiftSpeedModes = dict()
		for key, mode in self.comboBox_OutputAmplificationModes.items():
			for index, speed in self.camera.horizontal_shifting_speeds[mode].items():
				self.comboBox_HorizontalShiftSpeedModes.update({key+" ("+str(np.round(speed,2))+" MHz)":(mode, index)})
		[self.comboBox_HorizontalShiftSpeed.addItem(mode) for mode in self.comboBox_HorizontalShiftSpeedModes.keys()]
		self.comboBox_VerticalShiftSpeedModes = dict()
		for index, speed in self.camera.vertical_shifting_speeds.items():
			self.comboBox_VerticalShiftSpeedModes.update({str(np.round(speed,2))+" ms/pixel shift": index})
		[self.comboBox_VerticalShiftSpeed.addItem(mode) for mode in self.comboBox_VerticalShiftSpeedModes.keys()]
		self.pushButton_SetReadOut.clicked.connect(self._ReadOut)
		self.checkBox_FrameTransferMode.stateChanged.connect(self._ReadOut_FrameTransferMode)

		# GroupBox: CameraAcquisition
		self.canvas = MplCanvas(self, width=8, height=8, dpi=200)
		self.verticalLayout_CameraAcquisition.addWidget(self.canvas)
		self.data_queue = Queue()
		self.plotting_thread = PlottingThread(canvas=self.canvas, data_queue=self.data_queue, lineEdit_LostFrames=self.lineEdit_LostFrames)
		self.plotting_thread.start()
		self.acquisition_thread = AcquisitionThread(data_queue=self.data_queue, camera=self.camera)
		self.acquisition_thread.start()
		self.pushButton_StartAcquisition.clicked.connect(self._StartAcquisition)
		self.pushButton_StopAcquisition.clicked.connect(self._StopAcquisition)

		# GroupBox: Gain
		self.comboBox_PreAmpGainModes = dict()
		for index, gain in self.camera.preamp_gain_values.items():
			self.comboBox_PreAmpGainModes.update({str(np.round(gain,2))+"x": index})
		[self.comboBox_PreAmpGain.addItem(gain) for gain in self.comboBox_PreAmpGainModes.keys()]
		self.pushButton_SetGain.clicked.connect(self._Gain)
		self.checkBox_AllowHighEMGain.stateChanged.connect(self._Gain_AllowHighEMGain)
		FLAG, message, gain_info = self.camera.GetEMGainRange()
		self.lineEdit_EMCCDGainRange.setText(str(gain_info["lowest gain setting"])+"-"+str(gain_info["highest gain setting"]))
		self.lineEdit_EMCCDGain.setText(str(1))





	def _Exit_Camera(self):
		FLAG, message = self.camera.ShutDown(temperature=20)
		self.plotting_thread.RUNNING = False
		self.plotting_thread.wait()
		self.acquisition_thread.ACQUIRING = False
		self.acquisition_thread.RUNNING = False
		self.acquisition_thread.wait()
		sys.exit()

	def _Acquisition_Mode(self, mode):
		FLAG, message = self.camera.SetAcquisitionMode(mode=mode)
		[action.setChecked(False) for action in self.actions_Acquisition_Mode.values()]
		self.actions_Acquisition_Mode[mode].setChecked(True)

	def _Output_Amplifier_Mode(self, mode):
		FLAG, message = self.camera.SetOutputAmplifier(mode=mode)
		[action.setChecked(False) for action in self.actions_OutputAmplifier.values()]
		self.actions_OutputAmplifier[mode].setChecked(True)

	def _Readout_Mode(self, mode):
		FLAG, message = self.camera.SetReadMode(mode=mode)
		[action.setChecked(False) for action in self.actions_ReadoutMode.values()]
		self.actions_ReadoutMode[mode].setChecked(True)

	def _Trigger_Mode(self, mode):
		FLAG, message = self.camera.SetTriggerMode(mode=mode)
		[action.setChecked(False) for action in self.actions_TriggerMode.values()]
		self.actions_TriggerMode[mode].setChecked(True)

	def _Temperature(self):
		FLAG, message = self.camera.SetTemperature(temperature=int(self.lineEdit_TemperatureSetPoint.text()))
		FLAG, message = self.camera.CoolerON()
		FLAG, message, temperature = self.camera.StabilizeTemperature()	
		self.textBrowser_TemperatureReal.clear()
		self.textBrowser_TemperatureReal.append(str(temperature))

	def _Shutter_Mode(self):
		FLAG, message = self.camera.SetShutter(
			typ=self.comboBox_OutputTTLSignal_modes[self.comboBox_OutputTTLSignal.currentText()], 
			mode=self.comboBox_ShutterMode_modes[self.comboBox_ShutterMode.currentText()], 
			closingtime=int(self.lineEdit_ClosingTime.text()), 
			openingtime=int(self.lineEdit_OpeningTime.text()),)

	def _Image_Format(self):
		FLAG, message = self.camera.SetImage(
			hbin=int(self.lineEdit_HorizontalBinning.text()), 
			vbin=int(self.lineEdit_VerticalBinning.text()), 
			hstart=int(self.lineEdit_HorizontalStart.text()), 
			hend=int(self.lineEdit_HorizontalEnd.text()), 
			vstart=int(self.lineEdit_VerticalStart.text()), 
			vend=int(self.lineEdit_VerticalEnd.text()))

	def _Acquisition(self):
		FLAG, message = self.camera.SetExposureTime(float(self.lineEdit_ExposureTime.text()))
		FLAG, message = self.camera.SetAccumulationCycleTime(float(self.lineEdit_AccumulationCycleTime.text()))
		FLAG, message = self.camera.SetNumberAccumulations(int(self.lineEdit_NumberAccumulations.text()))
		FLAG, message = self.camera.SetNumberKinetics(int(self.lineEdit_NumberKinetics.text()))
		FLAG, message = self.camera.SetKineticCycleTime(float(self.lineEdit_KineticCycleTime.text()))

	def _ReadOut(self):
		FLAG, message = self.camera.SetHSSpeed(
			typ=self.comboBox_HorizontalShiftSpeedModes[self.comboBox_HorizontalShiftSpeed.currentText()][0], 
			index=self.comboBox_HorizontalShiftSpeedModes[self.comboBox_HorizontalShiftSpeed.currentText()][1])
		FLAG, message = self.camera.SetVSSpeed(index=self.comboBox_VerticalShiftSpeedModes[self.comboBox_VerticalShiftSpeed.currentText()])

	def _ReadOut_FrameTransferMode(self):
		FLAG, message = self.camera.SetFrameTransferMode(FRAME_TRANSFER_MODE=self.checkBox_FrameTransferMode.isChecked())
		if not FLAG:
			self.checkBox_FrameTransferMode.setChecked(not self.checkBox_FrameTransferMode.isChecked())

	def _Gain(self):
		FLAG, message = self.camera.SetPreAmpGain(index=self.comboBox_PreAmpGainModes[self.comboBox_PreAmpGain.currentText()])
		FLAG, message = self.camera.SetEMCCDGain(gain=int(self.lineEdit_EMCCDGain.text()))


	def _Gain_AllowHighEMGain(self):
		FLAG, message = self.camera.SetEMAdvanced(STATE=self.checkBox_AllowHighEMGain.isChecked())
		if not FLAG:
			self.checkBox_AllowHighEMGain.setChecked(not self.checkBox_AllowHighEMGain.isChecked())
		FLAG, message, gain_info = self.camera.GetEMGainRange()
		self.lineEdit_EMCCDGainRange.setText(str(gain_info["lowest gain setting"])+"-"+str(gain_info["highest gain setting"]))


	def _StartAcquisition(self):
		FLAG, message = self.camera.StartAcquisition()
		self.acquisition_thread.ACQUIRING = True

	def _StopAcquisition(self):
		self.acquisition_thread.ACQUIRING = False
		FLAG, message = self.camera.AbortAcquisition()


	







	def load_defaults(self):
		
		self._Acquisition_Mode(mode="single scan")
		self._Output_Amplifier_Mode(mode="CCD")
		self._Readout_Mode(mode="image")
		self._Trigger_Mode(mode="internal")
		self._Shutter_Mode()
		#self._Temperature()
		self._Image_Format()
		self._ReadOut()


















if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = EMCCD_frontend()
    ui.setupUi(MainWindow)
    ui.StartCameraSDK()
    ui.setup()
    ui.load_defaults()
    MainWindow.show()
    sys.exit(app.exec_())