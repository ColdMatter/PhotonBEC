import sys
sys.path.append("Y:/Control/PythonPackages/")



import piezo_controller_server

pzt_server = piezo_controller_server.PiezoControllerServer(globals())

pzt_server.setXvolts(11.2)