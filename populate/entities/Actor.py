import re
from rdflib import RDFS, OWL, SDO

from .Entity import Entity
from .Time import Time
from .ontologies import CRM, ODEUROPA, REO
from .utils import wikidata_api
from .utils.pronouns import Pronouns
from .vocabularies import VocabularyManager as VocManager

TITLES = {
    'en': ['Sir', 'Professor', 'The Hon.', 'Prof.', 'Commander', 'Dr.', 'Captain']
}


class Actor(Entity):
    def __init__(self, name, lang=None, alive_in=None, anonymize=False, is_person=False, birth=None, death=None):
        super().__init__(name, 'actor')
        is_animal = False
        role = None

        if not anonymize:
            self.add(RDFS.label, name)

            lemma = None
            if not Pronouns.is_pronoun(name, lang):
                lemma, role = VocManager.get('noses').interlink(name, lang)

            if lemma is not None:
                # print(name, lemma)
                if 'Animal' in role:
                    is_animal = True
                else:
                    is_person = True
                    if 'Occupation' in role:
                        self.add(REO.readP1, lemma)

            self.add(CRM.P137_exemplifies, lemma)

            b = birth.replace('?', '') if birth else None
            d = death.replace('?', '') if death else None
            self.add(SDO.birthDate, Time(birth, birth))
            self.add(SDO.deathDate, Time(death, death))

            # wd = None
            # if lemma is None and len(name) < 40:
            #     q = re.sub(r", [a-zA-Z]{1,3}\. .+", "", name)
            #     ttls = [x.replace('.', '\\.') for x in TITLES.get(lang, [])]
            #     q = re.sub(rf"^{'|'.join(ttls)} ", '', q).strip()
            #     q = re.sub(r"[.,:]$", '', q)  # trailing punctuation
            #     # print(q, ' <= ', name)
            #     wd = wikidata_api.searchperson(q.strip(), lang=lang, alive_in=alive_in, birth=b, death=d)
            # if wd is not None:
            #     self.add(OWL.sameAs, wd)
            #     is_person = True

        self.set_class(CRM.E21_Person if is_person else ODEUROPA.L6_Animal if is_animal else CRM.E39_Actor)
