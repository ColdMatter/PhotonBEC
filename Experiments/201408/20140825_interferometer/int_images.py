#execfile("int_images.py")
import os
import time
from int_functions import *
from random import shuffle

cameraLabel = "int_chameleon"
coarse_position = 13.75
num_steps = 30
voltage_step = 0.25
base_voltage = 60

#piezo = True
#saving = True
#take_images = True

#testing standard deviation
#piezo_base = linspace(42,48,13)
#piezo_base = ones(5)
#piezo_base = 35*piezo_base

turns = linspace(5.25,7.25,9)
#turns = [3.5, 3.0, 5.5, 6.0]

shuffle(turns)
for t in turns:
	dump = raw_input("Please turn the window " + str(t) + " turns and press return. Positive is INWARD.")
	#for standard deviation take multiple measurements
	for i in range(0,5):
		voltage_image(cameraLabel,coarse_position,base_voltage,voltage_step,num_steps,t)
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