from rdflib import TIME, RDFS, XSD
from .Entity import Entity
from .time_parsing import time_parsing


class Time(Entity):
    def __init__(self, seed, label):
        super().__init__(seed)
        self.setclass(TIME.TemporalEntity)
        self.add(RDFS.label, label)
        self.start = None
        self.end = None

    @classmethod
    def parse(cls, x, lang='en', fallback=None):
        if not x:
            return None

        res = time_parsing.parse_date(x, lang)

        if res is None:
            if fallback == 'text':
                return Time(x, x)
            return None

        startDate, endDate, startType, endType = res

        t = Time(startDate, x)
        t.set_start(startDate, startType)
        t.set_end(endDate, endType)

        return t

    def set_start(self, date, type):
        self.start = date
        self.add(TIME.hasBeginning, date, type)
        pass

    def set_end(self, date, type):
        self.end = date
        self.add(TIME.hasEnd, date, type)
        pass
