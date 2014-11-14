REM added -c mingw64 to end of second line -LZ
@echo off
python setup.py build_ext --inplace -c mingw64
pause