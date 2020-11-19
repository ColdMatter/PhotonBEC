'''
	Written by Joao Rodrigues
	November 2020
'''


import numpy as np
import copy
import ctypes
import socket
import time


########## Parameters
if socket.gethostname() == "ph-photonbec5":
	dll_device_manager=r'D:\Control\KCubeController\Thorlabs.MotionControl.DeviceManager.dll'
	dll_KCube=r'D:\Control\KCubeController\Thorlabs.MotionControl.KCube.InertialMotor.dll'
	serial_number=97000001


class KCubeController():

	kcube_return_codes=dict()
	kcube_return_codes.update({0: 'FT_OK'})
	kcube_return_codes.update({1: 'FT_InvalidHandle'})
	kcube_return_codes.update({2: 'FT_DeviceNotFound'})
	kcube_return_codes.update({3: 'FT_DeviceNotOpened'})
	kcube_return_codes.update({4: 'FT_IOError'})
	kcube_return_codes.update({5: 'FT_InsufficientResources'})
	kcube_return_codes.update({6: 'FT_InvalidParameter'})
	kcube_return_codes.update({7: 'FT_DeviceNotPresent'})
	kcube_return_codes.update({8: 'FT_IncorrectDevice'})
	kcube_return_codes.update({16: 'FT_NoDLLLoaded'})
	kcube_return_codes.update({17: 'FT_NoFunctionsAvailable'})
	kcube_return_codes.update({18: 'FT_FunctionNotAvailable'})
	kcube_return_codes.update({19: 'FT_BadFunctionPointer'})
	kcube_return_codes.update({20: 'FT_GenericFunctionFail'})
	kcube_return_codes.update({21: 'FT_SpecificFunctionFail'})
	kcube_return_codes.update({32: 'TL_ALREADY_OPEN'})
	kcube_return_codes.update({33: 'TL_NO_RESPONSE'})
	kcube_return_codes.update({34: 'TL_NOT_IMPLEMENTED'})
	kcube_return_codes.update({35: 'TL_FAULT_REPORTED'})
	kcube_return_codes.update({36: 'TL_INVALID_OPERATION'})
	kcube_return_codes.update({40: 'TL_DISCONNECTING'})
	kcube_return_codes.update({41: 'TL_FIRMWARE_BUG'})
	kcube_return_codes.update({42: 'TL_INITIALIZATION_FAILURE'})
	kcube_return_codes.update({43: 'TL_INVALID_CHANNEL'})
	kcube_return_codes.update({37: 'TL_UNHOMED'})
	kcube_return_codes.update({38: 'TL_INVALID_POSITION'})
	kcube_return_codes.update({39: 'TL_INVALID_VELOCITY_PARAMETER'})
	kcube_return_codes.update({44: 'TL_CANNOT_HOME_DEVICE'})
	kcube_return_codes.update({45: 'TL_JOG_CONTINOUS_MODE'})
	kcube_return_codes.update({46: 'TL_NO_MOTOR_INFO'})
	kcube_return_codes.update({47: 'TL_CMD_TEMP_UNAVAILABLE'})


	def __init__(self, VERBOSE=True, SIMULATION=False, serial_number=serial_number):
		self.VERBOSE=VERBOSE
		self.SIMULATION=SIMULATION
		self.serial_number=ctypes.c_char_p(str(serial_number).encode())

		# Loads the dlls
		self.dll_device_manager = ctypes.WinDLL(dll_device_manager)
		self.dll_KCube = ctypes.WinDLL(dll_KCube)

		# Initializes the device
		if self.SIMULATION:
			self.printout(message="Entering simulation mode")
			self.dll_KCube.TLI_InitializeSimulations()

		out=self.dll_KCube.TLI_BuildDeviceList()
		self.printout(code=out)

		out=self.dll_KCube.TLI_GetDeviceListSize()
		self.printout(message="{0} devices found".format(out))

		out=self.dll_KCube.KIM_Open(self.serial_number)
		self.printout(message="Opening devide", code=out)

		out=self.dll_KCube.KIM_Enable(self.serial_number)
		self.printout(message="Enabling devide", code=out)

		#out=self.dll_KCube.KIM_StartPolling(self.serial_number, ctypes.c_int(250))
		#self.printout(message="Start Polling: "+str(bool(out)))



	def printout(self, code=None, message=None):

		if self.VERBOSE:
			if not message is None:
				print("KCube object: "+message)
			if not code is None:
				print("KCube object: "+self.kcube_return_codes[code])


	def close(self):
		self.dll_KCube.KIM_Close(self.serial_number)
		if self.SIMULATION:
			self.printout(message="Exitig sumalation mode")
			self.dll_KCube.TLI_UninitializeSimulations()


	def get_current_position(self, channel=1):
		#### This seems not to be able to get the actual position, not sure why
		out=self.dll_KCube.KIM_GetCurrentPosition(self.serial_number, ctypes.c_int(channel))
		self.printout(message="Current position (channel {0}): ".format(channel)+str(out))
		return out


	def move_jog(self, channel=1, direction='forward'):
		direction_code={'backward':0, 'forward':1}
		SUCCESS=False
		if direction not in direction_code.keys():
			raise Exception("Invalid direction")
		else:
			self.printout(message="Moving jog "+direction)
			out=self.dll_KCube.KIM_MoveJog(self.serial_number, ctypes.c_int(channel), ctypes.c_int(direction_code[direction]))
			self.printout(code=out)
			if out==0:
				SUCCESS=True
		return SUCCESS


	def move_to_position(self, channel=1, position=0):
		SUCCESS=False
		self.printout(message="Moving channel {0} to position {1}".format(channel, position))
		out=self.dll_KCube.KIM_MoveAbsolute(self.serial_number, ctypes.c_int(channel), ctypes.c_int(position))
		self.printout(code=out)
		if out==0:
			SUCCESS=True
		return SUCCESS		

