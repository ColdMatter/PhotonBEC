
import numpy as np
import scipy as sp
import scipy.misc

'''
im = scipy.misc.lena()
factors = [2, 4, 8, 16, 32]
'''
im = imread('hummingbird.png')
#im = im[0:120, 0:120]
#factors = [2, 3, 4, 5, 6]
im = im[54:, 103:-104]
factors = [2, 3, 8, 17, 32]
im = sum(im, 2)


def rebin2222(a, shape):
	sh = shape[0], a.shape[0]/shape[0], shape[1], a.shape[1]/shape[1]
	#print sh
	#return sh#a.reshape(sh).mean(-1).mean(1)
	return mean(a.reshape(sh),(0, 2))

def rebin1d(a, binsize):
	cutoff = a.shape[1] % binsize
	if cutoff != 0:
		a = a[:, :-cutoff]
	sh = a.shape[0], a.shape[1]/binsize, binsize
	return mean(a.reshape(sh), -1)
	
def rebin(a, shape):
	a1 = rebin1d(a, shape[0])
	return rebin1d(a1.transpose(), shape[1]).transpose()
	
figure('image'), clf()
subplot(2, 3, 1)
imshow(im)
for i, b in enumerate(factors):
	subplot(2, 3, i+2)
	i = rebin(im, (b, b))
	imshow(i)
	
