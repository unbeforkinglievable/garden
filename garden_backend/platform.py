'''@brief platform abstraction layer

   All this code is written to run on a RaspberryPi or Linux
   The RaspberryPi version has hardware interfaces (i2c); Linux has sims for those interfaces
'''
import os

from .i2c import LinuxI2c, RaspberryI2c, I2cBus
from .adc import LinuxAdc, RaspberryAdc, AdcAddress, AdcChannel

if os.uname()[4].startswith('arm'):
    PLATFORM_NAME = 'Raspberry'
    PlatformI2c = RaspberryI2c
    PlatformAdc = RaspberryAdc
else:
    PLATFORM_NAME = 'Linux'
    PlatformI2c = LinuxI2c
    PlatformAdc = LinuxAdc
