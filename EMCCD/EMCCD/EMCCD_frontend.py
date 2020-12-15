'''
	Written by:		Joao Rodrigues
	Last Update: 	October 16th 2020

'''

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import copy
import numpy as np
from matplotlib.ticker import NullFormatter
from functools import partial
import time
from datetime import datetime
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from queue import Queue

from EMCCD_frontend_GUI import Ui_MainWindow
from EMCCD_backend import EMCCD
from EMCCD_frontend_CameraWindow_GUI import Ui_CameraWindow


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, initiate_axis=True):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if initiate_axis:
            self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)




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
				time.sleep(0.001)
			time.sleep(0.01)
			
	def acquisition(self):
		FLAG, message, info = self.camera.GetStatus(VERBOSE=False)
		if info == "DRV_IDLE" or info == "DRV_ACQUIRING":
			if info == "DRV_IDLE":
				self.ACQUIRING = False
			FLAG, message, image = self.camera.GetAcquiredData(VERBOSE=False)
			if type(image)==np.ndarray:
				#image = image - np.min(image)
				#image = image / np.max(image)
				image = np.flip(image, axis=0)
				self.data_queue.put(image)
			




class PlottingThread(QtCore.QThread):
	def __init__(self, canvas, data_queue, lineEdit_LostFrames, signal_min, signal_max):
		super(PlottingThread, self).__init__()
		self.canvas_big = None
		self.canvas_hist = None
		self.RUNNING = True
		self.data_queue = data_queue
		self.canvas = canvas
		self.lineEdit_LostFrames = lineEdit_LostFrames
		self.signal_min = signal_min 
		self.signal_max = signal_max
		self.canvas.axes.set_xticks([])
		self.canvas.axes.set_yticks([])
		self.canvas.show()
		self.image = self.canvas.axes.imshow(np.zeros([512,512]), cmap='gray')
		self.lost_frames = 0

	def get_timestamp(self):
		now = datetime.now()
		timestamp = ''.join([str(element) for element in [now.year, now.month, now.day, '_', now.hour, now.minute, now.second]]) 
		return timestamp

	def save_plot(self):
		filename = 'EMCCD'+self.get_timestamp()+'.png'
		self.canvas.fig.savefig(filename)

	def set_cmap_lim(self, cmin, cmax):
		self.cmin = cmin
		self.cmax = cmax

	def load_canvas_big(self, canvas_big):
		self.canvas_big = canvas_big
		self.canvas_big.axes.set_xticks([])
		self.canvas_big.axes.set_yticks([])
		self.image_big = self.canvas_big.axes.imshow(np.zeros([512,512]), cmap='gray')

	def load_canvas_hist(self, canvas_hist):
		self.canvas_hist = canvas_hist


		# Define the locations for the axes
		left, width = 0.12, 0.55
		bottom, height = 0.12, 0.55
		bottom_h = left_h = left+width+0.02
		 
		# Set up the geometry of the three plots
		rect_temperature = [left, bottom, width, height] # dimensions of temp plot
		rect_histx = [left, bottom_h, width, 0.25] # dimensions of x-histogram
		rect_histy = [left_h, bottom, 0.25, height] # dimensions of y-histogram

		self.hist_image = self.canvas_hist.fig.add_axes(rect_temperature) # temperature plot
		self.hist_hx = self.canvas_hist.fig.add_axes(rect_histx) # x histogram
		self.hist_hy = self.canvas_hist.fig.add_axes(rect_histy) # y histogram
		self.hist_hy.set_xscale("log")

		nullfmt = NullFormatter()
		self.hist_hx.xaxis.set_major_formatter(nullfmt)
		self.hist_hy.yaxis.set_major_formatter(nullfmt)

		aux_all_axes = [self.hist_image, self.hist_hx, self.hist_hy]
		[axis.set_xticks([]) for axis in aux_all_axes]
		[axis.set_yticks([]) for axis in aux_all_axes]


	def run(self):
		self.lineEdit_LostFrames.setText(str(self.lost_frames))
		while self.RUNNING:
			self.plot()
			time.sleep(0.001)
		self.quit()

	def plot(self):
		if not self.data_queue.empty():
			# Gets data
			data = self.data_queue.get()
			self.signal_min.setText(str(np.min(data)))
			self.signal_max.setText(str(np.max(data)))
			while not self.data_queue.empty():
				dummy = self.data_queue.get()
				self.lost_frames += 1
				self.lineEdit_LostFrames.setText(str(self.lost_frames))

			# Plots in the main app window
			self.image.set_data(data)
			self.image.set_clim([self.cmin, self.cmax])			

			# plots in the big undocked window
			if not self.canvas_big is None:
				self.image_big.set_data(data)
				self.image_big.set_clim([self.cmin, self.cmax])
			
			# plots in the histogram undocked window
			if not self.canvas_hist is None:
				if not hasattr(self, "image_hist_main"):
					self.image_hist_main = self.hist_image.imshow(data, cmap='gray')
					self.image_hist_x, = self.hist_hx.plot(np.sum(data, 0), color=(1.0,0.50,0.50), linewidth=0.5)
					self.image_hist_y, = self.hist_hy.plot(np.flip(np.sum(data, 1)), np.arange(data.shape[0]), color=(1.0,0.50,0.50), linewidth=0.5)
				else:
					self.image_hist_main.set_data(data)
					self.image_hist_main.set_clim([self.cmin, self.cmax])
					self.image_hist_x.set_ydata(np.sum(data, 0))
					self.hist_hx.relim()
					self.hist_hx.autoscale_view()
					self.image_hist_y.set_xdata(np.flip(np.sum(data, 1)))
					self.hist_hy.relim()
					self.hist_hy.autoscale_view()

			# Updates all plots
			self.canvas.draw()
			if not self.canvas_big is None:
				self.canvas_big.draw()
			if not self.canvas_hist is None:
				self.canvas_hist.draw()



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
		self.plotting_thread = PlottingThread(
			canvas=self.canvas, 
			data_queue=self.data_queue, 
			lineEdit_LostFrames=self.lineEdit_LostFrames,
			signal_min=self.lineEdit_signal_min,
			signal_max=self.lineEdit_signal_max)
		self.plotting_thread.start()
		self.acquisition_thread = AcquisitionThread(data_queue=self.data_queue, camera=self.camera)
		self.acquisition_thread.start()
		self.pushButton_StartAcquisition.clicked.connect(self._StartAcquisition)
		self.pushButton_StopAcquisition.clicked.connect(self._StopAcquisition)
		self.pushButton_Undock.clicked.connect(self._Undock)

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

		# GroupBox Plotting
		self.lineEdit_cmap_min.setText(str(0))
		self.lineEdit_cmap_max.setText(str(1))
		self.pushButton_PlottingSet.clicked.connect(self._PlottingSet)
		self.pushButton_Hist.clicked.connect(self._Hist)
		self.pushButton_SavePlot.clicked.connect(self._SavePlot)


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

	def _Undock(self):
		self.SecondWindow = QtWidgets.QMainWindow()
		self.camerawindown = Ui_CameraWindow()
		self.camerawindown.setupUi(self.SecondWindow)

		self.canvas_big = MplCanvas(self, width=8, height=8, dpi=200)
		self.camerawindown.gridLayout.addWidget(self.canvas_big)
		self.plotting_thread.load_canvas_big(canvas_big=self.canvas_big)
		self.SecondWindow.show()

	def _PlottingSet(self):
		cmin = float(self.lineEdit_cmap_min.text())
		cmax = float(self.lineEdit_cmap_max.text())
		self.plotting_thread.set_cmap_lim(cmin, cmax)

	def _Hist(self):
		self.ThirdWindow = QtWidgets.QMainWindow()
		self.histwindown = Ui_CameraWindow()
		self.histwindown.setupUi(self.ThirdWindow)

		self.canvas_hist = MplCanvas(self, width=8, height=8, dpi=200, initiate_axis=False)
		self.histwindown.gridLayout.addWidget(self.canvas_hist)
		self.plotting_thread.load_canvas_hist(canvas_hist=self.canvas_hist)
		self.ThirdWindow.show()	

	def _SavePlot(self):
		self.plotting_thread.save_plot()




	def load_defaults(self):
		
		self._Acquisition_Mode(mode="run till abort")
		# Vertical read speed
		#self.comboBox_VerticalShiftSpeed.setText(self.comboBox_VerticalShiftSpeedModes.keys()[1])
		self.comboBox_VerticalShiftSpeed.setCurrentIndex(3)
		self._Shutter_Mode()
		# Other defaults
		self._Output_Amplifier_Mode(mode="CCD")
		self._Readout_Mode(mode="image")
		self._Trigger_Mode(mode="internal")
		self._Shutter_Mode()
		#self._Temperature()
		self._Image_Format()
		self._ReadOut()
		self._PlottingSet()


















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