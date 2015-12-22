import wiringpi2
import time

class Tlv5620inException(Exception):
    pass

class Tlv5620in:
    __LOAD = 17
    __MOSI = 10
    __CLK = 11

    def __init__(self, LOAD, MOSI, CLK):
        self.__LOAD = LOAD
        self.__MOSI = MOSI
        self.CLK = CLK
        wiringpi2.wiringPiSetupGpio()
        wiringpi2.pinMode(self.__LOAD, 1)
        wiringpi2.pinMode(self.__MOSI, 1)
        wiringpi2.pinMode(self.__CLK, 1)
        wiringpi2.digitalWrite(self.__LOAD, 1)

    def set(self, channel, range, value):
        if (channel < 0 or channel > 3):
            raise Tlv5620inException('Invalid channel, must be 0, 1, 2 or 3')
        if (range != 0 and range != 1):
            raise Tlv5620inException('Invalid range, must be 0 or 1')
        if (value < 0 or value > 255):
            raise Tlv5620inException('Invalid value, must be between 0-255')
        firstbyte = (channel << 1)
        firstbyte = firstbyte | range
        wiringpi2.shiftOut(self.__MOSI, self.__CLK, 1, firstbyte)
        wiringpi2.shiftOut(self.__MOSI, self.__CLK, 1, value)
        wiringpi2.digitalWrite(self.__LOAD, 0)
        wiringpi2.digitalWrite(self.__LOAD, 1)

    def __del__(self):
        for channel in range(0, 3):
            self.set(channel, 0, 0)
        wiringpi2.digitalWrite(self.__LOAD, 0)



