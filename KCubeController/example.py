'''
	Written by Joao Rodrigues
	November 2020
'''

import time 

from KCubeController import KCubeController


kcube=KCubeController(VERBOSE=True, SIMULATION=True, serial_number=97000001)


position=kcube.get_current_position(channel=3)
print(position)


#FLAG=kcube.move_jog(channel=4, direction='forward')

FLAG=kcube.move_to_position(channel=1, position=1122)



#kcube.close()