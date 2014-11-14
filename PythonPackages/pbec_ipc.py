#coded by Jakov Marelic 9/2014

#this module is for including into some experiment or script to allow for easy interprocess communication
#run pbec_ipc.start_server(globals(), port = my_port_here) on the running script
#then use pbec_ipc.ipc_eval('python expression here', my_port_here) in the experiment to evaluate python expressions
#e.g.
# for cavity_lock.py I start a server and then evaluate 's.ring_rad' to get the value for the detected ring radius
#the protocol is plaintext and can be also done by a human using putty.
# set Connection Type: Raw, Hostname: localhost, Port: your_port_here

import socket
import threading
import struct

#uncomment to get messages of how the server is doing
def verbose(l):
	#print('[ipc] ' + str(l))
	pass

#high port number (> 1024)
#unique one for each service, good starting point is 
# the molar mass of rhodamine 6g
#avoid anything already well known http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
DEFAULT_PORT = 47902
#TODO write a dictionary mapping names to ports, then start_server() with a name instead of unmaintainable port numbers

IPC_BIN_CLIENT_GREETING = 'pbecipcbin\r\n'
IPC_TEXT_CLIENT_GREETING = 'pbecipctxt\r\n'
IPC_SERVER_HANDSHAKE = 'pbec ipc handshake. reply \'' + IPC_TEXT_CLIENT_GREETING.rstrip() + \
	'\' if you are a human. commands available: close, shutdown, eval [expr], exec [expr]. Please try to learn the difference between exec and eval which are python builtins\r\n'
IPC_SERVER_HANDSHAKE_ACK = 'starting'
	
assert len(IPC_BIN_CLIENT_GREETING) == len(IPC_TEXT_CLIENT_GREETING)
	
SOCK_RECV_BUFFER_SIZE = 4096
	
#SOME NOTES ON THE PROTOCOL
#the binary protocol works by first sending four bytes which make up an integer
# this integer is the length of the rest of the data
#e.g. '\x00\x00\x00\x0bhello world'

#the text protocol, where commands are seperated by line breaks is still around
# and can be used by putty or something
	
def sock_ipc_send(using_bin, sock, sock_fd, msg):
	if using_bin:
		buf = struct.pack('>I', len(msg)) + msg
		verbose('sending bin line ' + str(buf))
		sock.sendall(buf)
	else:
		sock.sendall(msg + '\r\n')
		
def sock_ipc_recv(using_bin, sock, sock_fd):
	if using_bin:
		data = sock.recv(SOCK_RECV_BUFFER_SIZE)
		if data == None or data == '':
			raise EOFError()
		assert len(data) >= 4 #TODO recover from this case instead of bailing out
		length = struct.unpack(">I", data[:4])[0]
		verbose('len(data)=%d length=%d' % (len(data), length))
		if len(data) - 4 == length:
			verbose('ipc_recv returned immediately')
			return data[4:]
		i = len(data) - 4
		result = [data]
		while i < length:
			dd = sock.recv(min(SOCK_RECV_BUFFER_SIZE, length - i))
			if dd == None or dd == '':
				raise EOFError()
			i += len(dd)
			result.append(dd)
		verbose('returning = ' + repr(result))
		return "".join(result)[4:]
	else:
		input = sock_fd.readline()
		if input == '':
			raise EOFError()
		return input.rstrip()
	
class IPCServer(threading.Thread):
	def __init__(self, host, port, evalGlobals):
		threading.Thread.__init__(self)
		self.daemon = True #die if other threads have ended too
		self.address = (host, port)
		self.closed = False
		self.evalGlobals = evalGlobals
		self.using_bin = True
		
	def run(self):
		server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#binding to localhost makes it faster, but then you can only use the same machine
		# bind to '' to accept anywhere, but only when its actually needed
		server_sock.bind(self.address)
		server_sock.listen(1)

		while not self.closed:
			verbose('accepting')
			(client_sock, addr) = server_sock.accept()
			client_fd = None
			verbose('accepted')

			try:
				client_sock.sendall(IPC_SERVER_HANDSHAKE)
				handshake = client_sock.recv(len(IPC_BIN_CLIENT_GREETING))
				if handshake == None or handshake == '':
					raise EOFError()
				if handshake.rstrip() == IPC_BIN_CLIENT_GREETING.rstrip():
					verbose('bin protocol')
					self.using_bin = True
				elif handshake.rstrip() == IPC_TEXT_CLIENT_GREETING.rstrip():
					verbose('text protocol')
					self.using_bin = False
					client_fd = client_sock.makefile()
				else:
					client_sock.sendall('bad handshake, try ' + IPC_CLIENT_PUTTY_GREETING)
				verbose('sending ack')
				sock_ipc_send(self.using_bin, client_sock, client_fd, IPC_SERVER_HANDSHAKE_ACK)
				
				verbose('entering repl loop')
				while 1:
					line = sock_ipc_recv(self.using_bin, client_sock, client_fd)
					if line == 'close':
						raise IOError()
					elif line == 'shutdown':
						self.closed = True
						raise IOError()
					elif line.startswith('eval '):
						ec = line[5:]
						try:
							ret = eval(ec, self.evalGlobals)
							sock_ipc_send(self.using_bin, client_sock, client_fd, repr(ret))
						except Exception as e:
							sock_ipc_send(self.using_bin, client_sock, client_fd, repr(e))
					elif line.startswith('exec '):
						ec = line[5:]
						try:
							exec(ec, self.evalGlobals)
							sock_ipc_send(self.using_bin, client_sock, client_fd, "done")
						except Exception as e:
							sock_ipc_send(self.using_bin, client_sock, client_fd, repr(e))
					verbose('=> ' + line)
			except Exception as e:
				#print repr(e)
				pass
			finally:
				client_sock.close()
				if client_fd != None:
					client_fd.close()
				verbose('closed client socket')
				
		verbose('closing server')
		server_sock.close()

