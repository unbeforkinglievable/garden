'''@brief ADC module

   ADC:        https://www.ti.com/lit/gpn/ads1015

   This module contains logic for talking to an ADC over an I2C bus
'''
import time
import struct


from abc import ABCMeta, abstractmethod

from .utils import setup_logger

class AdcAddress:
    '''@brief ADS1015 possible 7-bit I2C addresses
    '''
    ADDR0 = 0x48
    ADDR1 = 0x49
    ADDR2 = 0x4A
    ADDR3 = 0x4B

class AdcRegister:
    '''@brief ADS1015 registers
    '''
    CONVERSION = 0
    CONFIG     = 1
    LO_THRESH  = 2
    HI_THRESH  = 3

class AdcChannel:
    '''@brief ADS1015 channels
    '''
    CHANNEL0 = 0
    CHANNEL1 = 1
    CHANNEL2 = 2
    CHANNEL3 = 3
    NCHANNELS = 4

class AdcConfigRegister:
    '''@brief ADS1015 Configuration Register bits
    '''
    OS_SINGLE = 0x8000 # write to start a conversion; on read indicates if busy

    # which integration we want to do
    MUX_DIFF_0_1 = 0x0000
    MUX_DIFF_0_3 = 0x1000
    MUX_DIFF_1_3 = 0x2000
    MUX_DIFF_2_3 = 0x3000
    MUX_SINGLE_0 = 0x4000 # << this is what we want
    MUX_SINGLE_1 = 0x5000
    MUX_SINGLE_2 = 0x6000
    MUX_SINGLE_3 = 0x7000

    # what programmable gain amplifier setting we want associated with that measurement
    PGA_V6P144 = 0x0000
    PGA_V4P096 = 0x0200 # << this is what we want
    PGA_V2P048 = 0x0400
    PGA_V1P024 = 0x0600
    PGA_V0P512 = 0x0800
    PGA_V0P256 = 0x0A00

    # what mode we want (continuous/single)
    MODE_CONTINUOUS  = 0x0000
    MODE_SINGLE_SHOT = 0x0100 # << this is what we want

    # what sampling rate
    DR_1600SPS = 0x0080 # << this is what we want

    COMP_MODE_WINDOW     = 0x0010 # << we don't want this
    COMP_POL_ACTIVE_HIGH = 0x0008 # << we don't want this
    COMP_LAT_LATCH       = 0x0004 # << we don't want this
    COMP_QUEUE_ONE       = 0x0000
    COMP_QUEUE_DISABLE   = 0x0003 # << we want this

class Adc(object, metaclass=ABCMeta):
    '''@brief ADC class for the ADS1015
    '''
    def __init__(self, bus, address):
        '''@brief constructor
        '''
        self._bus = bus
        self._address = address
        self._logger = setup_logger()

    def write_register(self, register, value):
        '''@brief write a 16-bit (big-endian) value to the desired register
        '''
        self._bus.write(self._address, register, struct.pack('>H', value))

    def read_register(self, register):
        '''@brief read a 16-bit (big-endian) value from the desired register
        '''
        raw = self._read_register_raw(register)
        value = struct.unpack('>H', raw)[0]
        self._logger.debug('Raw: 0x%04X' % value)
        return value

    @abstractmethod
    def _read_register_raw(self, register):
        '''@brief abstract method so we have a hook for simulation
        '''
        pass

    def read_single(self, channel):
        '''@brief read the desired channel in single-ended mode
        '''
        if channel < AdcChannel.CHANNEL0 or channel >= AdcChannel.NCHANNELS:
            raise RuntimeError('Channel out of bounds (%d)' % channel)

        config = (
            AdcConfigRegister.OS_SINGLE |
            AdcConfigRegister.PGA_V4P096 |
            AdcConfigRegister.MODE_SINGLE_SHOT |
            AdcConfigRegister.DR_1600SPS |
            AdcConfigRegister.COMP_QUEUE_DISABLE
        )
        config |= ((channel + 4) << 12)

        self.write_register(AdcRegister.CONFIG, config)
        time.sleep(0.001) # at 1600SPS, this should take < 1ms
        raw_adc = self.read_register(AdcRegister.CONVERSION) >> 4
        self._logger.debug('Raw: 0x%04X' % raw_adc)
        if raw_adc & 0x800:
            # this is a negative number
            signed_result = raw_adc - 0x1000
        else:
            signed_result = raw_adc

        # convert from ADC reading to voltage
        # max this can read is +/- 4.096V (per config)
        # ADC has 0x7FF is the max value, which should represent 4.096V
        return signed_result * 4.096 / 2048

    def read_differential(self, source, target):
        '''@brief read the desired channel difference (if it is permissible)
        '''
        raise NotImplementedError('Implement me!')

class RaspberryAdc(Adc):
    '''@brief Raspberry version that acutally hits uses I2C
    '''
    def __init__(self, bus, address):
        '''@brief constructor
        '''
        super(RaspberryAdc, self).__init__(bus, address)

    def _read_register_raw(self, register):
        return self._bus.read(self._address, register, 2)

class LinuxAdc(Adc):
    '''@brief Linux version fo testing that plays a ramp of readings
    '''
    def __init__(self, bus, address):
        '''@brief constructor
        '''
        super(LinuxAdc, self).__init__(bus, address)
        self._register_cache = {}
        # FIXME: the Hydrometer can only really go up to v2.2 (it's saturated at that point)
        # so we could potentially decrease the PGA and get more resolution on range v0-v2.048V
        # but then we saturate the ADC a little early...so this is probably fine...we don't
        # need amazing resolution on this sensor anyway
        self._min_value = 0x0080
        self._max_value = 0x0480
        self._step = (self._max_value - self._min_value) // 32
        self._next_value = self._min_value

    def write_register(self, register, value):
        '''@brief cache desired register write so we can read it back later
        '''
        self._register_cache[register] = value
        super(LinuxAdc, self).write_register(register, value)

    def _read_register_raw(self, register):
        '''@brief read from the cache or play a ramp on the CONVERSION register
        '''
        if register == AdcRegister.CONVERSION:
            # we're reading an input; let's just play a simple ramp
            result = struct.pack('>H', self._next_value << 4)
            self._next_value += self._step
            if self._next_value >= self._max_value:
                self._next_value = self._min_value
            return result
        # we're reading a static register; let's report what is in the cache if we can
        if register not in self._register_cache:
            return struct.pack('<H', 0)
        return self._register_cache[register]
