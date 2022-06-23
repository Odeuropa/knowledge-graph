from os import path

from rdflib import URIRef, RDF, RDFS, SDO, SKOS

from . import Graph
from .SourceDoc import SourceDoc
from .Place import Place
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


def to_genre(id):
    if not id:
        return None
    id = "PUB" if id == "PUBH" else id
    id = "SCIE" if id == "SCI" else id
    id = "OTH" if id == "OTHER" else id
    genre = URIRef(path.join(BASE, 'genre', id))
    Graph.add(genre, RDF.type, SKOS.Concept)
    Graph.add(genre, RDFS.label, GENRES[id], 'en')
    return genre


class TextualObject(SourceDoc):
    def __init__(self, _id, title, author=None, date=None, place=None, lang=None, genre=None):
        super().__init__(_id, title, author, date, lang)
        self.genre = genre

        self.setclass(CRM.E33_Linguistic_Object)
        self.add(SDO.genre, to_genre(genre))
        self.add(SDO.inLanguage, lang)
        self.add(SDO.locationCreated, Place.from_text(place))

    def add_url(self, url):
        self.add(SDO.url, url)
