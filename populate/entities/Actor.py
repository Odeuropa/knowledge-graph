from rdflib import RDFS, OWL

from .Entity import Entity
from .ontologies import CRM, ODEUROPA, REO
from .utils import wikidata_api
from .vocabularies import VocabularyManager as VocManager


class Actor(Entity):
    def __init__(self, name, lang=None, alive_in=None, anonymize=False, is_person=False):
        super().__init__(name, 'actor')
        is_animal = False

        if not anonymize:
            self.add(RDFS.label, name)

            lemma, role = VocManager.get('noses').ienterlink(name, lang)

            if lemma is not None:
                print(name, lemma)
                if 'Animal' in role:
                    is_animal = True
                else:
                    is_person = True
                    if 'Occupation' in role:
                        self.add(REO.readP1, lemma)

            self.add(CRM.P137_exemplifies, lemma)

            wd = None
            if lemma is None and len(name) < 40:
                wd = wikidata_api.searchperson(name, lang=lang, alive_in=alive_in)
            if wd is not None:
                self.add(OWL.sameAs, wd)
                is_person = True

        self.set_class(CRM.E21_Person if is_person else ODEUROPA.L6_Animal if is_animal else CRM.E39_Actor)
