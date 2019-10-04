
import pbec_ipc





if __name__ == "__main__":
	#start_server(globals())
	#import time
	#time.sleep(0.3)
	
	sock = pbec_ipc.socket_connect(pbec_ipc.PORT_NUMBERS['piezo_controller'])
	
	
	
	pbec_ipc.socket_eval(sock, 'set piezo voltage whatever')
	
	pbec_ipc.socket_close()