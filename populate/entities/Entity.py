import uuid
from os import path

from rdflib import URIRef, RDF, RDFS, TIME, OWL
from .ontologies import CRM

from . import Graph
from .config import BASE


class Entity:
    def __init__(self, seed, group=None):
        curclass = type(self).__name__

        if seed.startswith('http'):
            self.uri = seed
        else:
            if group is None:
                raise TypeError("If seed is not a URI, the param group is mandatory")
            self.seed = seed
            self.uri = path.join(BASE, group, str(uuid.uuid5(uuid.NAMESPACE_DNS, curclass + seed)))
        self.res = URIRef(self.uri)

    def set_class(self, cls):
        return self.add(RDF.type, cls)

    def add(self, pred, obj, lang=''):
        return Graph.add(self.res, pred, obj, lang)

    def split_add(self, pred, obj, lang=''):
        if Graph.is_invalid(obj):
            return
        for x in obj.split('|'):
            Graph.add(self.res, pred, x.strip(), lang)

    def add_label(self, label, lang=None):
        self.add(RDFS.label, label.strip(), lang)

    def add_descr(self, text, lang):
        self.add(RDFS.comment, text.strip(), lang)

    def add_place(self, place):
        self.add(CRM.P7_took_place_at, place)

    def add_time(self, time):
        self.add(TIME.hasTime, time)

    def same_as(self, entity):
        self.add(OWL.sameAs, entity)


class MiniEntity(Entity):
    def __init__(self, group, id, label, clas):
        self.uri = path.join(BASE, group, id.replace(' ', '_'))
        self.res = URIRef(self.uri)
        self.add_label(label)
        self.set_class(clas)
