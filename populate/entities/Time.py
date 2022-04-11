from rdflib import TIME, RDFS, XSD
from .Entity import Entity
from .time_parsing import time_parsing


class Time(Entity):
    def __init__(self, seed, label):
        super().__init__(str(seed))
        self.seed = seed
        self.setclass(TIME.TemporalEntity)
        self.add(RDFS.label, label)
        self.start = None
        self.end = None

    @classmethod
    def parse(cls, x, lang='en', fallback=None):
        if not x:
            return None

        edtf = time_parsing.parse_date(x, lang)
        part_day = time_parsing.get_parts_of_the_day(x, lang)

        if edtf is None:
            # print(x, "=>", edtf, part_day)
            if fallback == 'text':
                t = Time(x, x)
            return None
        else:
            # print(x, edtf)
            t = Time(edtf + ''.join(part_day), edtf)
            t.compute_rdf_date()

        for pd in part_day:
            t.set_part_day(pd)

        return t

    def set_start(self, date, type):
        if not date or 'X' in date:
            return
        self.start = date
        self.add(TIME.hasBeginning, date, type)

    def set_end(self, date, type):
        if not date or 'X' in date:
            return
        self.end = date
        self.add(TIME.hasEnd, date, type)

    def compute_rdf_date(self):
        dt = time_parsing.parse_edtf(self.seed)
        # todo include info on writing time of the text
        if dt:
            start, end, startType, endType = dt
            self.set_start(start, startType)
            self.set_end(end, endType)

    def set_part_day(self, pd):
        # fixme something smarter
        self.add(RDFS.comment, pd, 'en')
