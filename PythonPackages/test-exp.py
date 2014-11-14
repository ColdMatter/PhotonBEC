
import pbec_experiment
from scipy.misc import imsave

cam = pbec_experiment.getCameraByLabel("chameleon")
cam.setup()

cam.set_max_region_of_interest()
im2 = cam.get_image()
imsave("large.png", im2)

for i in range(5):
	cam.set_centered_region_of_interest((i+2)*100, (i+2)*100)
	im1 = cam.get_image()
	imsave("small" + str(i) + ".png", im1)

cam.close()