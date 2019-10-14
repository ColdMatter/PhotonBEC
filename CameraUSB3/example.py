from CameraUSB3 import CameraUSB3
import PySpin
import matplotlib.pyplot as plt
import time
import numpy as np
from scipy.misc import imsave

camera_id = 'blackfly_minisetup'





######################### Gets a single frame
'''
camera = CameraUSB3(verbose=True, camera_id=camera_id, timeout=1000, acquisition_mode='single frame')
frame = camera.get_image()
'''


######################### Tests frame acquisition rate in single frame mode
'''
camera = CameraUSB3(verbose=True, camera_id=camera_id, timeout=1000, acquisition_mode='single frame')
print('\n\nTesting camera acquisition rate:')
n_frames = 100
frames = list()
times = list()
for i in range(0, n_frames):
	print('    -> Getting frame {0} out of {1}'.format(i, n_frames))
	times.append(time.time())
	frames.append(camera.get_image())
times = np.array(times)
delta_t = times[1:] - times[:-1]
delta_t_average = np.average(delta_t)
frame_rate = 1.0 / delta_t_average
print('\n Average acquisition rate is {0} frames/s\n\n'.format(int(frame_rate)))
'''


######################### Acquires different frames but working "continuous mode"
'''
camera = CameraUSB3(verbose=True, camera_id=camera_id, timeout=1000, acquisition_mode='continuous')
camera.begin_acquisition()
frame = camera.get_image()
camera.end_acquisition()
'''


######################### Tests frame acquisition rate in continuous mode

camera = CameraUSB3(verbose=True, camera_id=camera_id, timeout=1000, acquisition_mode='continuous')
print('\n\nTesting camera acquisition rate:')
n_frames = 100
frames = list()
times = list()
camera.begin_acquisition()
for i in range(0, n_frames):
	print('    -> Getting frame {0} out of {1}'.format(i, n_frames))
	times.append(time.time())
	frames.append(camera.get_image())
camera.end_acquisition()
times = np.array(times)
delta_t = times[1:] - times[:-1]
delta_t_average = np.average(delta_t)
frame_rate = 1.0 / delta_t_average
print('\n Average acquisition rate is {0} frames/s\n\n'.format(int(frame_rate)))







camera.close()

