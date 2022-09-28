from rdflib import URIRef, SDO, PROV, RDF, XSD

from .Entity import Entity, Graph
from .Place import Place
from .SourceDoc import SourceDoc
from .ontologies import CRM, MA, OA, NINSUNA


class ImageObject(SourceDoc):
    def __init__(self, _id, title, author=None, date=None, place=None, currentPlace=None, genre=None, url=None):
        super().__init__(_id, title, author, date)
        self.genre = genre

        self.set_class(CRM.E36_Visual_Item)
        self.add(SDO.genre, genre)
        self.add(SDO.locationCreated, Place.from_text(place))
        self.add(SDO.image, url)
        # internal uri
        self.add(SDO.image, f'https://data.odeuropa.eu/image/{_id}')

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
        self.set_class(MA.MediaFragment)
        self.media = media_obj

        x, y, w, h = bbox
        self.add(NINSUNA.spatialH, str(h))
        self.add(NINSUNA.spatialW, str(w))
        self.add(NINSUNA.spatialX, str(x))
        self.add(NINSUNA.spatialY, str(y))

    def add_annotation(self, body, prov, confidence=1):
        annotation = Annotation(self.uri, body)
        annotation.add(OA.hasTarget, self)
        annotation.add(PROV.wasGeneratedBy, prov)
        annotation.add(RDF.value, confidence, XSD.decimal)
        Graph.set_prov(self.media.add(CRM.P138_represents, body), prov)


class Annotation(Entity):
    def __init__(self, seed, body):
        super().__init__(seed, 'annotation')
        self.set_class(OA.Annotation)
        self.add(OA.hasBody, body)
