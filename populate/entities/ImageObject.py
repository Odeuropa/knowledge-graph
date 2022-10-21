import os.path
import re
from rdflib import URIRef, SDO, PROV, RDF, XSD, RDFS

from .Entity import Entity, Graph, MiniEntity
from .Place import Place
from .SourceDoc import SourceDoc
from .ontologies import CRM, MA, OA, NINSUNA
from .utils.getty import interlink_material

CM_REGEX = r'cm (\d+(?:\.\d+)?) × (\d+(?:\.\d+)?)'


class ImageObject(SourceDoc):
    def __init__(self, _id, title, author=None, date=None, place=None, url=None, lang=None):
        super().__init__(_id, title, author, date, lang)

        self.set_class(CRM.E36_Visual_Item)
        self.add(SDO.locationCreated, Place.from_text(place))
        self.add(SDO.image, url)
        # internal uri
        self.add(SDO.image, f'https://data.odeuropa.eu/image/{_id}')

        self.physical = PhysicalObject(self.uri)

    def add_fragment(self, bbox):
        frag = MediaFragment(self, bbox, self)
        self.add(MA.hasFragment, frag, self)
        return frag

    def add_type(self, typ):
        self.add(CRM.P2_has_type, typ)

    def add_material(self, m):
        x = re.match(CM_REGEX, m)

        if x is not None:
            w = x.group(1)
            h = x.group(2)
            self.physical.add_measure(m, (w, 'cm', 'width'), (h, 'cm', 'height'))
            return

        self.physical.add_material(m)

    def add_location(self, place, lang=None):
        if isinstance(place, str):
            place = Place.from_text(place, lang)
        self.physical.add(CRM.P53_has_former_or_current_location, place)

    def add_identifier(self, identifier):
        self.physical.add(CRM.P1_is_identified_by, identifier)


class PhysicalObject(Entity):
    # The physical part of the image (i.e. the proper painting hosted at the Museum)
    def __int__(self, parent_uri):
        self.uri = parent_uri.replace('/source/', '/source-object/')
        self.res = URIRef(self.uri)
        self.set_class(CRM.E24_HumanMade_Thing)

    def add_material(self, material):
        m = MiniEntity('material', material, material, CRM.E57_Material)
        m.same_as(interlink_material(material))
        self.add(CRM.P45_consists_of, m)

    def add_measure(self, label, *dimensions):
        dim_uri = self.uri + "/dimension/"

        measure = URIRef(dim_uri)
        Graph.add(measure, RDF.type, CRM.E16_Measurement)
        Graph.add(measure, CRM.P39_measured, self)
        Graph.add(measure, RDFS.label, label)

        for i, m in enumerate(dimensions):
            value, unit, typ = m
            r = URIRef(os.path.join(dim_uri, str(i)))
            Graph.add(r, RDF.type, CRM.E54_Dimension)
            Graph.add(r, CRM.P90_has_value, value, XSD.float)
            Graph.add(r, CRM.P91_has_unit, unit)
            Graph.add(measure, CRM.P40_observed_dimension, r)


class MediaFragment(Entity):
    def __init__(self, parent, bbox, media_obj):
        self.parent = parent
        media_uri = parent.uri
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
        if type(body).__name__ in ['Smell', 'SmellEmission', 'OlfactoryExperience']:
            Graph.set_prov(self.add(CRM.P67_refers_to, body), prov)
            Graph.set_prov(self.parent.add(CRM.P67_refers_to, body), prov)
        else:
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
