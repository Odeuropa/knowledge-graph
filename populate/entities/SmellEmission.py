from .Entity import Entity
from .ontologies import ODEUROPA


class SmellEmission(Entity):
    def __init__(self, seed, smell, source='', carrier='', lang='en'):
        super().__init__(seed)
        self.setclass(ODEUROPA.L12_Smell_Emission)
        self.add(ODEUROPA.F1_generated, smell)
        self.split_add(ODEUROPA.F3_had_source, source, lang)
        self.split_add(ODEUROPA.F4_had_carrier, carrier, lang)
