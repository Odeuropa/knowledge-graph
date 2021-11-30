import uuid
from os import path

from rdflib import URIRef, RDF

from . import Graph
from .config import BASE


class Entity:
    def __init__(self, seed):
        self.uri = path.join(BASE, 'text', str(uuid.uuid5(uuid.NAMESPACE_DNS, seed)))
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
