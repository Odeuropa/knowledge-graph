import re
from string import punctuation
from rdflib import RDFS, OWL, SDO

from .Entity import Entity
from .Time import Time
from .ontologies import CRM, ODEUROPA, REO
from .utils import wikidata_api
from .utils.pos import Pronouns
from .vocabularies import VocabularyManager as VocManager

TITLES = {
    'en': ['Sir', 'Professor', 'The Hon.', 'Prof.', 'Commander', 'Dr.', 'Captain']
}

ANONYMOUS_REGEX = r'(?i)(\[?s\.n\.?\]?|anonym(e|ous)|anonim[oa]|anoniem|autore non indicato)'
STOPWORDS_REGEX = r'(?i)(possibly|attributed to|chez|after|\[?puis\]?|\(?attribué\)?|\(.*\)|, attr\.?$)'


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
            if birth:
                self.add(SDO.birthDate, Time(birth, birth))
            if death:
                self.add(SDO.deathDate, Time(death, death))

            wd = None
            if lemma is None and role != 'Pronoun' and len(name) < 40:
                q = re.sub(r", [a-zA-Z]{1,3}\. .+", "", name)
                ttls = [x.replace('.', '\\.') for x in TITLES.get(lang, [])]
                q = re.sub(rf"^{'|'.join(ttls)} ", '', q).strip()
                q = re.sub(r"[.,:]$", '', q)  # trailing punctuation
                # print(q, ' <= ', name)
                wd = wikidata_api.searchperson(q.strip(), lang=lang, alive_in=alive_in, birth=b, death=d)
            if wd is not None:
                self.add(OWL.sameAs, wd)
                is_person = True

        self.set_class(CRM.E21_Person if is_person else ODEUROPA.L6_Animal if is_animal else CRM.E39_Actor)

    def add_place(self, place, lang=None):
        self.add(CRM.P53_has_former_or_current_location, place)

    @classmethod
    def create(cls, name, lang=None, alive_in=None, anonymize=False, is_person=False, birth=None, death=None):
        if name is None or len(name) < 1:
            return None
        if re.search(ANONYMOUS_REGEX, name):
            return None

        name = re.sub(STOPWORDS_REGEX, '', name).strip(punctuation).strip()
        if len(name) < 1:
            return None

        # TODO extract nationality in cases such as:
        # Anoniem (Duitsland) in of na 1560: null
        # Anoniem (Frankrijk): null
        # Anoniem (Haarlem) 1553 gedateerd: null
        # "Anoniem (Itali\xEB) eerste kwart 17de eeuw": null
        # Anoniem (Nederland) ca. 1700-1850: null
        # niederl\xE4ndisch
        # \xE4gyptisch

        return Actor(name, lang, alive_in, anonymize, is_person, birth, death)
