::@echo off
g++ -c -o gFlyCapture2Test.o -I .\..\..\include\ FlyCapture2Test.cpp
g++ -o gFlyCapture2Test.exe gFlyCapture2Test.o  .\..\..\lib\FlyCapture2d_v110.lib .\..\..\lib\FlyCapture2_v110.lib
pause