import uuid
from os import path

from rdflib import URIRef, RDF, RDFS, TIME
from .ontologies import CRM

from . import Graph
from .config import BASE


class Entity:
    def __init__(self, seed, group):
        curclass = type(self).__name__

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
