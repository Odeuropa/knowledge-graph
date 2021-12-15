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
    "THE": "Theater"
}

def to_genre(id):
    genre = URIRef(path.join(BASE, 'genre', id))
    Graph.add(genre, RDF.type, SKOS.Concept)
    Graph.add(genre, RDFS.label, GENRES[id], 'en')
    return genre

class TextualObject(Entity):
    def __init__(self, _id, title, author, year, place, lang, genre):
        super().__init__(_id)
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
            self.add(SDO.author, Actor(author.strip(), lang=lang, alive_in=year))
