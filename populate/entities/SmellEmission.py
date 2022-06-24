import re

from .Entity import Entity
from .SmellSource import SmellSource
from .ontologies import ODEUROPA


class SmellEmission(Entity):
    def __init__(self, seed, smell, source='', carrier='', lang='en'):
        super().__init__(seed, 'emission')
        self.set_class(ODEUROPA.L12_Smell_Emission)
        self.add(ODEUROPA.F1_generated, smell)

        for i, x in enumerate(source.split(' | ')):
            if not x:
                break
            s = re.sub(r'^of ', '', x).strip()

            self.add(ODEUROPA.F3_had_source, SmellSource(seed + str(i), s, lang))

        for i, x in enumerate(carrier.split(' | ')):
            if not x:
                break
            c = re.sub(r'^of ', '', x).strip()
            self.add(ODEUROPA.F4_had_carrier, SmellSource(seed + str(i) + 'c', c, lang))