def start_server(evalGlobals, port = DEFAULT_PORT, host = 'localhost'):
	IPCServer(host, port, evalGlobals).start()

def socket_connect(port = DEFAULT_PORT):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('localhost', port))
	sock.recv(len(IPC_SERVER_HANDSHAKE)) #throw away the handshake
	sock.sendall(IPC_BIN_CLIENT_GREETING)
	ack = sock_ipc_recv(True, sock, None)
	if ack != IPC_SERVER_HANDSHAKE_ACK:
		sock.close()
		return None
	return sock

def socket_eval(sock, expr):
	sock_ipc_send(True, sock, None, 'eval ' + expr)
	return sock_ipc_recv(True, sock, None)

def socket_exec(sock, expr):
	sock_ipc_send(True, sock, None, 'exec ' + expr)
	return sock_ipc_recv(True, sock, None)

def socket_close(sock):
	sock_ipc_send(True, sock, None, 'close')
	sock.close()

def ipc_eval(expr, port = DEFAULT_PORT):
	'''
	Must pass a python expression as a string
	'''
	sock = socket_connect(port)
	ret = socket_eval(sock, expr)
	socket_close(sock)
	return ret

def ipc_exec(expr, port = DEFAULT_PORT):
	'''
	Must pass a python expression as a string
	'''
	sock = socket_connect(port)
	socket_exec(sock, expr)
	socket_close(sock)
	
'''
from numpy.random import rand
im = rand(1000, 1000, 3)
import pickle
ims = pickle.dumps(im)
#print 'ims = ' + str(ims)
'''

if __name__ == "__main__":
	#start_server(globals())
	#import time
	#time.sleep(0.3)
	
	print('downloading the image from cavitylock')
	
	import pickle
	ipc_exec('import pickle')
	im_raw_p = ipc_eval('pickle.dumps(s.im_raw)')
	im_raw_p = im_raw_p.decode('string_escape')
	im_raw_p = im_raw_p[1:-1]
	im_raw = pickle.loads(im_raw_p)
	
	import scipy.misc
	scipy.misc.imsave('cavitylock.png', im_raw)
	

#NOTES FROm 13/11/14
"""
Serializing numpy 2D arrays is non trivial. Can try
from pbec_ipc import *
import pickle
ipc_exec("import pickle")
#d =ipc_eval("pickle.dumps(s.im_raw)")
##d =ipc_eval("pickle.dumps(s.im_raw).replace('\n','LINEBREAK')")
##d2 = d.replace('LINEBREAK','\n')
d =ipc_eval("pickle.dumps(s.im_raw).encode('string-escape')")
d2 = d.decode('string-escape')
im_raw = pickle.loads(d2)
#Still may fail...
"""
import numpy
def array_to_string(a):
	#Implemented in pbec_ipc
	#Seems to work OK, and human readably, but not so easy to machine-parse (deserialize) the result
	nd = numpy.ndim(a)
	if nd==1:
		s = str(list(a)) #handle 1D arrays
	else:
		###s = str(list([array_to_string(x) for x in a])) #handle 2D arrays
		s = ""
		s = str(list([array_to_string(x) for x in a])) #handle 2D arrays
	return s

def array_from_string(s):
	#Implemented in pbec_ipc, up to rank-3 arrays
	#Currently not working
	s1 = s.split("[")[2:]
	#handle the first line only. Handles 1D arrays to, I guess
	array(eval("["+s1[0].split("', '")[0]))
	a = array([0.0])#NOT WORKING YET	
	return a
	