from rdflib import TIME, RDFS
from .Entity import Entity
from durations import Duration
from durations.exceptions import InvalidTokenError


class Time(Entity):
    def __init__(self, label):
        super().__init__(label)
        self.setclass(TIME.TemporalEntity)
        self.add(RDFS.label, label)

    @classmethod
    def parse(cls, x):
        try:
            d = Duration(x)
            print(x, d, d.to_hours())
        except InvalidTokenError as err:
            pass