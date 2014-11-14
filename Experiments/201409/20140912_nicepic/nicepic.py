#number_of_cycles=1; name_extra=None;execfile("measure_beam_size.py")
#name_extra being non-None means it will save the image to a file

sys.path.append("D:\\Control\\PythonPackages\\")

from pbec_analysis import *
from pbec_experiment import get_single_image
from pbec_experiment import camera_pixel_size_map
from scipy.misc import imsave

number_of_cycles = int(raw_input("number of cycles[1] :") or 1)
camera_name = raw_input("camera name[chameleon] :") or "chameleon"

for i in range(number_of_cycles):
	ts = make_timestamp()
	im_raw = get_single_image(camera_name)
	
	ex = Experiment(ts)
	ex.setCameraData(im_raw)
	ex.meta.comments = "Measured beam size"
	ex.saveAllData()
	sys.stdout.write("\x07") #beep

#EoF
