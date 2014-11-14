
#on startup

import sys
sys.path.append("D:\\Control\\PythonPackages\\")

print "Setting AOM voltage.."
import SingleChannelAO
SingleChannelAO.SetAO0(0.9)
