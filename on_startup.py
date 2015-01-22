
#on startup

import sys
sys.path.append("D:\\Control\\PythonPackages\\")

print "Setting AOM voltage.."
import SingleChannelAO
##SingleChannelAO.SetAO0(0.9) #Value on 14/1/2015 is 1.0
SingleChannelAO.SetAO0(1.05)
