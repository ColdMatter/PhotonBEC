#execfile("analysis.py")
#this iteration of analysis was for experiments on 20140901 finding temporal coherence of LED

from int_functions import *

'''
#this is number of piezo steps, needed if we want img_map
n = 30
'''
close('all')
analyzeData = False
fitGaussian = True

if analyzeData:
	getWindowCoords = True
	single = False
	if single:
		mult = False
	else:
		mult = True
	stdUsed = False
	analysis_method = 'rmsVis'
	#def sinfunc(x,a,b,c,d):
		#return a*sin(b*x-c)+d
	guess = array([35, 0.42, 0, 70]) #amplitude, frequency, phase, offset guesses, doesn't get used in rmsvis method
	close("all")

	#if looking at single fringe
	if single:
		ts = '20140825_145131'
		if getWindowCoords:
			x_min, x_max, y_min, y_max = image_window(ts)
		max_vis, vis_map = visibility_images(ts,y_min,y_max,x_min,x_max,analysis_method,guess)
		print "The maximum visibility is " + str(max_vis)
		imshow(vis_map,vmax=1)
		title("Visibility")
		colorbar()
		
	#do this for a range of turns
	if mult:
		first_ts = "20140901_123515"
		last_ts = "20140901_125454"
		if getWindowCoords:
			x_min, x_max, y_min, y_max = image_window(first_ts)	
		ts_list = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
		#add second set of timestamps SIGH
		#first_ts = "20140901_102909"
		#last_ts = "20140901_105329"
		#ts_temp = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
		#ts_list.extend(ts_temp)
		n = size(ts_list)
		vis_map = empty((x_max-x_min,y_max-y_min,n))
		max_vis = empty(n)
		x = empty(n)
		if stdUsed:
			num_std = 5
			num_points = n/num_std
			base_voltages = empty(num_points)
			max_vis_per_point = empty(num_points)
			std_max_vis = empty(num_points)

		i = 0
		for ts in ts_list:
			md = MetaData(ts)
			md.load()
			voltages = md.parameters["xvs"]
			x[i] = voltages[0]
			max_vis[i], vis_map[:,:,i] = visibility_images(ts,y_min,y_max,x_min,x_max,analysis_method,guess)
			i = i+1

		#need to sort array!
		if stdUsed: 
			z = array(zip(x,max_vis))
			z = z[argsort(z[:,0])]
			x_sort = transpose(z)[0]
			max_vis = transpose(z)[1]
			for k in range(0,num_points):
				base_voltages[k] = x_sort[int(num_std*k)]
				max_vis_per_point[k] = mean(max_vis[int(num_std*k):int(num_std*k+num_std)])
				std_max_vis[k] = std(max_vis[int(num_std*k):int(num_std*k+num_std)])
				errorbar(base_voltages,max_vis_per_point,yerr=std_max_vis,fmt='b.')
				ylabel("Maximum Visibility")
				xlabel("Base Piezo Voltage (V)")
		
		#figure(3)
		else:
			plot(x,max_vis,'b.')
			ylabel("Maximum Visibility")
			xlabel("Base Piezo Voltage (V)")

#fit a gaussian to extract coherence length
if fitGaussian:
	test_x = (x_max-x_min)/2
	test_y = (y_max-y_min)/2
	#gaussian fitting function
	def gaussfunc(x,a,b,c,d):
		x1 = (x-b)**2
		x2 = 2*c**2
		return a*exp(-x1/x2)+d
	guess = array([0.5, 25, 20, 0.01]) #amplitude, x offset, width, y offset guesses

	testGuess = False
	if testGuess:
		errorbar(base_voltages,max_vis_per_point,yerr=std_max_vis,fmt='b.')
		y_guess = gaussfunc(sort(x),guess[0],guess[1],guess[2],guess[3])
		#y_test = gaussfunc(sort(x),test_pars[0],test_pars[1],test_pars[2],test_pars[3])
		plot(sort(x),y_guess,'r-')

	else:
		errorbar(base_voltages,max_vis_per_point,yerr=std_max_vis,fmt='b.')
		fitpars,covmat = curve_fit(gaussfunc, base_voltages, max_vis_per_point, p0=guess)
		variances = covmat.diagonal()
		std_devs = sqrt(variances)
		y_fit = gaussfunc(base_voltages,fitpars[0],fitpars[1],fitpars[2],fitpars[3])
		plot(base_voltages,y_fit,'r-')
		ylabel("Maximum Visibility")
		xlabel("Base Piezo Voltage (V)")
		print "The coherence length was calculated to be " + str(abs(fitpars[2])/2) + " plus/minus " + str(std_devs[2]/2) + " V"
	
'''
	for j in range(0,y_max-y_min-1):
		for i in range(0,x_max-x_min-1):
			y = vis_map[i,j,:]
			z = array(zip(x,y))	
			z = z[argsort(z[:,0])]
			x = transpose(z)[0]
			y = transpose(z)[1]
			try:
				fitpars, covmat = curve_fit(gaussfunc, x, y, p0=guess)
				coh_length[i,j] = abs(fitpars[2])/2
				#look at spatial maximum visibility just for the lols
				coh_amp[i,j] = fitpars[0]
			except:
				fitpars = zeros(3)
				coh_length[i,j] = 0
				coh_amp[i,j] = 0
			if j == test_y:
				if i == test_x:
					test_pars = fitpars
close("all")
subplot(1,2,1)
imshow(coh_length,vmax=1.5)
title("Coherence Length (mm)")
colorbar()
subplot(1,2,2)
imshow(coh_amp,vmin=0,vmax=1)
title("Maximum Visibility")
colorbar()
#test fit or guess
testFit = False
if testFit:
	y = vis_map[test_x,test_y,:]
	#close("all")
	figure(3)
	plot(x,y,'b.')
	#y_guess = gaussfunc(sort(x),guess[0],guess[1],guess[2],guess[3])
	y_test = gaussfunc(sort(x),test_pars[0],test_pars[1],test_pars[2],test_pars[3])
	plot(sort(x),y_test,'r-')
	xlabel('Coarse Position (mm)')
	ylabel('Visibility')
	title('Test Pixel Fit')
	#title("Title (a.u.)")
	grid(1)
#
#width of analysis region (to fit gaussian?)
#THIS IS EXTREMELY HACKY
#coarse_min = 8
#coarse_max = 20
#x_fit = empty(coarse_max-coarse_min+1)
#y_fit = empty(coarse_max-coarse_min+1)
'''