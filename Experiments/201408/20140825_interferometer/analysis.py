#execfile("analysis.py")

from int_functions import *

'''
#this is number of piezo steps, needed if we want img_map
n = 30
'''

getWindowCoords = True
single = False
if single:
	mult = False
else:
	mult = True

analysis_method = 'rmsVis'
#def sinfunc(x,a,b,c,d):
	#return a*sin(b*x-c)+d
guess = array([35, 0.42, 0, 70]) #amplitude, frequency, phase, offset guesses, doesn't get used in rmsvis method
#test_x = (x_max-x_min)/2
#test_y = (y_max-y_min)/2
close("all")

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
	first_ts = "20140827_152250"
	last_ts = "20140827_180327"
	if getWindowCoords:
		x_min, x_max, y_min, y_max = image_window(first_ts)	
	ts_list = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
	#add second set of timestamps SIGH
	first_ts = "20140901_102909"
	last_ts = "20140901_105329"
	ts_temp = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
	ts_list.extend(ts_temp)
	#ts_list = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
	n = size(ts_list)
	vis_map = empty((x_max-x_min,y_max-y_min,n))
	x = empty(n)
	max_vis = empty(n)
	num_std = 5
	num_turns = int(n/num_std)
	turns = empty(num_turns)
	max_vis_per_turn = empty(num_turns)
	std_max_vis_per_turn = empty(num_turns)

	i = 0
	for ts in ts_list:
		md = MetaData(ts)
		md.load()
		x[i] = md.parameters["turns"]
		#voltages = md.parameters["xvs"]
		#x[i] = voltages[0]
		max_vis[i], vis_map[:,:,i] = visibility_images(ts,y_min,y_max,x_min,x_max,analysis_method,guess)
		i = i+1
		#subplot(1,n,i)
		#imshow(vis_map[:,:,i-1],vmax=1)
		#colorbar()
	
	for k in range(0,num_turns):
		turns[k] = x[int(num_std*k)]
		max_vis_per_turn[k] = mean(max_vis[int(num_std*k):int(num_std*k+num_std)])
		std_max_vis_per_turn[k] = std(max_vis[int(num_std*k):int(num_std*k+num_std)])
	
	#figure(3)
	errorbar(turns,max_vis_per_turn,yerr=std_max_vis_per_turn,fmt='.')
	ylabel("Maximum Visibility")
	xlabel("Number of Turns")
	
'''
x = np.linspace(0,n-1,n)
def sinfunc(x,a,tau,b,c,d):
	return a*exp(-x/tau)*sin(b*x-c)+d
	
y = img_map[test_x,test_y,:]
y_fit = sinfunc(x,guess[0],guess[1],guess[2],guess[3],guess[4])
close("all")
plot(x,y,'b.')
plot(x,y_fit,'r-')	
'''


'''
visMap = True

#range of timestamps
first_ts = "20140819_185158"
last_ts = "20140819_185558"
ts_list = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
n = size(ts_list)

#image analysis window
x_min = 500
x_max = 710
y_min = 600
y_max = 850
test_x = 2*(x_max-x_min)/3
test_y = 2*(y_max-y_min)/3

#initialize arrays
coh_length = empty((x_max-x_min,y_max-y_min))
coh_amp = empty((x_max-x_min,y_max-y_min))
y = empty(n)

if visMap:
	x = empty(n)
	vis_map = empty((x_max-x_min,y_max-y_min,n))
	#keep this hard coded for now
	analysis_method = "rmsVis"
	i=0
	for ts in ts_list:
		vis_map[:,:,i] = visibility_images(ts,y_min,y_max,x_min,x_max,analysis_method)
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

#width of analysis region (to fit gaussian?)
#THIS IS EXTREMELY HACKY
coarse_min = 8
coarse_max = 20
x_fit = empty(coarse_max-coarse_min+1)
y_fit = empty(coarse_max-coarse_min+1)
guess = array([1, 15, 2, 0.1]) #amplitude, x offset, width, y offset guesses

for j in range(0,y_max-y_min-1):
	for i in range(0,x_max-x_min-1):
		y = vis_map[i,j,:]
		z = array(zip(x,y))
		z = z[argsort(z[:,0])]
		x_sort = transpose(z)[0]
		y_sort = transpose(z)[1]
		x_fit = x_sort
		y_fit = y_sort
		#x_fit = x_sort[coarse_min:coarse_max]
		#y_fit = y_sort[coarse_min:coarse_max]
		try:
			fitpars, covmat = curve_fit(gaussfunc, x_fit, y_fit, p0=guess)
			coh_length[i,j] = abs(fitpars[2])/2
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
'''