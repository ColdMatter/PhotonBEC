'''
	Test and Example code to work with the Thorlab's filter wheel


	Written by: Joao Rodrigues
	Last Update 19rd March 2019

'''

from FilterWheel import FilterWheel

OD_setting = dict()
OD_setting['position 1'] = 0
OD_setting['position 2'] = 0.5
OD_setting['position 3'] = 1.0
OD_setting['position 4'] = 2.0
OD_setting['position 5'] = 3.0
OD_setting['position 6'] = 4.0

# initializes filter object
filter_wheel = FilterWheel(OD_setting=OD_setting, verbose=True, COM_port=27)

#print(filter_wheel.table_attenuation)
#print(filter_wheel.table_position_key)

# sets filter to position 1
filter_wheel.reset_filter_wheel()

# sets a given attenuation
optimal_attenuation = 0.99
status = filter_wheel.set_wheel_attenuation(optimal_attenuation=optimal_attenuation, side_control='lower signal')



# returns the filter current attenuation
filter_wheel.get_current_status()
current_attenuation = filter_wheel.current_attenuation
print(current_attenuation)

filter_wheel.close_port()
