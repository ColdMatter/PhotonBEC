#execfile("int_images.py")
#this image collection file was for experiments on 20140901 looking at temporal coherence of LED
#ie taking fringe data at different piezo base voltages

import os
import time
from int_functions import *
from random import shuffle

cameraLabel = "int_chameleon"
coarse_position = 13.75
num_steps = 30
voltage_step = 0.25
base_voltage = 60

piezo_base = linspace(0,65,27)
#for standard deviation measurement:
for i in range(0,4):
	piezo_base = append(piezo_base,(linspace(0,65,27)))

turns = 0
shuffle(piezo_base)
for pb in piezo_base:
	#dump = raw_input("Please turn the window " + str(t) + " turns and press return. Positive is INWARD.")
	#for standard deviation take multiple measurements
	voltage_image(cameraLabel,coarse_position,pb,voltage_step,num_steps,turns)
	time.sleep(0.5)
'''
#lets do the whole raaaaange
coarse_positions = linspace(8,20,13)
#randomize order!
shuffle(coarse_positions)
for cp in coarse_positions:
	os.system("echo " + str(round(cp,4)) + " | clip")
	dump = raw_input("Please set coarse position to "+str(cp)+" mm, and then press return")
	voltage_image(cameraLabel,cp,base_voltage,voltage_step,num_steps,piezo,saving,take_images)
'''