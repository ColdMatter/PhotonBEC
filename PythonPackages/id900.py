import zmq
import sys
address = "tcp://169.254.99.143:5555"

context = zmq.Context()
tc = context.socket(zmq.REQ)
tc.connect(address)
a = tc.send(*IDN?)