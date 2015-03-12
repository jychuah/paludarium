#
# WebPersistent.py
# 
# A library for writing to and reading from WebPersistent.com
# 
# support@webpersistent.com
# 
# Requires python-requests
# 
# Example:
# 
# from WebPersistent import WebPersistent
#
# wp = WebPersistent()
# wp.device = "yourdevice"
# wp.getkey = "your get key"
# wp.postkey = "your post key"
# wp.post("a string i really should base64 encode")
# wp.get()
# print wp.status
# print wp.response

import requests
import hmac
import hashlib
import time

class WebPersistent:
        def __init__(self):
                self.device = ""
                self.getkey = ""
                self.postkey = ""
                self.status = 0
                self.response = ""
        def __generateUrl(self, method="GET", data=None):
                signature = ""
                key = ""
                if (method == "GET"):
                        key = self.getkey
                else:
                        key = self.postkey
                if (len(key) > 0):
                        utc_time = str(long(time.time()))
                        message = method + " device=" + self.device + "&timestamp=" + utc_time
                        if (method == "POST"):
                                message = message + "&data=" + postdata
                        signature = "/" + utc_time + "/" + hmac.new(key,message, digestmod=hashlib.md5).hexdigest()
                url = "http://www.webpersistent.com/devices/"
                url = url + self.device + signature
                return url
        def get(self):
                self.status = 0
                self.response = ""
                try:
                        r = requests.get(self.__generateUrl())
                        self.status = r.status_code
                        self.response = r.text
                except requests.exceptions.ConnectionError:
                        self.status = 403
                        self.response = "Connection Refused"
        def post(self, postdata):
                self.status = 0
                self.response = ""
                try:
                        r = requests.post(self.__generateUrl("POST", data=postdata), data=postdata, headers={'content-type':'text/plain'})
                        self.status = r.status_code
                        self.response = r.text
                except requests.exceptions.ConnectionError:
                        self.status = 403
                        self.response = "Connection Refused"
