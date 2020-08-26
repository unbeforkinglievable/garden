'''@brief Hydrometer module

   Hydrometer: https://www.vegetronix.com/Products/VH400

   This module contains logic for getting a hydrometer measurement
'''
from .utils import setup_logger

class Hydrometer(object):
    '''@brief class to abstract getting a reading from a hydrometer from an ADC over an I2C bus
    '''
    def __init__(self, adc, channel):
        self._adc = adc
        self._channel = channel
        self._logger = setup_logger()

    def poll(self):
        '''@brief get a measurement from the hydrometer (in Volumetric Water Content (VMC))
           @note this should return a number between 0.0 and 100.0 (it's a percentage)
        '''
        voltage = self._adc.read_single(self._channel)
        self._logger.debug('Voltage: %s' % str(voltage))

        # this voltage should now be between 0.0 and 3.0V as that's the output range of the sensor
        if voltage < 0 or voltage > 3.0:
            self._logger.error('Somehow have a bad voltage: %1.2f' % voltage)

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
    import time
    import logging
    import argparse
    from .platform import (
        PlatformI2c as I2c, I2cBus,
        PlatformAdc as Adc, AdcAddress, AdcChannel
    )

    parser = argparse.ArgumentParser(description='Test polling hydrometer')
    parser.add_argument('-v','--verbose',action='store_true',default=False,
                        help='Turn on extra logging')
    args = parser.parse_args()
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)
    i2c = I2c(I2cBus.BUS1)
    adc = Adc(i2c, AdcAddress.ADDR2)
    hydrometer = Hydrometer(adc, AdcChannel.CHANNEL3)

    try:
        while True:
            hydrometer._logger.info('VMC: %1.2f%%' % hydrometer.poll())
            time.sleep(2.0)
    except OSError:
        hydrometer._logger.error('Sensor not available; plugged in and powered?')
        raise
    except KeyboardInterrupt:
        hydrometer._logger.info('Goodbye')
    finally:
        i2c.close()


if __name__ == '__main__':
    main()
