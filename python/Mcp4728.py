# Mcp4728.py
#
# Library for controlling an Mcp4728 I2C Digital Analog Converter IC
# This is a port of an Arduino driver written for the same IC by NeuroElec
# The original code can be found at:
# https://code.google.com/p/neuroelec/source/browse/trunk/libraries/Arduino%2022/mcp4728

import numpy as np
from smbus import SMBus
class Mcp4728:

        __bus = None
        
        __defaultvdd = 5000
        __BASE_ADDR = 0x60
        __RESET = 0B00000110
        __WAKE = 0B00001001
        __UPDATE = 0B00001000
        __MULTIWRITE = 0B01000000
        __SINGLEWRITE = 0B01011000
        __SEQWRITE = 0B01010000
        __VREFWRITE = 0B10000000
        __GAINWRITE = 0B11000000
        __POWERDOWNWRITE = 0B10100000
        __GENERALCALL = 0B0000000
        __GAINWRITE = 0B11000000

        __dev_address = np.uint8(0)
        __deviceid = np.uint8(0B1100)
        __vdd = np.uint16(0)
        __vOut = np.uint16([0 ,0, 0, 0])
        __values = np.uint16([0, 0, 0, 0])
        __valuesEp =  np.uint16([0, 0, 0, 0])
        __intVref = np.uint8([0, 0, 0, 0])
        __intVrefEp = np.uint8([0, 0, 0, 0])
        __gain = np.uint8([0, 0, 0, 0])
        __gainEp = np.uint8([0, 0, 0, 0])
        __powerDown = np.uint8([0, 0, 0, 0])
        __powerDownEp = np.uint8([0, 0, 0, 0])

        def __init__(self, deviceID):
                __deviceid = deviceID
                __dev_address = (BASE_ADDR | __deviceID)
                __vdd = defaultVDD;

        def begin(self):
                __bus = SMBus(1)
                __getStatus()

        def reset(self):
                return __simpleCommand(__RESET)

        def update(self):
                return __simpleCommand(__UPDATE)

        def analogWrite(self, value1, value2, value3, value4):
                __values = np.uint16([value1, value2, value3, value4])
                return __fastWrite()

        def analogWrite(self, channel, value):
                __values[channel] = np.uint16(value)
                return __fastWrite()

        def eepromWrite(self, channel, value):
                __values[channel] = np.uint16(value)
                __valuesEp[channel] = np.uint16(value)
                return __singleWrite(channel)

        def eepromWrite(self, value1, value2, value3, value4):
                __valuesEp[0], __values[0] = np.uint16(value1)
                __valuesEp[1], __values[1] = np.uint16(value2)
                __valuesEp[2], __values[2] = np.uint16(value3)
                __valuesEp[3], __values[3] = np.uint16(value4)
                return __seqWrite()

        def eepromWrite(self):
                return __seqWrite()

        def eepromReset(self):
                __values = np.uint16([0, 0, 0, 0])
                __intVref = np.uint8([0, 0, 0, 0])
                __gain = np.uint8([0, 0, 0, 0])
                __powerDown = np.uint8([0, 0, 0, 0])
                return __seqWrite()

        def setVref(self, value1, value2, value3, value4):
                __intVref = np.uint8([value1, value2, value3, value4])
                return __writeVref()

        def setVref(self, channel, value):
                __intVref[channel] = np.uint8(value)
                return __writeVref()

        def setGain(self, value1, value2, value3, value4):
                __gain = np.uint8([value1, value2, value3, value4])
                return __writeGain()

        def setGain(self, channel, value):
                __gain[channel] = np.uint8(value)
                return __writeGain()

        def setPowerDown(self, value1, value2, value3, value4):
                __powerDown = np.uint8([value1, value2, value3, value4])
                return __writePowerDown()

        def setPowerDown(self, channel, value):
                __powerDown[channel] = np.uint8(value)
                return __writePowerDown()

        def getId(self):
                return __deviceID

        def getVref(self, channel):
                return __intVref[channel]

        def getGain(self, channel):
                return __gain[channel]

        def getPowerDown(self, channel):
                return __powerDown[channel]

        def getValue(self, channel):
                return __values[channel]

        def getVrefEp(self, channel):
                return __intVrefEp[channel]

        def getGainEp(self, channel):
                return __gainEp[channel]

        def getPowerDownEp(self, channel):
                return __powerDownEp[channel]

        def getValueEp(self, channel):
                return __valeuEp[channel]

        def vdd(self, currentVdd):
                __vdd = currentVdd

        def getVout(self, channel):
                vref = np.uint32(0)
                if (__intVref[channel] == 1):
                        vref = np.uint32(2048)
                else:
                        vref = __vdd
                vOut = np.uint32(vref * __values[channel] * (__gain[channel] + 1) / 4096);
                if (vOut > _vdd):
                        vOut = np.uint32(__vdd)
                return vOut

        def voutWrite(self, value1, value2, value3, value4):
                __vOut = np.uint16([value1, value2, value3, value4])
                __writeVout()

        def voutWrite(self, channel, vout):
                __vOut[channel] = np.unit16(vout)
                __writeVout()

        def __getStatus(self):
                status = 0
                try:
                        byteData = __bus.read_i2c_block_data(__dev_address, 0, 24)
                        for x in range(8):
                                deviceID = byteData[x * 3 + 0]
                                hiByte = byteData[x * 3 + 1]
                                loByte = byteData[x * 3 + 2]

                                isEEPROM = (deviceID & 0B00001000) >> 3
                                channel = (deviceID & 0B00110000) >> 4
                                if isEEPROM == 1:
                                        __intVrefEp[channel] = np.uint8((hiByte & 0B10000000) >> 7)
                                        __gainEp[channel] =  np.uint8((hiByte & 0B00010000) >> 4)
                                        __powerDownEp[channel] = np.uint8((hiByte & 0B01100000) >> 5)
                                        __valuesEp[channel] = np.uint16((hiByte & 0B00001111) << 8 | loByte)
                                else:
                                        __intVref[channel] = np.uint8((hiByte & 0B10000000) >> 7)
                                        __gain[channel] = np.uint8((hiByte & 0B00010000) >> 4)
                                        _powerDown[channel] = np.uint8((hiByte & 0B01100000) >> 5)
                                        __values[channel] = np.uint16((hiByte & 0B00001111) << 8 | loByte)
                except IOError:
                        status = 4
                finally:
                        return status

        def lowByte(self, value):
                return np.uint8(value & 255)
        def highByte(self, value):
                return np.uint8(value >> 8)
        
        def __fastWrite(self):
                status = 0
                try:
                        for val in __values:
                                bus.write_byte(__dev_address, highByte(val))
                                bus.write_byte(__dev_address, lowByte(val))
                except IOError:
                        status = 4
                finally:
                        return status

        def __multiWrite(self):
                status = 0
                try:
                        for channel in range(4):
                                bus.write_byte(__dev_address, np.uint8(MULTIWRITE | (channel << 1)))
                                bus.write_byte(__dev_address, np.uint8(__intVref[channel] << 7 | __powerDown[channel] << 5 | __gain[channel] << 4 | highByte(__values[channel])))
                                bus.write_byte(__dev_address, np.uint8(lowByte(__values[channel])))
                except IOError:
                        status = 4
                finally:
                        return status

        def __singleWrite(self, channel):
                status = 0
                try:
                        bus.write_byte(__dev_address, SINGLEWRITE | np.uint8(channel) << 1)
                        bus.write_byte(__dev_address, __intVref[channel] << 7 | __powerDown[channel] << 5 | __gain[channel] << 4 | highByte(__values[channel]))
                        bus.write_byte(__dev_address, lowByte(_values[channel]))
                except IOError:
                        status = 4
                finally:
                        return status


        def __seqWrite(self):
                status = 0
                try:
                        for channel in range(4):
                                bus.write_byte(__dev_address, __intVref[channel] << 7 | __powerDown[channel] << 5 | __gain[channel] << 4 | highByte(__values[channel]))
                                bus.write_byte(__dev_address, lowByte(__values[channel]))
                except IOError:
                        status = 4
                finally:
                        return status

        
        def __writeVref(self):
                status = 0
                try:
                        bus.write_byte(__dev_address, VREFWRITE | __intVref[0] << 3 | __intVref[1] << 2 | __intVref[2] << 1 | __intVref[3])
                except IOError:
                        status = 4
                finally:
                        return status

        def __writeGain(self):
                status = 0
                try:
                        bus.write_byte(__dev_address, GAINWRITE | __gain[0] << 3 | __gain[1] << 2 | __gain[2] << 1 | __gain[3])
                except IOError:
                        status = 4
                finally:
                        return status

        def __writePowerDown(self):
                status = 0
                try:
                        bus.write_byte(__dev_address, POWERDOWNWRITE | __powerDown[0] << 2 | __powerDown[1])
                        bus.write_byte(__dev_address, __powerDown[2] << 6 | __powerDown[3] << 4)
                except IOError:
                        status = 4
                finally:
                        return status

        def __writeVout(self):
                for channel in range(4):
                        if __intVref[channel] == 1:
                                __values[channel] = np.uint16(__vOut[channel] / (__gain[channel] + 1) * 2)
                        else:
                                __values[channel] = np.uint16(np.uint32(__vOut[channel] * 4096) / __vdd)
                __fastWrite()

        def __simpleCommand(self, cmd):
                status = 0
                try:
                        bus.write_byte(GENERALCALL, cmd)
                except IOError:
                        status = 4
                finally:
                        return status
        
