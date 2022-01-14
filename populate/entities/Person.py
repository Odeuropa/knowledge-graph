from rdflib import RDFS

from .Entity import Entity
from .ontologies import CRM


class Person(Entity):
    def __init__(self, name, anonymize=False):
        super().__init__(name)
        self.setclass(CRM.E21_Person)
        if not anonymize:
            self.add(RDFS.label, name)
