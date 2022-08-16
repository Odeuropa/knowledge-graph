import uuid
from os import path
from rdflib import URIRef, RDF, RDFS, SDO, SKOS

from .SourceDoc import SourceDoc
from .Entity import Entity
from . import Graph, Place
from .config import BASE
from .ontologies import CRM

GENRES = {
    "REL": "Religion",
    "MED": "Medicine",
    "BOT": "Botany",
    "PER": "Perfume books, fashion",
    "HOUS": "Household texts & recipes",
    "LIT": "Novels & poetry",
    "TRAV": "Travel literature / ethnography",
    "PUB": "Public Health",
    "SCIE": "Scientific and philosophical texts",
    "LAW": "Legal / criminal texts",
    "THE": "Theater",
    "OTH": "Other"
}


def to_genre(idg):
    if not idg:
        return None
    idg = "PUB" if idg == "PUBH" else idg
    idg = "SCIE" if idg == "SCI" else idg
    idg = "OTH" if idg == "OTHER" else idg
    genre = URIRef(path.join(BASE, 'genre', idg))
    Graph.add(genre, RDF.type, SKOS.Concept)
    Graph.add(genre, RDFS.label, GENRES[idg], 'en')
    return genre


class TextualObject(SourceDoc):
    def __init__(self, _id, title, author=None, date=None, place=None, lang=None, genre=None):
        super().__init__(_id, title, author, date, lang)

        self.genre = genre
        self.lang = lang

        self.set_class(CRM.E33_Linguistic_Object)
        self.add(SDO.genre, to_genre(genre))
        self.add(SDO.inLanguage, lang)
        self.add(SDO.locationCreated, Place.from_text(place))

    def add_url(self, url):
        self.add(SDO.url, url)

    def add_fragment(self, text, lang=None):
        frag = TextFragment(self, text, lang or self.lang)
        self.add(CRM.P165_incorporates, frag)
        return frag


class TextFragment(Entity):
    def __init__(self, parent, text, lang):
        self.uri = path.join(parent.uri, 'fragment', str(uuid.uuid5(uuid.NAMESPACE_DNS, text)))
        self.res = URIRef(self.uri)
        self.parent = parent

        self.set_class(CRM.E33_Linguistic_Object)
        self.add(RDF.value, text, lang)

    def add_annotation(self, what, prov):
        Graph.set_prov(self.add(CRM.P67_refers_to, what), prov)
        Graph.set_prov(self.parent.add(CRM.P67_refers_to, what), prov)
