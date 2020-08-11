from setuptools import setup, Extension
from Cython.Distutils import build_ext
import numpy
import os

# Get long_description from module docstring.
# Need to strip all Sphinx ReST extensions
try:
  from andor2 import __doc__ as docstr
  d1 = docstr.replace(':class:', '')\
           .replace(':attr:', '')\
           .replace(':func:', '')\
           .replace(':mod:', '')\
           .replace(':Usage:', 'Usage\n-----')\
           .replace(':Examples:', 'Examples\n--------')\
           .replace('>>>', '    >>>')\
           .replace('<acqmode>', '')\
           .replace('-----------', '')
except:
  d1 = open(os.path.join(os.path.dirname(__file__), 'README')).read()

andor2 = Extension("andor2",
                   sources = ["andor2.pyx"],
                   library_dirs = ['.','usr/local/lib'],
                   include_dirs = ['.', '..', numpy.get_include(),'/usr/lib64/python/site-packages/Cython/Includes'],
                   libraries = ['andor'])

andor2.cython_directives = {"embedsignature": True}

# Could add SDK v3 to the package as module 'andor3' ...

setup(
    name = 'andor',
    version = '1.14',
    description = 'Object-oriented interface for Andor EMCCD cameras',
    author = 'Guillaume Lepert',
    author_email = 'guillaume.lepert07@imperial.ac.uk',
    long_description=d1,
    url="",
    cmdclass={'build_ext': build_ext},
    ext_modules = [andor2],
    requires=['numpy', 'cython', 'h5py'],
    platforms=['linux'],
    classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: C',
    'Programming Language :: Cython',
    'Programming Language :: Python :: 2.7',
    'Topic :: Home Automation',
    'Topic :: Scientific/Engineering'
]
    
)

