from .Entity import Entity
from .ontologies import CRM, CRMsci
from .vocabularies import VocabularyManager as VocManager

SMELL_SOURCE = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/smell-source'
CARRIER = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/carrier'
ARTIFACT = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/artifact'


class SmellSource(Entity):
    def __init__(self, seed, label, lang='en', lemma=None, role=None):
        super().__init__(seed, 'object')
        self.add_label(label, lang)

        self.role = None
        if lemma is None:
            lemma, role = VocManager.get('olfactory-objects').interlink(label, lang)

        if lemma is None:
            self.set_class(CRMsci.S10_Material_Substantial)
        else:
            self.add(CRM.P137_exemplifies, lemma)
            if role and ARTIFACT in role:
                self.set_class(CRM.E22_HumanMade_Object)
            else:
                self.set_class(CRMsci.S10_Material_Substantial)

            if role:
                if CARRIER in role:
                    self.role = 'carrier'
                elif SMELL_SOURCE in role:
                    self.role = 'smell-source'
