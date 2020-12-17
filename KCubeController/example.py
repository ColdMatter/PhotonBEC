'''
	Written by Joao Rodrigues
	November 2020
'''

import time 

from KCubeController import KCubeController


kcube=KCubeController(VERBOSE=True, SIMULATION=False, serial_number=97100796)
#kcube=KCubeController(VERBOSE=True, SIMULATION=True, serial_number=97000001)


#FLAG=kcube.move_jog(channel=4, direction='forward')

FLAG=kcube.move_to_position(channel=1, position=500)


position=kcube.get_current_position(channel=1)
print(position)

[print(kcube.get_current_position(channel=i)) for i in [1,2,3,4]]



#kcube.close()