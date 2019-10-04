
import sys
sys.path.append("Y:\\Control\\PythonPackages\\")
sys.path.append("D:\\Control\\PythonPackages\\")

import pbec_experiment as pbece

class DataSource(object):
	#def __init__(self, constructor=None, init_calls=None, arm_calls=None, trigger_getdata=None, finalise_calls=None, save_calls=None):
	def __init__(self, constructor=None, init_calls=None, arm_calls=None, trigger_getdata=None, finalise_calls=None, save_calls=None, theglobal=None):

		import pprint
		self.source = eval(constructor)
		for init_line in init_calls:
			print 'evaling ' + init_line
			print 'globals'
			g = globals()
			pprint.pprint(g)
			eval(init_line, g)
	
		self.init_calls = init_calls
		self.arm_calls = arm_calls
		self.trigger_getdata = trigger_getdata
		self.finalise_calls = finalise_calls
		self.save_calls = save_calls