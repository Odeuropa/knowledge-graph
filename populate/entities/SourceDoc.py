# This class is thought to serve as superclass for TextualObject and ImageObject

from rdflib import RDFS, SDO

from .Actor import Actor
from .Entity import Entity
from .Time import Time


class SourceDoc(Entity):
    def __init__(self, _id, title, author=None, date=None, lang=None):
        super().__init__(str(date) + title)
        self.author = None
        self.title = title

        self.add(RDFS.label, title)

        if date:
            t = Time.parse(date)
            self.add(SDO.dateCreated, t)
            date = t.start if t else None

        if author:
            self.author = Actor(author.strip(), lang=lang, alive_in=date)
            self.add(SDO.author, self.author)
