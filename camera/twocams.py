import sys
sys.path.append("D:\\Control\\PythonPackages\\")
from pbec_experiment import *

cam1 = getCameraByLabel('chameleon')
cam2 = getCameraByLabel('flea')

figure(2), clf()
im2 = cam2.get_image()
imshow(im2)
print im2.shape

figure(1), clf()
im1 = cam1.get_image()
imshow(im1)
print im1.shape

figure(3), clf()
im1 = cam1.get_image()
imshow(im1)
print im1.shape
