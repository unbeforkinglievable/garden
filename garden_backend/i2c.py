'''@brief I2C Module
'''
import os
import binascii
import threading

from abc import ABCMeta, abstractmethod

from .utils import setup_logger

class I2cBus:
    BUS0 = 0
    BUS1 = 1

class I2c(object, metaclass=ABCMeta):
    '''@brief class for interacting with potentially many resources across a shared I2C interface
    '''
    def __init__(self, bus_id):
        '''@brief constructor
        '''
        self._id = bus_id
        self._lock = threading.RLock()
        self._logger = setup_logger()

    def write_read(self, address, register, write_data, read_length):
        '''@brief write and then read bytes to/from the desired address on the i2c bus
        '''
        with self._lock:
            self.write(address, register, write_data)
            return self.read(address, register, read_length)

    def write(self, address, register, data):
        '''@brief write bytes to the desired address on the i2c bus
        '''
        with self._lock:
            self._logger.debug('Writing 0x%02X:0x%02X 0x%s' % (address, register, binascii.hexlify(data).decode()))
            self._write(address, register, data)

    def read(self, address, register, length):
        '''@brief read bytes from the desired address on the i2c bus
        '''
        with self._lock:
            self._logger.debug('Reading 0x%02X:0x%02X' % (address, register))
            data = self._read(address, register, length)
        self._logger.debug('Read 0x%s' % binascii.hexlify(data).decode())
        return data

    def close(self):
        '''@brief cleanly close the device
        '''
        self._logger.debug('Closing')
        self._close()

    @abstractmethod
    def _write(self, address, register, data):
        '''@brief write bytes to the desired address on the i2c bus
        '''
        pass

    @abstractmethod
    def _read(self, address, register, length):
        '''@brief read bytes from the desired address on the i2c bus
        '''
        pass

    @abstractmethod
    def _close(self):
        '''@brief cleanly close the device
        '''
        pass

class RaspberryI2c(I2c):
    '''@brief version to actually use the I2C bus
    '''
    def __init__(self, bus_id):
        '''@brief constructor
        '''
        super(RaspberryI2c, self).__init__(bus_id)
        from smbus2 import SMBus
        self._bus = SMBus(bus='/dev/i2c-%d' % bus_id)

    def _write(self, address, register, data):
        self._bus.write_i2c_block_data(address, register, data)

    def _read(self, address, register, length):
        return bytes(self._bus.read_i2c_block_data(address, register, length))

    def _close(self):
        self._bus.close()

class LinuxI2c(I2c):
    '''@brief version to simulate an I2C bus, returning random information on reads
    '''
    def __init__(self, bus_id):
        '''@brief constructor
        '''
        super(LinuxI2c, self).__init__(bus_id)
        import random

    def _write(self, address, register, data):
        pass

    def _read(self, address, register, length):
        return bytes(bytearray(random.rand_int(0,0xFF) for i in range(length)))

    def _close(self):
        pass
