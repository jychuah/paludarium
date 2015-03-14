# data.py

from firebase import Firebase
from sseclient import SSEClient
from requests import HTTPError
from firebase_token_generator import create_token
import requests
import time
import threading
import json

class Data:
    state = { }
    firebase = None
    sse = None
    firebaseurl = ""
    email = ""
    secret = ""


    def __init__(self):
        print("init")

    def begin(self):
        self.start_firebase()
        self.state = self.new_default_config()
        firebase_state = self.get_initial_firebase_state()
        if not firebase_state is None:
            # found and read firebase
            state.update(firebase_state)
        else:
            # couldn't find firebase, trying to read config from file
            config_state = self.read_config()
            if not config_state is None:
                # found config, updating default config
                self.state.update(config_state)

        # patch firebase with any new default data
        if not self.overwrite_firebase_state():
            print("Could not write firebase state")

        # save config to local file
        if not self.write_config(self.state):
            print("Could not write config.txt")

    def overwrite_firebase_state(self):
        if self.firebase is None:
            return False
        try:
            self.firebase.child('state').patch(self.state)
            return True
        except HTTPError:
            return False

    def start_firebase(self, configfile="firebase.txt"):
        lines = [line.strip() for line in open(configfile)]
        if len(lines) >= 3:
            self.firebaseurl = lines[0]
            self.email = lines[1]
            self.secret = lines[2]
            auth_payload = {"email": email , "uid" : "1"}
            token = create_token(secret, auth_payload)            
            self.firebase = Firebase(firebaseurl, auth_token=token)
                    
    def get_initial_firebase_state(self):
        if self.firebase is None:
            return None
        try:
            result = self.firebase.child('state').get()
            if result is None:
                return None
            if 'error' in result:
                return None
            else:
                return None
        except HTTPError:
            return None
                                                                                                             
    def read_config(self):
        try:
            f = open("config.txt", "r")
            config_state = json.load(f)
            f.close()
            return config_state
        except IOError:
            return None
        return None

    def write_config(self, state):
        try:
            f = open("config.txt", "w")
            json.dump(state, f, indent=8,sort_keys=True)
            f.close()
            return True
        except IOError:
            return False

    def new_default_config(self):
        state = { }
        state['version'] = "0.1"
        state['status'] = { 'hostname' : 'paludarium', 'humidity' : 0, 'temperature' : 0, 'format' : 'fahrenheit', 'lights' : 'override', 'currentprogram' : -1 }
        state['channels'] = { x : 100 for x in range(4) }
        state['channeldefaults'] = { x : 100 for x in range(4) }
        state['programs'] = { x : "program " + str(x) for x in range(5)}
        state['relays'] = { x : "off" for x in range(2) }
        state['programdata'] = { x : self.new_programdata() for x in range(5) }
        return state

    def new_programdata(self):
        programdata = { 'channels' : { } }
        for x in range(4):
            programdata['channels'].update(self.new_channeldata(x))          
        return programdata

    def new_channeldata(self, channelnum):
        return { channelnum : {x : 100 for x in range(0, 24* 60, 30)}}

    def log_data(self, path, value):
        if self.firebase is None:
            return False
        try:
            self.firebase.child('data').child(path).put({ 'timestamp' : { '.sv' : 'timestamp'}, 'value' : value})
            return True
        except HTTPError:
            return False

    def connect_sse(self):
        if len(self.firebaseurl) > 0:
            self.sse = ClosableSSEClient(self.firebaseurl)
            for msg in self.sse:
                if not msg is None or not msg.data is None:
                    continue
                msg_data = json.loads(msg.data)
                path = msg_data['path']
                data = msg_data['data']

    def process_sse_event(self, path, data):
        print("Processing SSE event")
        if path.find("/state") > -1:
            path = path[len('/state'):]
        node = self.state
        for child in path.split('/'):
            node = node[child]
        node.update(data)


class ClosableSSEClient(SSEClient):
    """
    Hack in some closing functionality on top of the SSEClient
    """

    def __init__(self, *args, **kwargs):
        self.should_connect = True
        super(ClosableSSEClient, self).__init__(*args, **kwargs)

    def _connect(self):
        if self.should_connect:
            super(ClosableSSEClient, self)._connect()
        else:
            raise StopIteration()

    def close(self):
        self.should_connect = False
        self.retry = 0
        # HACK: dig through the sseclient library to the requests library down to the underlying socket.
        # then close that to raise an exception to get out of streaming. I should probably file an issue w/ the
        # requests library to make this easier
        self.resp.raw._fp.fp._sock.shutdown(socket.SHUT_RDWR)
        self.resp.raw._fp.fp._sock.close()
