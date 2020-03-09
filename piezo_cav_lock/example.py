import sys
sys.path.append("D:\\Control\\PythonPackages\\")
import pbec_ipc






#### Example of how to externally (via IPC) check if second loop correction is activated

cavity_second_loop_server_port = pbec_ipc.PORT_NUMBERS["cavity lock second loop"]
cavity_second_loop_server_host = 'localhost'

def is_second_cavity_lock_loop_activated(port, host):
	return pbec_ipc.ipc_eval("is_second_cavity_lock_loop_activated()", port=port, host=host)


print(is_second_cavity_lock_loop_activated(port=cavity_second_loop_server_port, host=cavity_second_loop_server_host))