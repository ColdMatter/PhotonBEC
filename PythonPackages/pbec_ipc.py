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
PORT_NUMBERS = {'cavity_lock': DEFAULT_PORT, 'laser_controller': DEFAULT_PORT+1, 'piezo_controller': DEFAULT_PORT+2}
PORT_NUMBERS.update({'spectrometer_cavity_lock':DEFAULT_PORT+3})
PORT_NUMBERS.update({'fianium_controller':DEFAULT_PORT+4})
PORT_NUMBERS.update({'spectrometer_server':DEFAULT_PORT+5})
PORT_NUMBERS.update({'spectrometer_server V2':DEFAULT_PORT+6})
PORT_NUMBERS.update({'cavity lock second loop':DEFAULT_PORT+8})

HOST_ADDRESSES = {'ph-photonbec':'ph-photonbec.ph.ic.ac.uk'} #Renamed with .qols on 20170522
#HOST_ADDRESSES = {'ph-photonbec':'ph-photonbec.qols.ph.ic.ac.uk'} #other hosts to be added later as need be
#HOST_ADDRESSES.update({'ph-photonbec2':'ph-photonbec2.qols.ph.ic.ac.uk'})
HOST_ADDRESSES.update({'ph-photonbec2':'ph-photonbec2'})
HOST_ADDRESSES.update({'ph-photonbec3':'ph-photonbec3.ph.ic.ac.uk'})
HOST_ADDRESSES.update({'ph-photonbec3':'ph-photonbec5.ph.ic.ac.uk'})


IPC_BIN_CLIENT_GREETING = 'pbecipcbin\r\n'
IPC_TEXT_CLIENT_GREETING = 'pbecipctxt\r\n'
IPC_SERVER_HANDSHAKE = 'pbec ipc handshake. reply \'' + IPC_TEXT_CLIENT_GREETING.rstrip() + \
	'\' if you are a human. commands available: close, shutdown, eval [expr], exec [expr]. Please try to learn the difference between exec and eval which are python builtins\r\n'
IPC_SERVER_HANDSHAKE_ACK = 'starting'
	
assert len(IPC_BIN_CLIENT_GREETING) == len(IPC_TEXT_CLIENT_GREETING)
	
SOCK_RECV_BUFFER_SIZE = 4096

encoding = 'latin-1'
	
#SOME NOTES ON THE PROTOCOL
#the binary protocol works by first sending four bytes which make up an integer
# this integer is the length of the rest of the data
#e.g. '\x00\x00\x00\x0bhello world'

#the text protocol, where commands are separated by line breaks is still around
# and can be used by putty or something
	
def sock_ipc_send(using_bin, sock, sock_fd, msg):
	if using_bin:
		buf = struct.pack('>I', len(msg)) + msg.encode(encoding=encoding)
		verbose('sending bin line ' + str(buf))
		sock.sendall(buf)
	else:
		sock.sendall(msg + '\r\n')
		
def sock_ipc_recv(using_bin, sock, sock_fd):
	if using_bin:
		data = sock.recv(SOCK_RECV_BUFFER_SIZE)
		verbose("just received socket data")
		length = struct.unpack(">I", data[:4])[0]	
		data = data.decode(encoding=encoding)

		if data == None or data == '':
			verbose("raising EOF exception")
			raise EOFError()
		assert len(data) >= 4 #TODO recover from this case instead of bailing out
		
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
			result.append(dd.decode(encoding=encoding))
		verbose('returning = ' + repr(result))
		return "".join(result)[4:]
	else:
		input = sock_fd.readline()
		if input == '':
			raise EOFError()
		return input.rstrip()
	
