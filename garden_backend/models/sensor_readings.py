import enum
import datetime

from . import db

class SensorKind(enum.Enum):
    HYDROMETER = 0

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    kind = db.Column(db.Integer, index=True)

    def __repr__(self):
        return '<%s %s:%s>' % (
            type(self).__name__,
            [k for k,v in SensorKind.__members.items() if v.value=self.kind][0],
            self.id
        )

class SensorReading(db.Model):
    id = db.Colum(db.DateTime, primary_key=True, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    sensor = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    value = db.Column(db.Float)

    def __repr__(self):
        return '<%s %s %s %1.2f>' % (
            type(self).__name__,
            self.timestamp,
            repr(self.sensor),
            self.value
        )
