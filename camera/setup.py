from distutils.core import setup, Extension
import numpy
setup(name='pyflycap', version='1.0',
    ext_modules=[Extension('pyflycap', ['pyflycap.cpp'], include_dirs=[numpy.get_include()])])
