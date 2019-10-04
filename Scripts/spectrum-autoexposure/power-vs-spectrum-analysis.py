
import sys
sys.path.append("D:\\Control\\PythonPackages\\")

import pbec_experiment as pbece
import pbec_analysis as pbeca

import pbec_ipc

saving = True
dataset = 6
if dataset == 0:
	first_ts, last_ts = "20150728_193558", "20150728_193712"
	lamb_range = (550, 600)
	counts_range = (1e8, 1e10)
elif dataset == 1:
	first_ts, last_ts = "20150728_195316", "20150728_195501"
	lamb_range = (550, 600)
	counts_range = (1e8, 1e10)
elif dataset == 2:
	first_ts, last_ts = "20150728_200125", "20150728_200730"
	lamb_range = (570, 600)
	counts_range = (1e5, 1e7)
elif dataset == 3:
	first_ts, last_ts = "20150804_181621", "20150804_181943"
	lamb_range = (585, 593)
	counts_range = (1e5, 1e9)
elif dataset == 4:
	first_ts, last_ts = "20150804_182414", "20150804_182845"
	lamb_range = (585, 593)
	counts_range = (1e5, 1e9)
elif dataset == 5:
	first_ts, last_ts = "20150804_183301", "20150804_183618"
	lamb_range = (585, 593)
	counts_range = (1e5, 1e9)	
elif dataset == 6:
	first_ts, last_ts = "20150804_184426", "20150804_184808"
	lamb_range = (585, 593)
	counts_range = (1e5, 1e9)
	


save_folder = "./"+first_ts+"/"
save_prefix = save_folder+first_ts+"_"
if saving: 
	if not(pbeca.os.path.exists("./"+first_ts)):
		pbeca.os.makedirs("./"+first_ts+"/")

ts_list = pbeca.timestamps_in_range(first_ts, last_ts, extension='_spectrum.json')
oexperiment_list = [pbeca.ExperimentalDataSet(ts=ts) for ts in ts_list]
[oexperiment.meta.load() for oexperiment in oexperiment_list]

figlabel = 'spectra-vs-power'
figure(figlabel), clf()
powers = sorted(list(set([ex.meta.parameters['power_mw'] for ex in oexperiment_list])))
for p in powers:
	this_power_ex = [ex for ex in oexperiment_list if ex.meta.parameters['power_mw'] == p][0]
	this_power_ex.constructDataSet()
	this_power_ex.dataset['spectrum'].loadData()
	
	print this_power_ex.meta.parameters
	count_rate = this_power_ex.dataset['spectrum'].spectrum / this_power_ex.meta.parameters['int_time']
	semilogy(this_power_ex.dataset['spectrum'].lamb, count_rate, 'x-', label='power ' + str(p) + 'mW')

title('timestamps = ' + str((first_ts, last_ts)),fontsize=12)
xlabel('wavelength / nm')
ylabel('Count Rate 1/s')
xlim(*lamb_range)
ylim(*counts_range)
grid(1)
legend(loc="upper left",prop={'size':9})
if saving: savefig(save_prefix+figlabel+".png")