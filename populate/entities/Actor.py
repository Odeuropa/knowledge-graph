from rdflib import RDFS, OWL

from .Entity import Entity
from .ontologies import CRM
from .utils import wikidata_api


class Actor(Entity):
    def __init__(self, name, lang=None, alive_in=None, anonymize=False, is_person=False):
        super().__init__(name, 'actor')
        if not anonymize:
            self.add(RDFS.label, name)

            wd = None
            if len(name) < 40:
                wd = wikidata_api.searchperson(name, lang=lang, alive_in=alive_in)
            if wd is not None:
                self.add(OWL.sameAs, wd)
                is_person = True

        self.set_class(CRM.E21_Person if is_person else CRM.E39_Actor)
