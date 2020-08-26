'''@brief Flask App to expose HTTP endpoints for interfacing with sensors/readings
'''
import os
from flask import Flask

from .platform import (
    PlatformI2c as I2c, I2cBus,
    PlatformAdc as Adc, AdcAddress, AdcChannel,
    PLATFORM_NAME
)

from .hydrometer import Hydrometer

# from .models import Sensor, SensorReading, SensorKind

HERE = os.path.abspath(os.path.dirname(__file__))

def create_app(test_config=None):
    app = Flask('sensor_app', instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # app.config.update(
    #     SQLALCHEMY_DATABASE_URI = (
    #         os.environ.get('DATABASE_URL') or
    #         'sqlite:///' + os.path.join(HERE, 'app.db')
    #     )
    #     SQLALCHEMY_TRACK_MODIFICATIONS = False
    # )

    i2c = I2c(I2cBus.BUS1)
    adc = Adc(i2c, AdcAddress.ADDR2)
    hydrometer = Hydrometer(adc, AdcChannel.CHANNEL3)

    # db = X()

    @app.route('/')
    def welcome():
        return 'We are running on %s' % PLATFORM_NAME

    @app.route('/sense')
    def poll_hydrometer():
        # FIXME: implement database write
        # FIXME: implement cron or something to hit this endpoint periodically
        value = hydrometer.poll()

        # FIXME: search the DB to see if there is a HYDROMETER already
        # if not, create one
        # sensor = Sensor(kind=SensorKind.HYDROMETER)

        # create a reading object
        # reading = SensorReading(sensor=sensor,value=value)

        # commit to DB
        # db.session.add(reading)
        # db.session.commit()

        # return result
        return '{"value": %f}' % value

    @app.route('/last')
    def get_last():
        # FIXME: implement database read
        # reading = SensorReading.get(-1)
        return '{"readings":[]}'

    @app.route('/history')
    def get_history():
        # FIXME: implement database read
        # SensorReading.
        return '{"readings":[]}'


    @app.route('/purge')
    def purge_history():
        # FIXME: implement database read
        # for reading in SensorReading.query.all():
        #     db.session.delete(reading)
        # db.session.commit()

        # for sensor in Sensor.query.all():
        #     db.session.delete(sensor)
        # db.session.commit()

        return '{"readings":[]}'


    return app
