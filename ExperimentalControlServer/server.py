
#toy state machine that will eventually be used as an experimental controller

import socket, threading, json
from collections import deque

import experimental_control

#binding to localhost makes it faster, but then you can only use the same machine
# bind to '' to accept anywhere, but only when its actually needed
server_address = ('localhost', 55555)
server_open = True

methods = ['initialise', 'arm', 'trigger', 'finalise', 'save']

state = 'unconfigured' ##initial state

def message_received(method, params):
	'''
	function is called when a message is received over a tcp/ip connection
	'''
	#data and metadata can come from the server connected components like cameras and spectrometers but also from client connections
	if method == 'initialise':
		#params contains configuration, a list of components and parameters to get data from
		for data_src in params['data_sources']:
			print 'datasrc=' + str(data_src)
			data_src['theglobal'] = globals()
			import pprint
			print 'globals='
			pprint.pprint(data_src['theglobal'])
			s = experimental_control.DataSource(**data_src)
			#s = experimental_control.DataSource(constructor=, init_calls=None, arm_calls=None, trigger_getdata=None, finalise_calls=None, save_calls=None)
		
		
		state = 'configured'
	elif method == 'arm':
		#set all measuring equipment ready to receive trigger
		state = 'waiting'
	elif method == 'trigger':
		#take data
		# generate timestamp
		state = 'running'
	elif method == 'finalise':
		#clean up and do immediate post processing
		state = 'ready'
	elif method == 'save':
		#save data to disk
		state = 'ready'
	print 'method = ' + method + ' => ' + state

class ClientSocketHandler(threading.Thread):
	def __init__(self, client_sock, addr, queue_lock, message_queue):
		threading.Thread.__init__(self, name='client thread')
		self.client_socket = client_sock
		self.addr = addr
		self.queue_lock = queue_lock
		self.message_queue = message_queue
		self.open = True
		self.client_fd = client_sock.makefile()
		
	def run(self):
		self.client_socket.sendall('exp-ctrl-handshake\r\n')
		ack_handshake = self.recv()
		if ack_handshake != 'exp-ctrl-handshake':
			raise IOError('no ack handshake')
			
		while self.open:
			message = self.recv()
			method = message.split()[0]
			if method not in methods:
				raise IOError('missing or invalid method: ' + str(message))
			with self.queue_lock:
				self.message_queue.append(message)
				self.queue_lock.notify()
			
	def send(self, line):
		self.client_socket.sendall(line + '\r\n')
		
	def recv(self):
		input = self.client_fd.readline()
		if input == '':
			raise EOFError()
		return input.rstrip()
		
class ServerThread(threading.Thread):
	def __init__(self, server_sock, client_list, queue_lock, message_queue):
		threading.Thread.__init__(self, name='server thread')
		self.server_sock = server_sock
		self.client_list = client_list
		self.queue_lock = queue_lock
		self.message_queue = message_queue
		self.open = True
		
	def run(self):
		while self.open:
			(client_socket, addr) = self.server_sock.accept()
			print 'accepted connection from ' + str(addr)
			client_handler = ClientSocketHandler(client_socket, addr, self.queue_lock, self.message_queue)
			client_handler.start()
			self.client_list.append(client_handler)
		
		
def create_server_socket():
	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_sock.bind(server_address)
	server_sock.listen(5)
	return server_sock
	
def main():
	queue_lock = threading.Condition()
	message_queue = deque() #use append() and popleft()

	server_sock = create_server_socket()
	client_list = []
	server_thread = ServerThread(server_sock, client_list, queue_lock, message_queue)
	server_thread.start()
	print 'started server'
	
	while server_thread.open:
		with queue_lock:
			queue_lock.wait()
			message = message_queue.popleft()
		print 'handling message ' + message
		i = message.find(' ')
		if i != -1:
			params = json.loads(message[i+1:])
		else:
			params = []
		message_received(message[:i], params)
	
	#loop waiting for a queue to get messages
	#handle message
	
		
if __name__ == "__main__":
	main()