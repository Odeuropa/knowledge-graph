import uuid
from os import path
from rdflib import URIRef, SDO
from .ontologies import MA, OA
from .Entity import Entity
from .SourceDoc import SourceDoc
from .Place import Place
from .ontologies import CRM
from .config import BASE


class ImageObject(SourceDoc):
    def __init__(self, _id, title, author=None, date=None, place=None, currentPlace=None, genre=None, url=None):
        super().__init__(_id, title, author, date)
        self.genre = genre

        self.setclass(CRM.E36_Visual_Item)
        self.add(SDO.genre, genre)
        self.add(SDO.locationCreated, Place.from_text(place))
        self.add(SDO.image, url)
        currentPlace = currentPlace.split(', inv./cat.nr')[0]
        self.add(CRM.P53_has_former_or_current_location, Place.from_text(currentPlace))

    def add_fragment(self, bbox):
        frag = MediaFragment(self.uri, bbox, self)
        self.add(MA.hasFragment, frag, self)
        return frag


class MediaFragment(Entity):
    def __init__(self, media_uri, bbox, media_obj):
        self.uri = media_uri + '#xywh=' + ','.join([str(x) for x in bbox])
        self.res = URIRef(self.uri)
        self.setclass(MA.MediaFragment)
        self.media = media_obj

        x, y, w, h = bbox
        self.add(SDO.height, str(h))
        self.add(SDO.width, str(w))

    def add_annotation(self, body):
        annotation = Annotation(self.uri, body)
        annotation.add(OA.hasTarget, self)
        self.media.add(CRM.P138_represents, body)


class Annotation(Entity):
    def __init__(self, seed, body):
        super().__init__(seed)
        self.setclass(OA.Annotation)
        self.add(OA.hasBody, body)
