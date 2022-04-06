import re
from os import path
from rdflib import URIRef, RDF, RDFS, SDO, SKOS
from .Entity import Entity
from .Actor import Actor
from .Time import Time
from .ontologies import CRM
from .config import BASE
from . import Graph

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


class TextualObject(Entity):
    def __init__(self, _id, title, author=None, year=None, place=None, lang=None, genre=None):
        super().__init__(str(year) + title)
        self.author = None
        self.title = title
        self.genre = genre

        self.setclass(CRM.E33_Linguistic_Object)
        self.add(RDFS.label, title)
        self.add(SDO.genre, to_genre(genre))
        self.add(SDO.inLanguage, lang)

        if year:
            if "(" in year:
                # the content in parentheses is normally the date in which has been written
                cont = re.search(r'\((.*?)\)', year)
                year = cont.group(1) if not cont.group(1).startswith('from') else year.replace(cont.group(0), '')

            t = Time.parse(year)
            self.add(SDO.dateCreated, t)
            year = t.start if t else None

        if author:
            self.author = Actor(author.strip(), lang=lang, alive_in=year)
            self.add(SDO.author, self.author)
