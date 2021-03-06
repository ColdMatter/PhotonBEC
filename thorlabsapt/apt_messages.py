#A place to put all the message label for Thorlabs APT controller
#and the utilities to look up message numbers
MGMSG_MOD_IDENTIFY=0x0223

MGMSG_MOT_SET_HOMEPARAMS=0x0440
MGMSG_MOT_REQ_HOMEPARAMS=0x0441
MGMSG_MOT_GET_HOMEPARAMS=0x0442

MGMSG_MOT_MOVE_HOME=0x0443
MGMSG_MOT_MOVE_HOMED=0x0444

MSMSG_MOT_REQ_STATUSUPDATE = 0x0480
MSMSG_MOT_GET_STATUSUPDATE = 0x0481

MGMSG_MOT_SET_MOVEABSPARAMS=0x0450
MGMSG_MOT_REQ_MOVEABSPARAMS=0x0451
MGMSG_MOT_GET_MOVEABSPARAMS=0x0452

MGMSG_MOT_SET_VELPARAMS = 0x0413
MGMSG_MOT_REQ_VELPARAMS = 0x0414
MGMSG_MOT_GET_VELPARAMS = 0x0415

MGMSG_MOT_SET_JOGPARAMS = 0x0416
MGMSG_MOT_REQ_JOGPARAMS = 0x0417
MGMSG_MOT_GET_JOGPARAMS = 0x0418

MGMSG_MOT_MOVE_COMPLETED=0x0464
MGMSG_MOT_MOVE_STOP=0x0465

MGMSG_MOT_MOVE_ABSOLUTE=0x0453
MGMSG_MOT_MOVE_JOG = 0x046A
MGMSG_MOT_MOVE_RELATIVE = 0x0448

MGMSG_MOT_SET_GENMOVEPARAMS = 0x043A
MGMSG_MOT_REQ_GENMOVEPARAMS = 0x043B
MGMSG_MOT_GET_GENMOVEPARAMS = 0x043C

MGMSG_MOT_SET_BOWINDEX = 0x04F4
MGMSG_MOT_REQ_BOWINDEX = 0x04F5
MGMSG_MOT_GET_BOWINDEX = 0x04F6

MGMSG_MOT_SET_POWERPARAMS = 0x0426
MGMSG_MOT_REQ_POWERPARAMS = 0x0427
MGMSG_MOT_GET_POWERPARAMS = 0x0428



#THIS CODE GOES AT THE END OF THE FILE
#NOTE: all intermediate variables' names must start with "__" or else they'll be returned in the inverse message lookup.
import sys as __sys
__this_module = __sys.modules[__name__]
__messages = dict((k,v) for k,v in __this_module.__dict__.iteritems() if not k.startswith('__'))
__inverse_messages={v:k for k,v in __messages.items()}

#def lookup_message(message_number):
#    return inverse_messages[message_number]
