# data.py
# Interfaces with WebPersistent.com to store and retrieve controller data

from firebase import firebase
from sseclient import SSEClient
import time
import threading
import json

class Data:
    state = { }
    firebase = None
    
    __FIREBASE_GET_ERROR = 0;
    __FIREBASE_EMPTY_DATASET = 1;
    __FIREBASE_EMPTY_INCOMPLETE_DATA = 2;
    
    def __init__(self):
    
    def begin(self):
        start_firebase()
    	  state = blankstate()
        fbstate = get_initial_firebase_state()
        if not fbstate is None:
        		state.update(fbstate)
        else:
            if read_config():
            	 # couldn't read firebase, found a config file
            else:
              	 # couldn't firebase, couldn't read a config file
              	 
              
            
    
    def start_firebase(self, configfile="firebase.txt"):
        lines = [line.strip() for line in open(configfile)]
        if len(lines) >= 3:
	         firebaseurl = lines[0]
   	      email = lines[1]
      	   secret = lines[2]
        		self.firebase = firebase.FirebaseApplication(firebaseurl, firebase.FirebaseAuthentication(secret, email, extra={'id': 1})
            
    def get_initial_firebase_state(self):
		  try:
				result = self.firebase.get('/state', None)
				if 'error' in result:
				    return None
		  except IOError:
				return None
		  finally:
				return result			   
                                                         
    def read_config(self):
        try:
            f = open("config.txt", "r")
            config_state = json.load(f)
        except IOError:
            return False
        finally:
          	self.state = config_state
            f.close()
            return True
            

	 def blankstate():
        state = { }
        state['status'] = { 'hostname' : 'paludarium', 'humidity' : 0, 'temperature' : 0, 'format' : 'fahrenheit', 'lights' : 'override' }
        state['channels'] = { x : 100 for x in range(4) }
        state['programs'] = { x : "program " + str(x) for x in range(5)}
        state['relays'] = { x : "off" for x in range(2) }
        state['programdata'] = { x : new_programdata() for x in range(5) }
        return state
        

	 def new_programdata():
        programdata = { 'channels' : { } }
        for x in range(4):
        		programdata['channels'].update(new_channeldata(x))         	
        return programdata
        
    
	 def new_channeldata(channelnum):
        return { channelnum : {x : 100 for x in range(0, 24* 60, 30)}}

        
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
    
