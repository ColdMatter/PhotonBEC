#exit()

#ipython --pylab
#exec(open("calibrate_AOM_amplitude.py").read())
import time
import os
from SingleChannelAO import SingleChannelAO, SetAO0
from SingleChannelAI import SingleChannelAI, GetAI0

#CONSTANT
data_folder = "D:\Data"
pbec_prefix = "pbec_"

def TimeStamp():
	#Outputs time stamp in format YYYYMMDD_hhmmss
	t = time.localtime()
	YYYY = str(t.tm_year)
	MM= str(100+t.tm_mon)[-2:] #pre-pends zeroes where needed
	DD = str(100+t.tm_mday)[-2:]
	hh = str(100+t.tm_hour)[-2:]
	mm = str(100+t.tm_min)[-2:]
	ss = str(100+t.tm_sec)[-2:]
	l=[YYYY,MM,DD,"_",hh,mm,ss]
	return "".join(l)

def DataFolder(ts=TimeStamp(),make=False):
	"""
	Returns the name of the correct folder to save data.
	If folder does not exist, makes it and higher level folders as needed.
	"""
	folder_day = ts.split("_")[0]
	folder_month=folder_day[:-2]
	folder_year=folder_month[:-2]
	#Yearly folders
	year_folder = data_folder+"\\"+folder_year
	if (os.listdir(data_folder).count(folder_year)==0) & make:
		os.mkdir(year_folder)
	#
	#Monthly folders
	month_folder = year_folder+"\\"+folder_month
	if (os.listdir(year_folder).count(folder_month)==0) & make:
		os.mkdir(month_folder)
	#
	#Daily folders
	day_folder = month_folder+"\\"+folder_day
	if (os.listdir(month_folder).count(folder_day)==0) & make:
		os.mkdir(day_folder)

	return day_folder+"\\"

def SaveData(x,y,ts,savefignum=None,comment=""):
	save_folder = DataFolder(ts,make=1)
	out_str = ts+"\n"
	out_str+= comment+"\n"
	xxyy = zip(x,y)
	for xy in xxyy:
		#out_str += str(list(xy))[1:-1]+"\n"
		out_str += str(array(xy))[2:-1]+"\n"
	fil = open(save_folder+pbec_prefix+ts+".dat","w")
	fil.write(out_str)
	fil.close()
	if savefignum!=None:
		figure(savefignum)
		savefig(save_folder+pbec_prefix+ts+"_fig"+str(savefignum)+".png")
	#
	return save_folder+ts
	

def SetAndGet(set_vals=linspace(0,2,101),fignum=217,\
	x_label="Set Value / V", y_label="Measured Value / V",comment="",\
	saving=False,savefignum=None, pause_between_measurements=0):
	Npts = len(set_vals)
	get_vals=[]
	ts = TimeStamp()
	for s in set_vals:
		SetAO0(s)
		if pause_between_measurements!=0:
			time.sleep(pause_between_measurements)
		get_vals.append(GetAI0(Npts=Npts))
	#
	figure(fignum),clf()
	plot(set_vals,get_vals)
	xlabel(x_label), ylabel(y_label)
	grid(1)
	title(ts+"\n"+comment)
	show()
	if saving:
		savename=SaveData(set_vals,get_vals,ts,savefignum=savefignum,comment=comment)
		print "Data saved as "+savename
	return set_vals,array(get_vals),ts
	

#
"""
while 1:
	x,y,ts = SetAndGet()
	time.sleep(3)
"""
#SetAndGet(comment="AOM calibration",x_label="Control / V",y_label = "PD into 10 k$\Omega$ / V",saving=1,savefignum=217)
#SetAndGet(comment="AOM calibration",x_label="Control / V",y_label = "PD into 10 k$\Omega$ / V",saving=0,savefignum=217)
#EOF
