# This class is thought to serve as superclass for TextualObject and ImageObject

from rdflib import RDFS, SDO

from .Entity import Entity
from . import Actor, Time


class SourceDoc(Entity):
    def __init__(self, _id, title, author=None, date=None, lang=None):
        super().__init__(str(date) + title, 'source')
        self.author = None
        self.date = None

        self.title = title

        self.add(RDFS.label, title)

        if date:
            t = Time.parse(date)
            self.add(SDO.dateCreated, t)
            date = t.start if t else None
            self.date = date

        if author:
            self.author = Actor(author.strip(), lang=lang, alive_in=date)
            self.add(SDO.author, self.author)

    def add_author(self, author, lang=None, birth=None, death=None):
        name = author.strip()
        if birth or death:
            person = Actor(name, lang=lang, birth=birth, death=death)
        else:
            person = Actor(name, lang=lang, alive_in=self.date)
        self.add(SDO.author, person)
