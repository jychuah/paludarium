# data.py

from firebase import Firebase
from sseclient import SSEClient
from requests import HTTPError
from firebase_token_generator import create_token
import requests
import time
import threading
import json
from exceptions import ValueError
import logging

class Data:
    state = { }
    firebase = None
    sse = None
    firebaseurl = ""
    email = ""
    secret = ""
    log = None
    callbacks = { }

    def __init__(self):
        self.log = logging.getLogger("paludraium.data")
        self.log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.log.addHandler(ch)
        self.log.debug("init Data")

    def begin(self):
        self.start_firebase()
        self.state = self.new_default_config()
        firebase_state = self.get_initial_firebase_state()
        self.log.debug("Firebase state after get_initial_firebase_state: " + self.__print_pretty(firebase_state))
        if not firebase_state is None:
            # found and read firebase
            self.state.update(firebase_state)
            self.log.debug("Updated local state from Firebase" + self.__print_pretty(self.state))
        else:
            # couldn't find firebase, trying to read config from file
            self.log.debug("Could not connect to Firebase, attempting to read local config")
            config_state = self.read_config()
            if not config_state is None:
                # found config, updating default config
                self.log.debug("Updating local state from config file")
                self.state.update(config_state)
            else:
                self.log.info("Could not read a Firebase configuration or a local configuration. Creating default configuration.")

        # patch firebase with any new default data
        self.log.debug("Attempting to write complete local state to Firebase")
        if not self.overwrite_firebase_state():
            self.log.info("Could not write local state to Firebase")

        # save config to local file
        self.log.debug("Writing local state to local configuration file")
        if not self.write_config(self.state):
            self.log.info("Could not write local state to local configuration file")

    def register_callback(self, path, callback):
        callbacks[path] = callback

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
            auth_payload = {"email": self.email , "uid" : "1"}
            token = create_token(self.secret, auth_payload)
            self.firebase = Firebase(self.firebaseurl, auth_token=token)
                    
    def get_initial_firebase_state(self):
        if self.firebase is None:
            self.log.debug("get_initial_firebase_state: No Firebase connection available")
            return None
        try:
            result = self.firebase.child('state').get()
            if result is None:
                return None
            if 'error' in result:
                return None
            else:
                return result
        except HTTPError:
            return None

    def read_config(self):
        try:
            f = open("config.txt", "r")
            config_state = json.load(f)
            f.close()
            return config_state
        except (IOError, ValueError):
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
        state['status'] = { 'version' : '0.1', 'hostname' : 'paludarium', 'humidity' : 0, 'temperature' : 0  }
        state['status']['channels'] = { x : 100 for x in range(4) }
        state['control'] = { 'format' : 'fahrenheit', 'lights' : 'override', 'current_program' : -1 }
        state['control']['relays'] = { x : "off" for x in range(2) }
        state['control']['override_values'] = { x : 100 for x in range(4) }
        state['programs'] = { x : "program " + str(x) for x in range(5)}
        state['program_data'] = { x : self.new_programdata() for x in range(5) }
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

    def connect_sse_state(self):
        if len(self.firebaseurl) > 0:
            # connect to firebase SSE
            self.sse = ClosableSSEClient(self.firebaseurl.rstrip("/") + "/state.json")
            self.log.info("Connected SSE Client to Firebase")
            for msg in self.sse:
                self.log.debug("SSE Event received")
                if msg is None or msg.data is None:
                    self.log.debug("SSE Event was empty")
                    continue
                self.log.debug("Got valid SSE Event: " + msg.dump())
                try:
                    msg_data = json.loads(msg.data)
                    path = msg_data['path']
                    data = msg_data['data']
                    self.process_sse_event(path, data)
                except ValueError:
                    self.log.debug("Could not decode SSE Event")
                except TypeError:
                    self.log.debug("Could not decode SSE Event, maybe a keep-alive event")

    def process_sse_event(self, path, data):
        if not path == "/":
            for key in callbacks.keys():
                if key in path:
                    callbacks[key](path, data)

    def __print_pretty(self, data):
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


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

d = Data()
d.begin()
d.connect_sse_state()