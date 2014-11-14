#execfile("analysis.py")

from int_functions import *

#do we need to reload the visibility map?
visMap = False
#reload image window coordinates?
windowCoords = False
#analysis method?
analysis_method = "rmsVis"
#need this for visibility_images function, won't be used if rmsVis is selected
askGuess = True

#range of timestamps to analyze
first_ts = "20140819_185158"
last_ts = "20140819_185558"

if windowCoords:
	x_min, x_max, y_min, y_max = image_window(first_ts)

ts_list = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
n = size(ts_list)

test_x = (x_max-x_min)/2
test_y = (y_max-y_min)/2

#initialize arrays
coh_length = empty((x_max-x_min,y_max-y_min))
coh_amp = empty((x_max-x_min,y_max-y_min))
y = empty(n)

if visMap:
	x = empty(n)
	vis_map = empty((x_max-x_min,y_max-y_min,n))
	i=0
	for ts in ts_list:
		pass_guess = empty(4)
		vis_map[:,:,i] = visibility_images(ts,y_min,y_max,x_min,x_max,analysis_method,pass_guess)
		md = MetaData(ts)
		md.load()
		x[i] = md.parameters["coarse_position"]
		i=i+1		

y = vis_map[test_x,test_y,:]
plot(x,y,'b.')

#fit a gaussian to extract coherence length
#gaussian fitting function
def gaussfunc(x,a,b,c,d):
	x1 = (x-b)**2
	x2 = 2*c**2
	return a*exp(-x1/x2)+d

#width of analysis region (to fit gaussian) and guesses - ask user!
if askGuess:
	guess = empty(4)
	coarse_min = int(raw_input("Enter the minimum coarse position (integer) and press return "))
	coarse_max = int(raw_input("Enter the maximum coarse position (integer) and press return "))
	guess[0] = float(raw_input("Enter the guess for the amplitude and press return "))
	guess[1] = float(raw_input("Enter the guess for the x offset and press return "))
	guess[2] = float(raw_input("Enter the guess for the width and press return "))
	guess[3] = float(raw_input("Enter the guess for the y offset and press return "))
	#close("all")

x_sort = empty(coarse_max-coarse_min+1)
y_sort = empty(coarse_max-coarse_min+1)

#sort values so we can only fit part of it
z = array(zip(x,y))
z = z[argsort(z[:,0])]
x_sort = transpose(z)[0]
y_sort = transpose(z)[1]

#y_guess = sinc2func(sort(x),guess[0],guess[1])
#plot(sort(x),y_guess,'r-')

x_fit = x_sort[coarse_min:coarse_max]
y_fit = y_sort[coarse_min:coarse_max]
#y_guess = gaussfunc(sort(x),guess[0],guess[1],guess[2],guess[3])

fitpars, covmat = curve_fit(gaussfunc,x_fit,y_fit,p0=guess)
#fitpars, covmat = curve_fit(sinc2func,x_fit,y_fit,p0=guess)

variances = covmat.diagonal()
std_devs = sqrt(variances)

x_fit_new = linspace(x_fit[0],x_fit[13],50)
y_fit_new = gaussfunc(x_fit_new,fitpars[0],fitpars[1],fitpars[2],fitpars[3])
#y_fit_new = sinc2func(x_fit,fitpars[0],fitpars[1],fitpars[2],fitpars[3])
plot(x_fit,y_fit_new,'r-')
print "The coherence length is equal to " + str(guess[2]/2) + " plus/minus " + str(std_devs[2]) + " mm"
xlabel('Coarse Position (mm)')
ylabel('Visibility')
'''

#guess = array([1, 15, 2, 0.1]) #amplitude, x offset, width, y offset guesses
#test fit or guess?
testFit = False

for j in range(0,y_max-y_min-1):
	for i in range(0,x_max-x_min-1):
		y = vis_map[i,j,:]
		z = array(zip(x,y))
		z = z[argsort(z[:,0])]
		x_sort = transpose(z)[0]
		y_sort = transpose(z)[1]
		try:
			fitpars, covmat = curve_fit(gaussfunc, x_sort, y_sort, p0=guess)
			coh_length[i,j] = abs(fitpars[2])/2
			coh_amp[i,j] = fitpars[0]
		except:
			fitpars = zeros(3)
			coh_length[i,j] = 0
			coh_amp[i,j] = 0
		if testFit:
			if j == test_y:
				if i == test_x:
					test_pars = fitpars
figure(2)
subplot(1,2,1)
imshow(coh_length,vmin=0.5,vmax=1.5)
title("Coherence Length (mm)")
colorbar()
subplot(1,2,2)
imshow(coh_amp,vmin=0,vmax=1)
title("Maximum Visibility")
colorbar()

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