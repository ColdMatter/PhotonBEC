from __future__ import division
from pbec_data_format import *
from pbec_experiment import *
from pbec_analysis import *
from scipy.optimize import curve_fit
from ThorlabsMDT69xA import *
import time
import zipfile
import os
#might not need this import statement
from os.path import basename

#takes first timestamp (or any timestamp) and allows user to determine image analysis window for that image set
#returns coordinates x_min, x_max, y_min, y_max
def image_window(ts):
	zip_fn = timestamp_to_filename(ts,file_end=".zip",make_folder = False)
	img_zip = zipfile.ZipFile(zip_fn,"r")
	#not sure how to do this without creating a folder to extract to...
	img_folder = timestamp_to_filename(ts,file_end="",make_folder=False)
	if not os.path.exists(img_folder): 
		os.makedirs(img_folder)
	img_zip.extractall(img_folder)#
	#this is a hacky way to just look at the first image in the zip file
	i=0
	for file in os.listdir(img_folder):
		if i==0:
			img_fn = img_folder+folder_separator+file
			img = imread(img_fn)
			i=i+1
		else:
			break
	imshow(img)
	dump = raw_input("Please zoom the image into the analysis window you would like and press return")
	x_max, x_min = ylim()
	y_min, y_max = xlim()
	close("all")
	#delete images from temporary folder then delete the folder
	for file in os.listdir(img_folder):
		img_fn = img_folder+folder_separator+file
		os.remove(img_fn)
	os.rmdir(img_folder)
	
	return int(ceil(x_min)), int(ceil(x_max)), int(ceil(y_min)), int(ceil(y_max))

#takes timestamp_to_analyze, image analysis window coordinates and visibility analysis method as variables
#returns array of visibilities for each pixel depending on which analysis method is chosen
def visibility_images(timestamp_to_analyze,y_min,y_max,x_min,x_max,analysis_method):

	maxMinVis = False
	rmsVis = False
	fitVis = False
	
	#analysis methods
	if analysis_method == "maxMinVis":
		maxMinVis = True
	if analysis_method == "rmsVis":
		rmsVis = True
	if analysis_method == "fitVis":
		fitVis = True

	#get zip filename from timestamp
	zip_fn = timestamp_to_filename(timestamp_to_analyze,file_end=".zip",make_folder = False)

	#open zipfile and extract to temporary folder
	img_zip = zipfile.ZipFile(zip_fn,"r")
	img_folder = timestamp_to_filename(timestamp_to_analyze,file_end="",make_folder=False)

	if not os.path.exists(img_folder): 
		os.makedirs(img_folder)
	img_zip.extractall(img_folder)

	#find number of images in folder
	n = size(os.listdir(img_folder))

	#initialize image array
	img_arr = empty((x_max-x_min,y_max-y_min,n))

	#load all image files into image array and test pixel array
	i=0
	for file in os.listdir(img_folder):
		img_fn = img_folder+folder_separator+file
		img = imread(img_fn)
		#img_arr = dstack((img_arr,img[x_min:x_max,y_min:y_max,1]))
		img_arr[:,:,i] = img[x_min:x_max,y_min:y_max,1]
		i=i+1

	#find rms visibility
	if rmsVis:
		#find rms value of fringes for each pixel
		rms_arr = std(img_arr,2)
		#numerator is sqrt(2)*rms
		num_arr = sqrt(2)*rms_arr
		#denominator is just mean (y0 effectively)
		den_arr = mean(img_arr,2)
		
	#find curve fit visibility by looping through pixels to fit along dimension
	#could maybe use apply_along_axis? don't think so, curve_fit returns too many dimensions
	if fitVis:
		#initialize arrays
		a_arr = zeros((x_max-x_min,y_max-y_min))
		y0_arr = zeros((x_max-x_min,y_max-y_min))
		a_sdev_arr = zeros((x_max-x_min,y_max-y_min))
		y0_sdev_arr = zeros((x_max-x_min,y_max-y_min))
		
		x = np.linspace(0,n-1,n)
		
		#sine fitting function
		def sinfunc(x,a,b,c,d):
			return a*sin(b*x-c)+d
		#initial guess
		guess = array([100, 0.5, 3, 50]) #amplitude, frequency, phase, offset guesses
		#test guesses
		#y_fit = guess[0]*np.sin(guess[1]*x-guess[2])+guess[3]
		#plot(x,y_fit,'r-')		
	
		#find maximum for ignoring any pixels with no light
		max_arr = amax(img_arr,2)
		for j in range(0,y_max-y_min-1):
			for i in range(0,x_max-x_min-1):
				if max_arr[i,j] != 0:
					y = img_arr[i,j,:]
					fitpars, covmat = curve_fit(sinfunc, x, y, p0=guess)
					a_arr[i,j] = fitpars[0]
					y0_arr[i,j] = fitpars[3]
					variances = covmat.diagonal()
					std_devs = np.sqrt(variances)
					a_sdev_arr[i,j] = std_devs[0]
					y0_sdev_arr[i,j] = std_devs[3]
				else:
					a_arr[i,j] = 0
					y0_arr[i,j] = 0
				if j == test_y-y_min:
					if i == test_x-x_min:
						#show test pixel fit
						plot(x,sinfunc(x,fitpars[0],fitpars[1],fitpars[2],fitpars[3]),'r-')
		num_arr = abs(a_arr)
		den_arr = y0_arr

	#calculate max and min for visibility
	if maxMinVis:
		num_arr = max_arr - amin(img_arr,2)
		den_arr = max_arr + amin(img_arr,2)

	#calculate visibility
	vis_arr = num_arr/den_arr

	#options to ignore visibilities greater than one and avoid dividing by zero
	for j in range(0,y_max-y_min-1):
		for i in range(0,x_max-x_min-1):
			#if vis_arr[i,j] > 1:
				#vis_arr[i,j] = 0
			if den_arr[i,j] == 0:
				vis_arr[i,j] = 0

	#delete images from temporary folder then delete the folder
	for file in os.listdir(img_folder):
		img_fn = img_folder+folder_separator+file
		os.remove(img_fn)
	os.rmdir(img_folder)

	return vis_arr

