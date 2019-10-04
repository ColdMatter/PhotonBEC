
import sys
#sys.path.append("Y:\\Control\\PythonPackages\\")
sys.path.append("D:\\Control\\PythonPackages\\")

import time

import tektronix


def test_speed():
	N = 20
	data = []
	print 'taking data'
	st = time.time()
	tek = tektronix.Tektronix(binary=True)
	tek.setChannel(chan=1)
	tek.setDataRange(1000, 2000)
	for i in range(N):
		raw_data = tek.getRawChannelDataAsString()
		data.append([ord(d) for d in raw_data])
	#t_data = tek.getTData(data[0])
	et = time.time()
	print 'taking ' + str(N) + ' readings took ' + str(et - st) + ' sec or ' + str((et-st)/N) + ' sec/reading'


def plot_two_data_ranges():
	tek = tektronix.Tektronix(binary=True)
	print 'before = ' + str(tek.getVoltageScales())
	tek.setVoltageScale(1, 0.003)
	tek.setChannel(chan=1)
	tek.setDataRange(1200, 2000)
	raw_data_1 = tek.getRawChannelDataAsString()
	data_1 = array([ord(d) for d in raw_data_1])
	conversion_values_1 = tek.get_voltage_conversion_values()
	print 'middle  = ' + str(tek.getVoltageScales())
	tek.setVoltageScale(1, 0.03)
	tek.setChannel(chan=1)
	tek.setDataRange(1200, 2000)
	raw_data_2 = tek.getRawChannelDataAsString()
	data_2 = array([ord(d) for d in raw_data_2])
	conversion_values_2 = tek.get_voltage_conversion_values()
	print 'after  = ' + str(tek.getVoltageScales())
	
	data_1v = tek.convert_raw_data_to_volts(data_1, conversion_values_1)
	data_2v = tek.convert_raw_data_to_volts(data_2, conversion_values_2)
	
	figure('two-data'),clf()
	plot(data_1v)
	plot(data_2v)
	ylabel('Volts / V')
	
#plot_two_data_ranges()


def many_different_scales():
	#pixels where the height is the data
	#background is where there isnt data
	#time scale must be 500ns per square
	pulse_range = (330, 470)
	background_range = (0, 150)
	
	#see lab book 31/8/2016
	T = 48
	R = 232
	S = 0.22

	tek = tektronix.Tektronix(binary=True)
	tek.setChannel(chan=1)
	tek.setDataRange(1200, 2000)
	scales = linspace(0.5, 0.05, 9)
	datas = []
	raw_readings = []
	for scale in scales:
		tek.setVoltageScale(1, scale)
		data = tek.getRawChannelDataAsString()
		data = array([ord(d) for d in data])
		raw_readings.append(data)
		con_vals = tek.get_voltage_conversion_values()
		print 'set scale = ' + str(scale) + ' conversion_values = ' + str(con_vals) + ' ratio=' + str(scale / con_vals[1])
		data = tek.convert_raw_data_to_volts(data, con_vals)
		data = data*T/S/R #data is in power now
		datas.append(data)
		
	pulse_mask = arange(len(data))
	pulse_mask = (pulse_mask > pulse_range[0]) & (pulse_mask < pulse_range[1])
	background_mask = arange(len(data))
	background_mask = (background_mask > background_range[0]) & (background_mask < background_range[1])
	
	figure('scales'),clf()
	for d, s in zip(datas, scales):
		plot(d*1e3, label=str(s))
	ylabel('Laser power after AoM / mW')
	#plot([background_range[0], background_range[0]], [0, ylim()[1]], 'r-')
	#plot([background_range[1], background_range[1]], [0, ylim()[1]], 'r-')
	#plot([pulse_range[0], pulse_range[0]], [0, ylim()[1]], 'r-')
	#plot([pulse_range[1], pulse_range[1]], [0, ylim()[1]], 'r-')
	x = arange(len(data))
	fill_between(x, ylim()[0], ylim()[1], where=(x<background_range[1]), facecolor='k', alpha=0.1,color="w")
	fill_between(x, ylim()[0], ylim()[1], where=((x<pulse_range[1])&(x>pulse_range[0])), facecolor='k', alpha=0.1,color="w")
	legend(loc='best', prop={'size':8})
	
	figure('raw_readings'),clf()
	for d, s in zip(raw_readings, scales):
		plot(d, label=str(s))

	amplitudes = [mean(dat[pulse_mask]) - mean(dat[background_mask]) for dat in datas]
	figure('amplitudes-vs-scale'),clf()
	plot(scales, amplitudes, 'x-')
	ylim([0, ylim()[1]*1.5])
	
many_different_scales()