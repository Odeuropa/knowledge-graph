import uuid
from os import path

from rdflib import URIRef, RDF, RDFS, SDO, SKOS

from . import Graph
from .Entity import Entity
from .SourceDoc import SourceDoc
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

KEYWORD_TO_GENRE = {
    "agriculture": "BOT",
    "alkohol": "PUB",
    "bukovništvo": "BOT",
    "cerkev": "REL",
    "chemistry": "SCIE",
    "christianity": "REL",
    "church": "REL",
    "domača zdravila": "HOUS",
    "enologija": "BOT",
    "fitopatologija": "MED",
    "fizika": "SCIE",
    "gospodinjstvo": "HOUS",
    "Humoristični list": "LIT",
    "povesti": "LIT",
    "romani": "LIT",
    "kemija": "SCIE",
    "kletarstvo": "BOT",
    "kmetijstvo": "BOT",
    "književnost": "LIT",
    "krščans": "REL",
    "kuhar": "HOUS",
    "law": "LAW",
    "leposlovje": "LIT",
    "literarna": "LIT",
    "literary": "LIT",
    "literature": "LIT",
    "medicina": "MED",
    "običaji": "TRAV",
    "teologija": "REL",
    "pedagogika": "SCIE",
    "pedagogy": "SCIE",
    "physics": "SCIE",
    "poezija": "LIT",
    "pravo": "LAW",
    "prirodoslovne vede": "SCIE",
    "prose": "LIT",
    "proza": "LIT",
    "sadj": "BOT",
    "dramatika": "LIT",
    "sociologija": "SCIE",
    "sociology": "SCIE",
    "technology": "SCIE",
    "tehnologija": "SCIE",
    "terminologija": "SCIE",
    "terminology": "SCIE",
    "terminološki": "SCIE",
    "therapy": "MED",
    "uporabne vede": "SCIE",
    "verski": "REL",
    "veterinarstvo": "MED",
    "vinarstvo": "BOT",
    "vino": "BOT",
    "vinogradništvo": "BOT",
    "vinsk": "BOT",
    "vrtnarstvo": "BOT",
    "zdravilne": "MED",
    "zdravljenje": "MED",
    "zdravstvo": "MED",
    "zoologija": "SCIE",
    "zoology": "SCIE",
    "čebelarstvo": "BOT"
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
        self.add_place(place, lang)

    def add_fragment(self, text, lang=None, url=None):
        frag = TextFragment(self, text, lang or self.lang)
        frag.add(SDO.url, url)
        self.add(CRM.P165_incorporates, frag)
        return frag

    def add_genre_from_keyword(self, keyword):
        for k in KEYWORD_TO_GENRE:
            if k in keyword:
                return self.add(SDO.genre, to_genre(KEYWORD_TO_GENRE[k]))


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
