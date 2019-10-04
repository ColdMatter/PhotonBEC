import sys, json

import matplotlib.pyplot as plt

if len(sys.argv) == 1:
	print 'drag a spectrometer json data file to display'
	raw_input('press any key to continue . . .')

spec_path = sys.argv[1]

spec_fd = open(spec_path, 'r')
spec_data = json.load(spec_fd)
spec_fd.close()

#spec_data['lamb']
#spec_data['spectrum']
#spec_data['ts']

fig = plt.figure('display-json-spectrum')
plt.clf()
plt.subplot(2, 1, 1)
plt.title(spec_data['ts'])
plt.plot(spec_data['lamb'], spec_data['spectrum'], '-')
plt.grid(1)
plt.ylabel('Spectrum / counts')

plt.subplot(2, 1, 2)
plt.semilogy(spec_data['lamb'], spec_data['spectrum'], '-')
plt.grid(1)
plt.xlabel('Wavelength / nm')
plt.ylabel('Spectrum / counts')

plt.show()