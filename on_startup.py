
#on startup

import sys
sys.path.append("D:\\Control\\PythonPackages\\")
sys.path.append("PythonPackages/")

print "Setting AOM voltage.."
import SingleChannelAO
####SingleChannelAO.SetAO0(0.9) #Value on 14/1/2015 is 1.0
####SingleChannelAO.SetAO0(1.05) #Value on 23/7/15
#SingleChannelAO.SetAO0(1.14) #Value on 24/7/15
#SingleChannelAO.SetAO0(0)

SingleChannelAO.SetAO0(0.0)