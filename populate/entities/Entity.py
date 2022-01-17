import uuid
from os import path

from rdflib import URIRef, RDF, RDFS, TIME
from .ontologies import CRM

from . import Graph
from .config import BASE


class Entity:
    def __init__(self, seed):

        self.uri = path.join(BASE, type(self).__name__, str(uuid.uuid5(uuid.NAMESPACE_DNS, seed)))
        self.res = URIRef(self.uri)

    def setclass(self, cls):
        self.add(RDF.type, cls)

    def add(self, pred, obj, lang=''):
        Graph.add(self.res, pred, obj, lang)

    def split_add(self, pred, obj, lang=''):
        if Graph.is_invalid(obj):
            return
        for x in obj.split('|'):
            Graph.add(self.res, pred, x.strip(), lang)

    def add_label(self, label):
        self.add(RDFS.label, label)

    def add_place(self, place):
        self.add(CRM.P7_took_place_at, place)

    def add_time(self, place):
        self.add(TIME.hasTime, place)
