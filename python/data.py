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
    ref = None
    controller_id = ""
    connected = False

    def __init__(self):
        self.log = logging.getLogger("paludarium.data")
        self.log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.log.addHandler(ch)
        self.log.debug("init Data")

    def begin(self):
        self.start_firebase()

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
            self.secret = lines[1]
            self.controller_id = lines[2]
            uid = 'controller:' + self.controller_id
            auth_payload = {"controller_id": self.controller_id, "uid" : uid }
            token = create_token(self.secret, auth_payload)
            self.firebase = Firebase(self.firebaseurl, auth_token=token)
            self.ref = self.firebase.child("controllers").child(self.controller_id)
        else:
            self.log.critical("firebase file was incomplete")

    def write_status(self, path, value):
        self.ref.child(path).set(value)

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

    def connect_sse_state(self, update_receiver):
        if len(self.firebaseurl) > 0:
            # connect to firebase SSE
            self.sse = ClosableSSEClient(self.firebaseurl.rstrip("/") + "/controllers/" + self.controller_id + ".json")
            self.log.info("Connected SSE Client to Firebase")
            for msg in self.sse:
                self.log.debug("SSE Event received")
                if msg is None or msg.data is None:
                    self.log.debug("SSE Event was empty")
                    continue
                try:
                    msg_data = json.loads(msg.data)
                    path = msg_data['path']
                    data = msg_data['data']
                    self.process_sse_event(path, data)
                    update_receiver.update()
                except ValueError:
                    self.log.debug("Could not decode SSE Event")
                except TypeError:
                    self.log.debug("Could not decode SSE Event, maybe a keep-alive event")
                time.sleep(0.2);
            self.log.info("SSE Client Disconnected")

    def process_sse_event(self, path, data):
        if path == "/":
            self.state = data
            self.connected = True
        else:
            paths = path.split("/")
            last_key = paths[len(paths) - 1]
            paths = paths[1:len(paths) - 1]
            node = self.state
            for child in paths:
                if child.isdigit():
                    child = int(child)
                node = node[child]
            if last_key.isdigit():
                last_key = int(last_key)
            node[last_key] = data
        self.log.debug("data: " + self.__print_pretty(self.state))

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
