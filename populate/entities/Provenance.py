from rdflib import PROV, RDFS, SDO, URIRef

from . import Person
from .Entity import Entity


class Provenance(Entity):
    def __init__(self, seed, label, description, annotator=None):
        super().__init__(seed, 'provenance')
        self.set_class(PROV.Activity)
        self.add(RDFS.label, label)
        self.add(RDFS.comment, description)

        if annotator:
            if not isinstance(annotator, URIRef):
                annotator = Person(annotator, anonymize=True)
            self.add(PROV.wasAssociatedWith, annotator)

    def add_software(self, name, uri):
        sa = SoftwareAgent(name, uri)
        self.add(PROV.wasAssociatedWith, sa)


class SoftwareAgent(Entity):
    def __init__(self, name, uri):
        super().__init__(name, 'software')
        self.set_class(PROV.SoftwareAgent)
        self.add_label(name)
        self.add(SDO.url, uri)
