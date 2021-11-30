from rdflib import RDFS

from .Entity import Entity
from .ontologies import CRM


class TextualObject(Entity):
    def __init__(self, title):
        super().__init__(title)
        self.setclass(CRM.E33_Linguistic_Object)
        self.add(RDFS.label, title)
