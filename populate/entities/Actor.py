from rdflib import RDFS, OWL

from .Entity import Entity
from .ontologies import CRM
from .utils import wikidata_api


class Actor(Entity):
    def __init__(self, name, lang, alive_in):
        super().__init__(name)
        self.add(RDFS.label, name)

        wd = wikidata_api.searchperson(name, lang=lang, alive_in=alive_in)
        if wd:
            self.setclass(CRM.E21_Person)
            self.add(OWL.sameAs, wd)
        else:
            self.setclass(CRM.E39_Actor)

