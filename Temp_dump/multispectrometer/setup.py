import numpy
from distutils.core import setup, Extension
setup(name='pyspectro', version='1.0',
    ext_modules=[Extension('pyspectro', ['pyspectro.cpp'], include_dirs=[numpy.get_include()])])
