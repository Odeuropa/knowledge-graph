from rdflib import PROV, RDFS

from .Entity import Entity
from .Person import Person


class Provenance(Entity):
    def __init__(self, annotator):
        super().__init__(annotator)
        self.setclass(PROV.Activity)
        self.add(RDFS.label, "Manual annotation")

        annt = Person(annotator, anonymize=True)
        self.add(PROV.wasAssociatedWith, annt)
