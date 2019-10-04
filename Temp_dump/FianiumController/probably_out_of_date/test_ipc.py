import sys
sys.path.append("Z:\\Control\\PythonPackages\\")#uncomment for ph-photonbec
#sys.path.append("D:\\People\\Vianez\\Fianium\\")#uncomment for ph-photonbec3
import pbec_ipc
port, host = pbec_ipc.PORT_NUMBERS["fianium_controller"], "localhost"

#Notes on how best to interface with the fianium_main server (which controls the GUI)
#(1) Do not try to directly connect to the fia (FianiumLaser object).
#(2) Do use the fianium_main functions which use the fia_lock mechanism

#Enable the laser
pbec_ipc.ipc_exec("enableUpdate(True)",port,host)

#Get the pulse energy
pbec_ipc.ipc_eval("getCurrentPulseEnergy()",port,host)

#Diable the laser
pbec_ipc.ipc_exec("enableUpdate(False)",port,host)

#Get the pulse energy
pbec_ipc.ipc_eval("getCurrentPulseEnergy()",port,host)


#Enable the laser again
pc=pbec_ipc.ipc_exec("enableUpdate(True)",port,host)

#Set the pulse energy
pbec_ipc.ipc_exec("setValueUpdate_pe(1100)",port,host)
