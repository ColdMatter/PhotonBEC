
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import time
import agilent33521A

a = agilent33521A.AgilentFunctionGenerator()

a.outputOn()
time.sleep(2)
a.outputOff()

'''
time.sleep(2)
print('polarity is = ' + str(a.getOutputPolarity()))
a.setOutputPolarityNormal()
time.sleep(2)
print('polarity is = ' + str(a.getOutputPolarity()))
a.setOutputPolarityInverted()
'''