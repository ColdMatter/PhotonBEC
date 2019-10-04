import sys
sys.path.append("D:\\Control\\PythonPackages\\")
import pbec_ipc

port = pbec_ipc.PORT_NUMBERS["spectrometer_cavity_lock"]
host = "localhost"
#pbec_ipc.ipc_eval('s.ts',port=port,host=host)
#pbec_ipc.ipc_exec('setSetPoint(568)',port=port,host=host)
#pbec_ipc.ipc_eval('s.spec_int_time',port=port,host=host)
#pbec_ipc.ipc_exec('setSpectrometerIntegrationTime(50)',port=port,host=host)
#pbec_ipc.ipc_eval('s.lamb',port=port,host=host)
#pbec_ipc.ipc_eval('s.spectrum',port=port,host=host)
pbec_ipc.ipc_exec('s.lamb_range((540,600))',port=port,host=host)