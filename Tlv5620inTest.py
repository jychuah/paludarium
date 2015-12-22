__author__ = 'jychuah'

from Tlv5620in import *
import time

print "Initializing Tlv5620in"
tlv = Tlv5620in(17, 10, 11)
print "Writing DAC A to 255"
tlv.set(0, 0, 255)
print "Waiting 20 seconds"
time.sleep(20)
print "Ending"