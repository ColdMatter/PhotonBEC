#execfile("data_format_test.py")
from __future__ import division
from pylab import *
import json

import sys
sys.path.append("D:\Control\PythonPackages")
from pbec_analysis import *


#Make some fake data
Npts = 11
x = linspace(0,1000,Npts)
y1 = sin(x)
y2 = cos(x)

#Make some comments
"independent parameter is x. Data are y1 and y2, in that order"

#Save data functions
#Utilities stolen from http://stackoverflow.com/questions/3488934/simplejson-and-numpy-array
def arr2json(arr):
    return json.dumps(arr.tolist())
def json2arr(astr,dtype):
    return np.fromiter(json.loads(astr),dtype)

#Probably best done in JSON format for small-ish data files. Maybe.
class DataFormat():
	def __init__(self, timestamp, indep_variable = None, dep_variables = None, \
			parameters = {}, comments = "", links = None):
		self.timestamp = timestamp #uses format from pbec_analysis
		self.indep_variable = indep_variable
		self.dep_variables = dep_variables #should be a dictionary, with human-readable keys and array values
		self.parameters = parameters
		self.comments = comments
		self.links = links #for any other files which are linked.
	def getDictOfData(self):
		dd = {}
		dd.update({"timestamp":self.timestamp})
		dd.update({"indep_variable":list(self.indep_variable)})
		dep_var_rejig = {}
		for key in self.dep_variables:
			dep_var_rejig.update({key:(self.dep_variables[key])})
		#ld.append({"dep_variables":self.dep_variables.tolist()})
		dd.update({"dep_variables":dep_var_rejig})
		dd.update({"parameters":self.parameters})
		dd.update({"comments":self.comments})		
		dd.update({"links":self.links})
		return dd
	def getFilename(self,make_folder = False):
		f = pbec_prefix + "_" + self.timestamp + ".json"
		return DataFolder(self.timestamp, make = make_folder) + f
	def getJSONrepresentation(self,**kwargs):
		return json.dumps(self.getDictOfData(),**kwargs)
	def saveData(self):
		js = self.getJSONrepresentation(indent=4)
		filename = self.getFilename(make_folder=True)
		fil = open(filename,"w")
		fil.write(js)
		fil.close()
	def loadData(self):
		filename = self.getFilename();
		fil = open(filename,"r");
		raw_json = fil.read();
		fil.close()
		decoded = json.loads(raw_json)
		#Re-format some variables
		self.__dict__.update(decoded)
	def plotMe(self,fignum=764,xlab="Inependent variable",ylab = "Dependent variables",title_extra=None):
		figure(fignum),clf()
		for key in self.dep_variables:
			plot(self.indep_variable,self.dep_variables[key],label = key)
		xlabel(xlab)
		ylabel(ylab)
		if title_extra!=None:
			title_string = self.comments+"\n"+title_extra
		else:
			title_string = self.comments
		title(title_string)
		legend()
		grid(1)



"""
Fields needed for 'scope data (not easy to make useful for images)
- data and time of creation
- raw data (indep parameter, x)
- raw data (dependent variables, set of y's)
- control parameters and settings
- human-input comments
- linked files
"""


#------------------------
#Testing area
#------------------------
if 0:
	#make a data file
	timestamp = TimeStamp()
	df = DataFormat(timestamp, x,{"y1":y1,"y2":y2},comments = "test")
	dd = df.getDictOfData()
	js = df.getJSONrepresentation(indent=4)
	df.saveData()

if 1:
	#Load data, starting from as TimeStamp
	ts = "20130920_175118"
	df = DataFormat(ts)
	df.loadData()
	df.plotMe(fignum=764,xlab="x",ylab="a.u.",title_extra = "extra texta")


#EOF
