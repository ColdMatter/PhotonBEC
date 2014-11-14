#execfile("int_images.py")
import os
from int_functions import *
from random import shuffle
cameraLabel = "int_chameleon"
num_steps = 30
voltage_step = 0.1
base_voltage = 30

piezo = True
saving = True
take_images = True

#lets do the whole raaaaange
coarse_positions = linspace(8,20,13)
#randomize order!
shuffle(coarse_positions)
for cp in coarse_positions:
	os.system("echo " + str(round(cp,4)) + " | clip")
	dump = raw_input("Please set coarse position to "+str(cp)+" mm, and then press return")
	voltage_image(cameraLabel,cp,base_voltage,voltage_step,num_steps,piezo,saving,take_images)