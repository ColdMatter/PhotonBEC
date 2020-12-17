
'''

Class to control the USB 3 FLIR Cameras. It's written on top on the already existing FLIR's python 
wrapper PySpin, which uses the Spinnaker SDK. All the software necessary should be found on the Control
folder, on the Software subfolder. 

Written by: Joao Rodrigues
Date: October 2019

'''

import PySpin
import numpy as np 
import time




class CameraUSB3():

	lab_cameras = {'blackfly_minisetup': '19128822', 'blackfly_semiconductor_cavity': '17458446', 'blackfly_semiconductor_cavity_lock': '19441065'}

	def __init__(self, verbose=True, camera_id=None, timeout=1000, acquisition_mode='single frame'):

		'''
			Parameters:
				verbose (bool): 
				camera_id (str): check CameraUSB3.lab_cameras for implememted cameras
				timeout (int): number of miliseconds to wait for an image because timeout Exception is raised
				acquisition_mode (str): either 'single frame' (default) or 'continuous'

		'''

		self.camera_id = camera_id
		self.timeout = timeout
		self.cam_system = PySpin.System.GetInstance()
		self.cam_list = self.cam_system.GetCameras()

		num_cameras = self.cam_list.GetSize()
		self.acquisition_mode = acquisition_mode
		self.camera_running = None

		if num_cameras == 0:
			raise Exception('No USB3 cameras were detected')
		if camera_id is None:
			raise Exception('No camera serial number defined')

		if verbose is True:
			print('\n')
			print('-> Detected {0} USB3 cameras'.format(num_cameras))

		try:
			self.cam = self.cam_list.GetBySerial(serialNumber=self.lab_cameras[camera_id])
			self.cam.Init()
			self.nodemap = self.cam.GetNodeMap()
			self.s_node_map = self.cam.GetTLStreamNodeMap()
			#self.cam_initiated_flag = True
		except:
			raise Exception('\n\n Could not initiate camera: '+camera_id)

		try:
			self._set_acquisition_mode(acquisition_mode=self.acquisition_mode)
		except Exception as e:
			print(e)
			raise Exception('Could not defined acquisition mode')


	def _set_acquisition_mode(self, acquisition_mode):
		''' 
			Sets the acquisition mode.
			Implemented modes are 'single frame' and 'continuous'

		'''

		##### Sets the acquisition mode
		node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
		if PySpin.IsAvailable(node_acquisition_mode) and PySpin.IsWritable(node_acquisition_mode):
			if acquisition_mode == 'single frame':
				acquisition_mode_code = PySpin.CEnumEntryPtr(node_acquisition_mode.GetEntryByName('SingleFrame'))
			elif acquisition_mode == 'continuous':
				acquisition_mode_code = PySpin.CEnumEntryPtr(node_acquisition_mode.GetEntryByName('Continuous'))
			else:
				self.close()
				raise Exception('Unknown acquisition mode')

			if PySpin.IsAvailable(acquisition_mode_code) and PySpin.IsReadable(acquisition_mode_code):
				frame_mode_integer_code = acquisition_mode_code.GetValue()
				node_acquisition_mode.SetIntValue(frame_mode_integer_code)
				if acquisition_mode == 'single frame':
					self.acquisition_mode = acquisition_mode
				elif acquisition_mode == 'continuous':
					self.acquisition_mode = 'continuous'
				else:
					raise Exception()
			else:
				self.close()
				raise Exception('Error in setting acquisition mode')

		##### In the case of "continuous mode", set buffer handling to "newest first"
		if acquisition_mode == 'continuous':
			handling_mode = PySpin.CEnumerationPtr(self.s_node_map.GetNode('StreamBufferHandlingMode'))
			if PySpin.IsAvailable(handling_mode) and PySpin.IsWritable(handling_mode):
				handling_mode_entry = handling_mode.GetEntryByName('NewestOnly')
				handling_mode.SetIntValue(handling_mode_entry.GetValue())
			else:
				self.close()
				raise Exception('Error in setting buffer mode')			


	def begin_acquisition(self):
		self.cam.BeginAcquisition()
		self.camera_running = True


	def end_acquisition(self):
		self.cam.EndAcquisition()
		self.camera_running = False


	def get_image(self):
		''' 
			Returs a numpy array frame.
			Single frame mode is very slow. For faster frame rates one should use the "continuous" mode

		'''

		if self.acquisition_mode == 'single frame':
			self.begin_acquisition()
			frame_incomplete = True
			while frame_incomplete:
				try:
					frame = self.cam.GetNextImage(self.timeout)
				except Exception as e:
					self.cam.EndAcquisition()
					self.close()
					print("Timeout exceed waiting for an image. Probably error in communicating with camera. ")
					raise e
				frame_incomplete = frame.IsIncomplete()
			frame_array = frame.GetNDArray()
			frame.Release()
			self.end_acquisition()
			return frame_array

		elif self.acquisition_mode == 'continuous':
			frame_incomplete = True
			while frame_incomplete:
				try:
					frame = self.cam.GetNextImage(self.timeout)
				except Exception as e:
					self.cam.EndAcquisition()
					self.close()
					print("Timeout exceed waiting for an image. Probably error in communicating with camera. ")
					raise e
				frame_incomplete = frame.IsIncomplete()
			frame_array = frame.GetNDArray()
			frame.Release()
			return frame_array


	def close(self):
		''' Closes the connection with the camera. Python usually stops if the camera connection is not closed. '''
		if self.camera_running is True:
			self.end_acquisition()
		self.cam.DeInit()
		del self.cam
		self.cam_list.Clear(); 
		self.cam_system.ReleaseInstance()