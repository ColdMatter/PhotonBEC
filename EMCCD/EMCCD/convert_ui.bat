@ECHO OFF
ECHO Converting GUI's
pyuic5 -x -o EMCCD_frontend_GUI.py EMCCD_frontend_GUI.ui
pyuic5 -x -o EMCCD_frontend_CameraWindow_GUI.py EMCCD_frontend_CameraWindow_GUI.ui
PAUSE