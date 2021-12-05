from rdflib import TIME, RDFS, XSD
from .Entity import Entity
from .time_parsing import en


class Time(Entity):
    def __init__(self, label):
        super().__init__(label)
        self.setclass(TIME.TemporalEntity)
        self.add(RDFS.label, label)

    @classmethod
    def parse(cls, x):
        res = en.parse_date(x)
        if res is None:
            return None

        startDate, endDate, startType, endType = res
        t = Time(x)
        t.set_start(startDate, startType)
        t.set_end(endDate, endType)

    def set_start(self, date, type):
        self.add(TIME.hasBeginning, date, )
        pass

    def set_end(self, date, type):
        self.add(TIME.hasEnd, date, type)
        pass
