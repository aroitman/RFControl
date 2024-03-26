from pcaspy import SimpleServer, Driver
import random
import math
import time
from epics import PV
from . import config

start_time = time.time()
prefix = config.epics_prefix
pvdb = {'setVoltage':{'prec':10}, 'setCurrent':{'prec':10}, 'setFrequency':{'prec':10}, 'setPSState':{'prec':10}, 'setSWState':{'prec':10}, 'getVoltage':{'prec':10}, 'getCurrent':{'prec':10}, 'getFrequency':{'prec':10}, 'getVoltageLimit':{'prec':10}, 'getCurrentLimit':{'prec':10}, 'getSWState':{'prec':10}, 'getInterlock':{'type':'enum', "enums":["OFF", "ON"]}, 'getFullRange':{'type':'enum', 'enums':['OFF', 'ON']}, 'getPSUState':{'type':'enum', 'enums':['OFF', 'ON']}, 'isRunning':{'type':'enum', 'enums':['NO', 'YES'], 'scan':0.1 }, 'isMatching':{'type':'enum', 'enums':['NO', 'YES'], 'scan':0.1}}

class myDriver(Driver):
    def __init__(self):
        super(myDriver, self).__init__()

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()
    print("EPICS server started.")
    while True:
        server.process(0.1)



