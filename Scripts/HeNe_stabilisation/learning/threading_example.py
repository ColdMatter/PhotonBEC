#execfile("threading_example.py")
import time
from threading import Thread
import Queue
import multiprocessing

def func1(x,sleep_time=5):
    print "func1 argument: "+str(x)
    time.sleep(sleep_time)
    print "func1 finished\n"
    
def func2(y,sleep_time=5):
    print "func2 argument: "+str(y)
    time.sleep(sleep_time)
    print "func2 finished\n"

t1 = Thread(target=func1,args=("gbd",))
t1.start()
t2 = Thread(target=func2,args=("wgjsdhbvd jkdfhbd jh",))
t2.start()

time.sleep(0.01) #makes sure that the threads print out at the end
#execfile("threading_example.py")
#EoF