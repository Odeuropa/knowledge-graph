from rdflib import PROV, RDFS

from .Entity import Entity
from .Person import Person


class Provenance(Entity):
    def __init__(self, seed, label, description, annotator=None):
        super().__init__(seed)
        self.setclass(PROV.Activity)
        self.add(RDFS.label, label)
        self.add(RDFS.comment, description)

        if annotator:
            annt = Person(annotator, anonymize=True)
            self.add(PROV.wasAssociatedWith, annt)
