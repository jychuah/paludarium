# data.py
# Interfaces with WebPersistent.com to store and retrieve controller data

from WebPersistent import WebPersistent
import time
import threading
import json

class Data:
    state = { 'Temperature': 0, 'Humidity': 0, 'Fans': 'off', 'Lights': 'override',
                'Channels' : [[10] * (24 * 60 / 30)] * 4}    
    __running = False
    __getting = False
    __posting = False
    __workerThread = None
    __wp = None
    
    def __init__(self, configfile="config.txt"):
        self.__wp = WebPersistent()
        lines = [line.strip() for line in open(configfile)]
        self.__wp.device = lines[0]
        self.__wp.getkey = lines[1]
        self.__wp.postkey = lines[2]
        
    def begin(self):
        print "Data thread beginning"
        self.__running = True
        self.__workerThread = threading.Thread(target=self.__threadWorker)
        self.__workerThread.start()
        

    def __threadWorker(self):
        while (self.__running):
            if not self.__posting:
                self.__getting = True
                self.__wp.get()
                self.__getting = False
                print self.__wp.status
                print self.__wp.response
                self.__processResponse(self.__wp.response)
                time.sleep(5)

    def __processResponse(self, response):
        changed = false
        webstate = json.loads(self.__wp.response)
        for key in webstate.keys():
            if key == 'Channels':
                for channel in range(min(len(self.state['Channels']), len(webstate['Channels']))):
                    if not self.state['Channels'][channel] == webstate['Channels'][channel]:
                        self.state['Channels'][channel] = webstate['Channels'][channel]
                        changed = true
            else:    
                if key in self.state:
                    if not self.state[key] == webstate[key]:
                        self.state[key] = webstate[key]
                        changed = true
        return changed

    def postState(self):
        dump = json.dumps(state, separators=(',',':'))
        self.__posting = True
        self.__wp.post(dump)
        slef.__posting = False
        return self.__wp.status == 200
    
