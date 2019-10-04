import numpy as np
import matplotlib.pyplot as plt
from time import sleep
from scipy.optimize import curve_fit


def compute_locking_signal(images_mean, main_pca_component, normalization_factor, current_image):

	current_image = np.squeeze(current_image[:,:,0])
	current_image_centered = np.reshape(current_image, [current_image.shape[0]*current_image.shape[1]]) - images_mean
	projection = np.dot(current_image_centered, main_pca_component) / normalization_factor

	return projection