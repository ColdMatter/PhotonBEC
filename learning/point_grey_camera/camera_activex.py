#http://people.seas.harvard.edu/~krussell/html-tutorial/activeX.html

import win32com.client
#activeX_class_name = "ActiveFlyCap 2.0 Type Library" #herein lies the problem for now
#activeX_class_name = "ActiveFlyCapLibControlClass"
activeX_class_name = "ActiveFlyCapLib"
win32com.client.Dispatch(activeX_class_name)





"""
#Example from http://jotsite.com/discussit_x.php?cmd=show&thread=9 and then modified
from wx import *
from wx.lib.activexwrapper import MakeActiveXClass
import win32com.client.gencache

#Probably part of this line makes no sense: magic number programming!
calendar = win32com.client.gencache.EnsureModule('{8E27C92E-1264-101C-8A2F-040224009C02}', 0, 7, 0)

ActiveXWrapper = MakeActiveXClass(calendar)
"""