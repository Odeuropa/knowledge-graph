from rdflib import PROV, RDFS

from . import Person
from .Entity import Entity


class Provenance(Entity):
    def __init__(self, seed, label, description, annotator=None):
        super().__init__(seed, 'provenance')
        self.set_class(PROV.Activity)
        self.add(RDFS.label, label)
        self.add(RDFS.comment, description)

        if annotator:
            annt = Person(annotator, anonymize=True)
            self.add(PROV.wasAssociatedWith, annt)
