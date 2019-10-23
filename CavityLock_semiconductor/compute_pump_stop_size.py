import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy.optimize import curve_fit
import socket
if socket.gethostname() == 'ph-photonbec3':
	sys.path.append("Y:\\Control\\CameraUSB3\\")
	sys.path.append("Y:\\Control\\PythonPackages\\")
	sys.path.append("Y:\\Control\CavityLock")
from pbec_analysis import *
import pbec_experiment
from CameraUSB3 import CameraUSB3

########## Parameters
ROI_half_size = 150
camera_label = "blackfly_semiconductor_cavity"
calibration = {'pixel size (um)': 3.75, 'objective focal length (mm)': 35, 'camera focal length (mm)': 200}



########## Gets camera and configures it
cam = CameraUSB3(verbose=True, camera_id=camera_label, timeout=1000, acquisition_mode='single frame')
# gets frame
camera_frame = cam.get_image()
# gets ROI
x = np.arange(0, camera_frame.shape[1], 1)
y = np.arange(0, camera_frame.shape[0], 1)
centroid_x = np.where(camera_frame == np.amax(camera_frame))[1][0]
centroid_y = np.where(camera_frame == np.amax(camera_frame))[0][0]
camera_frame = camera_frame[centroid_y-ROI_half_size:centroid_y+ROI_half_size, centroid_x-ROI_half_size:centroid_x+ROI_half_size]
camera_frame = camera_frame / np.max(camera_frame)
#
#
#
#
#
pixel_calibration = calibration['pixel size (um)'] / (calibration['camera focal length (mm)'] / calibration['objective focal length (mm)'])



########## Fits Gaussian

def twoD_Gaussian((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
	a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
	b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
	c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
	g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))
	return g.ravel()

x = np.arange(0, 2*ROI_half_size, 1)
y = np.arange(0, 2*ROI_half_size, 1)
centre_x = pixel_calibration*np.where(camera_frame == np.amax(camera_frame))[1][0]
centre_y = pixel_calibration*np.where(camera_frame == np.amax(camera_frame))[0][0]
x,y = np.meshgrid(x, y); x = x*pixel_calibration; y = y*pixel_calibration
print('\n\nMaximum intensity pixel was found to be at: ')
print(int(centre_x), int(centre_y))

initial_guess = (1, centre_x, centre_y, 50, 50, 0, 0)
camera_frame_for_fit = 1.0*camera_frame
camera_frame_for_fit[np.where(camera_frame_for_fit<0.5)] = 0
popt, pcov = curve_fit(twoD_Gaussian, (x, y), camera_frame_for_fit.ravel(), p0=initial_guess)
camera_frame_fitted = twoD_Gaussian((x, y), *popt)
camera_frame_fitted = np.reshape(camera_frame_fitted, camera_frame.shape)
print('\n\nOptimum parameters are:')
print(popt)

ts = make_timestamp()
ts = ts.split('_')[0]+'\_'+ts.split('_')[1]
rc('text', usetex=True)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 4))
ax1.imshow(camera_frame, cmap=plt.cm.jet, origin='bottom', extent=(x.min(), x.max(), y.min(), y.max()))
ax1.set_xlabel('x ($\mu$m)')
ax1.set_ylabel('y ($\mu$m)')
ax2.imshow(camera_frame_fitted, cmap=plt.cm.jet, origin='bottom', extent=(x.min(), x.max(), y.min(), y.max()))
ax2.set_xlabel('x ($\mu$m)')
fig.suptitle(r'Pump spot size is: $2\sigma_x=$'+str(int(2*np.abs(popt[3])))+'$\mu$m, $2\sigma_y=$'+str(int(2*np.abs(popt[4])))+'$\mu$m, at '+ts)
fig.tight_layout()
plt.show()

cam.close()