class IPCServer(threading.Thread):
	def __init__(self, host, port, evalGlobals, threading_cond=None, threading_return=None):
		threading.Thread.__init__(self)
		verbose("Initiating ipc server")
		self.daemon = True #die if other threads have ended too
		self.address = (host, port)
		self.closed = False
		self.evalGlobals = evalGlobals
		self.using_bin = True
		self.threading_cond = threading_cond
		self.threading_var = threading_return
		
	def run(self):
		server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#binding to localhost makes it faster, but then you can only use the same machine
		# bind to '' to accept anywhere, but only when its actually needed
		if not self.threading_cond:
			server_sock.bind(self.address)
		else:
			with self.threading_cond:
				self.threading_var[0] = True
				try:
					server_sock.bind(self.address)
				except:
					self.threading_var[0] = False
				self.threading_cond.notify()
			if not self.threading_var[0]:
				return
		server_sock.listen(1)

		while not self.closed:
			verbose('accepting on ' + str(server_sock.getsockname()))
			(client_sock, addr) = server_sock.accept()
			client_fd = None
			verbose('accepted')

			try:
				client_sock.sendall(IPC_SERVER_HANDSHAKE.encode(encoding=encoding))
				handshake = client_sock.recv(len(IPC_BIN_CLIENT_GREETING)).decode(encoding=encoding)
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
					verbose("bad handshake")
					client_sock.sendall('bad handshake, try ' + IPC_CLIENT_PUTTY_GREETING)
				verbose('sending ack')
				sock_ipc_send(self.using_bin, client_sock, client_fd, IPC_SERVER_HANDSHAKE_ACK)
				
				verbose('entering repl loop:')
				while 1:
					line = sock_ipc_recv(self.using_bin, client_sock, client_fd)
					verbose('---------')
					if line == 'close':
						verbose("    close")
						raise IOError()
					elif line == 'shutdown':
						verbose("    shutdown")
						self.closed = True
						raise IOError()
					elif line.startswith('eval '):
						verbose("    eval")
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
				verbose("Exception: "+str(e))
				pass
			finally:
				client_sock.close()
				if client_fd != None:
					client_fd.close()
				verbose('closed client socket')
				
		verbose('closing server')
		server_sock.close()

def start_server(evalGlobals, port = DEFAULT_PORT, host = ''):
        #host = "" means "accept connections form anywhere"
	signal_cond = threading.Condition()
	bind_successful = [True]
	with signal_cond:
		IPCServer(host, port, evalGlobals, signal_cond, bind_successful).start()
		signal_cond.wait()
	return bind_successful[0]

def socket_connect(port = DEFAULT_PORT, host = 'localhost'):
        #Modified 25/11/16 by RAN to make non-localhost connections possible
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))
	sock.recv(len(IPC_SERVER_HANDSHAKE)) #throw away the handshake
	sock.sendall(IPC_BIN_CLIENT_GREETING.encode(encoding=encoding))
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
	try:
		sock_ipc_send(True, sock, None, 'close')
	finally:
		pass
	try:
		sock.close()
	finally:
		pass

def ipc_eval(expr, port = 'cavity_lock',host='localhost'):
	'''
	Must pass a python expression as a string
	'''
	if isinstance(port, str):
		port = PORT_NUMBERS[port]
	sock = socket_connect(port,host=host)
	ret = socket_eval(sock, expr)
	socket_close(sock)
	return ret

def ipc_exec(expr, port = DEFAULT_PORT,host='localhost'):
	'''
	Must pass a python expression as a string
	'''
	sock = socket_connect(port,host=host)
	socket_exec(sock, expr)
	socket_close(sock)

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
def ipc_get_array(arr_name,port = 'cavity_lock',host='localhost'):
	import pickle
	ipc_exec('import pickle',port=port,host=host)
	arr_local_p = ipc_eval('pickle.dumps('+arr_name+')',port=port,host=host)

	#arr_local_p = arr_local_p.decode('string_escape') # python2 ??
	#arr_local_p = arr_local_p[1:-1]
	import ast
	arr_local_p = ast.literal_eval(arr_local_p)

	return pickle.loads(arr_local_p)

'''
import hene_utils
im_raw = ipc_get_array("s.im_raw")
centre = ipc_get_array("s.centre")
x0,y0 = centre
(dx,dy) = (int(ipc_eval("s.dx")),int(ipc_eval("s.dy")))
subim = im_raw[x0-dx:x0+dx,y0-dy:y0+dy,0]
rad_prof = hene_utils.radial_profile(subim,(dx,dy))
figure(1),clf(),plot(rad_prof)
figure(2),clf(),imshow(subim)
'''