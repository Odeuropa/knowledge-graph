import re
import uuid
from os import path

from rdflib import URIRef, RDF, RDFS, TIME, OWL
from .ontologies import CRM

from . import Graph
from .config import BASE


class Entity:
    def __init__(self, seed, group=None):
        curclass = type(self).__name__
        self.seed = seed
        if seed.startswith('http'):
            self.uri = seed
        else:
            if group is None:
                raise TypeError("If seed is not a URI, the param 'group' is mandatory")
            self.uri = path.join(BASE, group, str(uuid.uuid5(uuid.NAMESPACE_DNS, curclass + seed)))
        self.res = URIRef(self.uri)

        self.time = None
        self.label = None


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
        self.label = label

    def add_descr(self, text, lang):
        self.add(RDFS.comment, text.strip(), lang)

    def add_place(self, place, lang=None):
        self.add(CRM.P7_took_place_at, place, lang=lang)

    def add_time(self, time, inferred=False):
        self.time = time
        statement = self.add(TIME.hasTime, time)
        if inferred:
            Graph.add_rdfstar(statement, CRM.P2_has_type, 'inferred')

    def same_as(self, entity):
        self.add(OWL.sameAs, entity)


class MiniEntity(Entity):
    def __init__(self, group, id, label, clas):
        safe_id = re.sub(r'[à`|"]','',id.replace(' ', '_'))
        self.uri = path.join(BASE, group, safe_id)
        self.res = URIRef(self.uri)
        self.add_label(label)
        self.set_class(clas)
