from .Entity import Entity
from .ontologies import ODEUROPA, CRM
from .vocabularies import VocabularyManager as VocManager


class Gesture(Entity):
    def __init__(self, seed, label=None, lang='en', lemma=None):
        super().__init__(seed, 'gesture')
        if label is None:
            label = seed
        self.set_class(ODEUROPA.L7_Gesture)
        self.add_label(label, lang)

        self.role = None
        if lemma is None:
            lemma, role = VocManager.get('olfactory-gestures').interlink(label, lang)

        self.interlinked = lemma is not None
        if lemma is not None:
            self.set_uri(lemma)
            # self.add(CRM.P137_exemplifies, lemma)