#takes camera label, coarse position, base piezo voltage, piezo voltage step size and number of steps as variables
#increments piezo voltage and gets image from camera, saving to zip archive in appropriate data folder
def voltage_image(cameraLabel,coarse_position,base_voltage,voltage_step,num_steps,piezo,saving,take_images):
	timestamp = make_timestamp()
	
	if piezo:
		pzt = ThorlabsMDT69xA()
		
	if saving:
		meta = MetaData(timestamp)
		zip_fn = timestamp_to_filename(timestamp,file_end=".zip",make_folder = True)
		img_zip = zipfile.ZipFile(zip_fn,'w',)

		#save coarse position (mm) in metadata
		meta.parameters.update({"coarse_position":coarse_position})

	#initialize arrays
	xvs = []

	#open camera
	if take_images:
		#max number of crap images to ignore
		max_number_of_tries = 5
		c = getCameraByLabel(cameraLabel)
		c.setup()

	#set voltage, take image n times
	if piezo:
		pzt.setXvolts(base_voltage)
	for i in range(0,num_steps):
		xvs.append(base_voltage + voltage_step*i)
		if piezo:
			pzt.setXvolts(xvs[-1])
		#might not need this, just in case
		if saving:
			meta.parameters.update({"xvs":xvs})
		#might not need this much time
		time.sleep(0.1)
		if take_images: 
			img = c.get_image()
			count=0
			while (c.error != None) & (count < max_number_of_tries):
				count +=1
				print "Camera error: "+str(c.error)
				print "Trying again for the "+str(count)+"th time"
				img = c.get_image()
		else: 
			img=ones((10,10))
		if saving:
			#makes 02 for 2nd image, for example
			fe = "_im"+str(100+i)[-2:]+".jpg"
			fn = timestamp_to_filename(timestamp,file_end=fe,make_folder = False)
			#save image, write to zipfile, then remove the image file
			imsave(fn,img)
			img_zip.write(fn,basename(fn))
			os.remove(fn)
		#time.sleep(0.5)
	
	if saving:
		#save metadata, close zip archive, close camera, close piezo
		meta.save()
		img_zip.close()
	if take_images:
		c.close()
	if piezo:
		pzt.ser.close()

#takes range of timestamps to analyze, image analysis window coordinates and fit parameter guesses
#returns array of coherence lengths for each pixel
def coherence_length(first_ts,last_ts,x_min,x_max,y_min,y_max,guess):
	
	ts_list = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
	n = size(ts_list)
	
	#keep this hard coded for now
	analysis_method = "rmsVis"

	#initialize arrays
	vis_map = empty((x_max-x_min,y_max-y_min,n))
	coh_length = empty((x_max-x_min,y_max-y_min))
	x = empty(n)
	y = empty(n)

	i=0
	for ts in ts_list:
		vis_map[:,:,i] = visibility_images(ts,y_min,y_max,x_min,x_max,analysis_method)
		#vis_map = dstack((vis_map,visibility_images(ts,y_min,y_max,x_min,x_max,analysis_method)))
		md = MetaData(ts)
		md.load()
		x[i] = md.parameters["coarse_position"]
		i=i+1

	#fit a gaussian to extract coherence length
	#gaussian fitting function
	def gaussfunc(x,a,b,c,d):
		x1 = (x-b)**2
		x2 = 2*c**2
		return a*exp(-x1/x2)+d
	
	#test guesses
	center_x = (x_max-x_min)/2
	center_y = (y_max-y_min)/2
	y = vis_map[center_x,center_y,:]
	plot(x,y,'b.')
	y_guess = gaussfunc(x,guess[0],guess[1],guess[2],guess[3])
	
	return x, y, y_guess
	
	#initial guess
	#guess = array([100, 0.5, 3, 50]) #amplitude, x offset, width, y offset guesses
	'''		
	for j in range(0,y_max-y_min-1):
		for i in range(0,x_max-x_min-1):
			y = vis_map[i,j,:]
			fitpars, covmat = curve_fit(gaussfunc, x, y, p0=guess)
			coh_length[i,j] = fitpars[2]/2
	
	return coh_length
	'''