'''@brief Hydrometer module

   Hydrometer: https://www.vegetronix.com/Products/VH400

   This module contains logic for getting a hydrometer measurement
'''
import logging

logger = logging.getLogger('hydrometer')
logger.setLevel(logging.DEBUG)


class Hydrometer(object):
    '''@brief class to abstract getting a reading from a hydrometer from an ADC over an I2C bus
    '''
    def __init__(self, adc, channel):
        self._adc = adc
        self._channel = channel

    def poll(self):
        '''@brief get a measurement from the hydrometer (in Volumetric Water Content (VMC))
           @note this should return a number between 0.0 and 100.0 (it's a percentage)
        '''
        voltage = self._adc.read_single(self._channel)

        # this voltage should now be between 0.0 and 3.0V as that's the output range of the sensor
        if voltage < 0 or voltage > 3.0:
            logger.error('Somehow have a bad voltage: %1.2f' % voltage)

        # Taken from https://www.vegetronix.com/Products/VH400/VH400-Piecewise-Curve.phtml
        # this is a piecewise approximation to convert from voltage to Volumetric Water Content
        # 2.2V to 3.0V    VWC= 62.5*V  - 87.5
        # 1.82V to 2.2V   VWC= 26.32*V - 7.89
        # 1.3V to 1.82V   VWC= 48.08*V - 47.5
        # 1.1V to 1.3V    VWC= 25*V    - 17.5
        # 0 to 1.1V       VWC= 10*V    - 1
        segments = [
            #(minv, slope, offset)
            (2.2,  62.5,  87.50),
            (1.82, 26.32,  7.89),
            (1.3,  48.08, 47.50),
            (1.1,  25.00, 17.50),
            (0,    10.00,  1.00)
        ]
        for minv, slope, offset in segments:
            if voltage >= minv:
                break
        return (slope * voltage) - offset

def main():
    from .platform import (
        PlatformI2c as I2c, I2cBus,
        PlatformAdc as Adc, AdcAddress, AdcChannel
    )
    import time

    i2c = I2c(I2cBus.BUS1)
    adc = Adc(i2c, AdcAddress.ADDR0)
    hydrometer = Hydrometer(adc, AdcChannel.CHANNEL0)

    try:
        while True:
            print(hydrometer.poll())
            time.sleep(1.0)
    except OSError:
        logger.error('Sensor not available; plugged in and powered?')
    except KeyboardInterrupt:
        logger.info('Goodbye')
    finally:
        i2c.close()


if __name__ == '__main__':
    main()
