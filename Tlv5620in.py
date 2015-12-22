import wiringpi2
import time

LOAD = 17
MOSI = 10
CLK = 11

wiringpi2.wiringPiSetupGpio()

wiringpi2.pinMode(LOAD, 1)
wiringpi2.pinMode(MOSI, 1)
wiringpi2.pinMode(CLK, 1)
wiringpi2.digitalWrite(LOAD, 1)

print "output 255"
wiringpi2.shiftOut(MOSI, CLK, 1, 0)
wiringpi2.shiftOut(MOSI, CLK, 1, 128)
wiringpi2.digitalWrite(LOAD, 0)
wiringpi2.digitalWrite(LOAD, 1)
print "wait 10"
time.sleep(10)
print "output 0"
wiringpi2.shiftOut(MOSI, CLK, 1, 0)
wiringpi2.shiftOut(MOSI, CLK, 1, 0)
wiringpi2.digitalWrite(LOAD, 0)
wiringpi2.digitalWrite(LOAD, 1)
print "wait 10"
time.sleep(10)
