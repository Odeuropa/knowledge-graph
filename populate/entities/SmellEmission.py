import re

from .Entity import Entity
from .SmellSource import SmellSource
from .ontologies import ODEUROPA


class SmellEmission(Entity):
    def __init__(self, seed, smell, source='', carrier='', lang='en'):
        super().__init__(seed, 'emission')
        self.set_class(ODEUROPA.L12_Smell_Emission)
        self.add(ODEUROPA.F1_generated, smell)

        self.count_source = 0

        for x in re.split(r'(?: ?\| ?)|(?: and )', source):
            if not x or re.match(r'^\W+$', x.strip()):
                break
            s = re.sub(r'^(of|with) ', '', x.strip()).strip()

            self.add_source(s, lang)

        for x in carrier.split(' | '):
            if not x:
                break
            c = re.sub(r'^of ', '', x).strip()
            self.add_carrier(c, lang)

    def add_source(self, source, lang=None):
        if not isinstance(source, Entity):
            source = SmellSource(self.seed + str(self.count_source), source, lang)

        self.add(ODEUROPA.F3_had_source, source)
        self.count_source += 1

    def add_carrier(self, carrier, lang=None):
        if not isinstance(carrier, Entity):
            carrier = SmellSource(self.seed + str(self.count_source), carrier, lang)

        self.add(ODEUROPA.F4_had_carrier, carrier)
        self.count_source += 1
