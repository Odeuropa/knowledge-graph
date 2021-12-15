import re
from .Entity import Entity
from .ontologies import ODEUROPA
from .utils import vocab_api as VocabAPI


class SmellEmission(Entity):
    def __init__(self, seed, smell, source='', carrier='', lang='en'):
        super().__init__(seed)
        self.setclass(ODEUROPA.L12_Smell_Emission)
        self.add(ODEUROPA.F1_generated, smell)

        for x in source.split('|'):
            if not x:
                break
            s = re.sub(r'^of ', '', x)
            self.add(ODEUROPA.F3_had_source, VocabAPI.interlink('olfactory-objects', s, lang), lang)
        for x in carrier.split('|'):
            if not x:
                break
            c = re.sub(r'^of ', '', x)
            self.split_add(ODEUROPA.F4_had_carrier, VocabAPI.interlink('olfactory-objects', c, lang), lang)
