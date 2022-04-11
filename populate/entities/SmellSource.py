from .Entity import Entity
from .ontologies import CRM, CRMsci
from .vocabularies import vocabulary_manager as VocManager

BASE_OO = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/'


class SmellSource(Entity):
    def __init__(self, seed, label, lang='en', lemma=None, role=None):
        super().__init__(seed)
        self.add_label(label)

        self.role = None
        if lemma is None:
            lemma, role = VocManager.get('olfactory-objects').interlink(label, lang)

        if lemma is not None:
            self.add(CRM.P137_exemplifies, lemma)
            if role and BASE_OO + 'artifact' in role:
                self.setclass(CRM.E22_HumanMade_Object)
            else:
                self.setclass(CRMsci.S10_Material_Substantial)

            if role:
                if BASE_OO + 'carrier' in role:
                    self.role = 'carrier'
                elif BASE_OO + 'smell-source' in role:
                    self.role = 'smell-source'
