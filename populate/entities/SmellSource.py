from .Entity import Entity
from .ontologies import CRM, CRMsci
from .vocabularies import VocabularyManager as VocManager

SMELL_SOURCE = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/smell-source'
CARRIER = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/carrier'
ARTIFACT = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/artifact'


class SmellSource(Entity):
    def __init__(self, seed, label=None, lang='en', lemma=None, role=None):
        super().__init__(seed, 'object')
        if label is None:
            label = seed

        self.role = None
        if lemma is None:
            lemma, role = VocManager.get('olfactory-objects').interlink(label, lang)
            if lemma is None:
                lemma, role = VocManager.get('fragrant-spaces').interlink(label, lang)
                if lemma is not None:
                    role = 'place'

        self.interlinked = lemma is not None
        if lemma is None:
            self.set_class(CRMsci.S10_Material_Substantial)
            self.add_label(label, lang)
        else:
            self.set_uri(lemma)
            # self.add(CRM.P137_exemplifies, lemma)
            # if role == 'place':
            #     self.set_class(CRM.E53_Place)
            # if role == 'person':
            #         self.set_class(CRM.E21_Person)
            # if role and ARTIFACT in role:
            #     self.set_class(CRM.E22_HumanMade_Object)
            # else:
            #     self.set_class(CRMsci.S10_Material_Substantial)

            if role:
                if CARRIER in role:
                    self.role = 'carrier'
                elif SMELL_SOURCE in role:
                    self.role = 'smell-source'
