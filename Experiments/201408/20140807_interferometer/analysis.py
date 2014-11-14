#execfile("analysis.py")
#this analysis function was used to look at the visibility of the center pixel for the pump laser
#also generates visibility and coherence length maps

from int_functions import *

#range of timestamps
first_ts = "20140807_151846"
last_ts = "20140807_154505"

ts_list = timestamps_in_range_single_day(first_ts, last_ts, extension=".zip")
n = size(ts_list)

#image analysis window
x_min = 630
x_max = 740
y_min = 700
y_max = 830

getWindowCoords = True
if getWindowCoords:
	x_min, x_max, y_min, y_max = image_window(ts)

center_x = (x_max-x_min)/2
center_y = (y_max-y_min)/2

#keep this hard coded for now
analysis_method = "rmsVis"

#initialize arrays
vis_map = empty((x_max-x_min,y_max-y_min,n))
coh_length = empty((x_max-x_min,y_max-y_min))
x = empty(n)
y = empty(n)
#max_vis = empty(n)

max_width = 10
i=0
for ts in ts_list:
	vis_map[:,:,i] = visibility_images(ts,y_min,y_max,x_min,x_max,analysis_method)
	#max_vis[i] = amax(vis_map[center_x-max_width:center_x+max_width,center_y-max_width:center_y+max_width,i])
	md = MetaData(ts)
	md.load()
	x[i] = md.parameters["coarse_position"]
	i=i+1

#fit a gaussian to extract coherence length
#gaussian fitting function
def sinc2func(x,a,b,c,d):
	return (a*sin(b*(x-c))/(b*(x-c)))**2+d

def gaussfunc(x,a,b,c,d):
	x1 = (x-b)**2
	x2 = 2*c**2
	return a*exp(-x1/x2)+d

guess = array([1, 20, 2, 0.1]) #amplitude, x offset, width, y offset guesses for gaussian
#guess = array([1,0.5,19,0.1]) #width and x offset guess for sinc function
	
y = vis_map[center_x,center_y,:]
close("all")
plot(x,y,'b.')

#width of analysis region (to fit gaussian?)
#THIS IS EXTREMELY HACKY
coarse_min = 0
coarse_max = 50
x_fit = empty(coarse_max-coarse_min+1)
y_fit = empty(coarse_max-coarse_min+1)

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

y_fit_new = gaussfunc(x_fit,fitpars[0],fitpars[1],fitpars[2],fitpars[3])
#y_fit_new = sinc2func(x_fit,fitpars[0],fitpars[1],fitpars[2],fitpars[3])
plot(x_fit,y_fit_new,'r-')
#print "The coherence length is equal to " + str(guess[2]/2) + " mm"

#figure(2)
#plot(x,max_vis,'b.')
#title('Maximum Visibility in Center of Image')
#plot(x,y_guess,'r-')
xlabel('Coarse Position (mm)')
ylabel('Visibility')
#grid(1)
