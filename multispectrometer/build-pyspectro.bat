REM added -c mingw64 to end of second line -LZ
REM BTW Took -c mingw64 out 25/7/16. See comments below
@echo off
SET VS90COMNTOOLS=%VS140COMNTOOLS%
python setup.py build_ext --inplace
REM python setup.py build_ext --inplace -c mingw64
::Original problem was python setup.py install says "error: Could not find Visual Studio 2008 in your path."
::Old solution was to use mingw64 to compile, which is not offically supported for building python extensions
::New solution: point python setup.py install to the version of visual studio which is installed (here version 14, visual studio 2015)
::How to point to appropriate vs here https://pypi.python.org/pypi/fastlmm
pause