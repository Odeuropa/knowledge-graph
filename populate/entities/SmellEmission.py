from .Entity import Entity
from .ontologies import ODEUROPA
from . import vocab_api as VocabAPI


class SmellEmission(Entity):
    def __init__(self, seed, smell, source='', carrier='', lang='en'):
        super().__init__(seed)
        self.setclass(ODEUROPA.L12_Smell_Emission)
        self.add(ODEUROPA.F1_generated, smell)
        self.split_add(ODEUROPA.F3_had_source, VocabAPI.interlink('olfactory-objects', source, lang), lang)
        self.split_add(ODEUROPA.F4_had_carrier, VocabAPI.interlink('olfactory-objects', carrier, lang), lang)
