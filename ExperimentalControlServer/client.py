
import socket, json, time

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('localhost', 55555))
	sock_fd = sock.makefile()
	
	sock.sendall('exp-ctrl-handshake\r\n')
	sock.recv(len('exp-ctrl-handshake\r\n')) #throw away the handshake
	
	params = {'data_sources': [{'constructor': 'pbece.getCameraByLabel("flea")',
		'init_calls': ['self.source.set_max_region_of_interest()'], 'arm_calls': [],
		'trigger_getdata': [], 'finalise_calls': [], 'save_calls': []}]}
	sock.sendall('initialise ' + json.dumps(params) + '\r\n')
	sock
	
	time.sleep(2)

		
if __name__ == "__main__":
	main()