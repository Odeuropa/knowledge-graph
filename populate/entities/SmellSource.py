from .Entity import Entity
from .ontologies import CRM, CRMsci
from .vocabularies import vocabulary_manager as VocManager


class SmellSource(Entity):
    def __init__(self, seed, label, lang='en'):
        super().__init__(seed)
        self.setclass(CRMsci.S10_Material_Substantial)
        self.add_label(label)

        match = VocManager.get('olfactory-objects').interlink(label, lang)
        self.add(CRM.P137_exemplifies, match)
