from os import path

from rdflib import URIRef, RDF, RDFS

from .Entity import Entity
from .AttributeAssignment import AttributeAssignment
from .Graph import add, is_invalid
from .ontologies import ODEUROPA, CRM


class OlfactoryExperience(Entity):
    def __init__(self, seed, smell, quality='', place='', lang='en'):
        super().__init__(seed, 'experience')
        self.assignment_id = 0
        self.gesture_id = 0

        self.smell = smell
        self.perceiver = None

        self.set_class(ODEUROPA.L13_Olfactory_Experience)
        self.add(ODEUROPA.F2_perceived, smell)
        self.add(CRM.P7_took_place_at, place)

        if not is_invalid(quality):
            for x in quality.split('|'):
                self.add_quality(x.strip(), lang)

    def add_perceiver(self, perceiver):
        self.perceiver = perceiver
        self.add(CRM.P14_carried_out_by, perceiver)

    def add_quality(self, adjective, lang):
        self.assignment_id += 1
        attr_uri = path.join(self.uri, 'assignment', str(self.assignment_id))
        assignment = AttributeAssignment(attr_uri, adjective, lang, self.smell, self.perceiver)

        add(assignment, CRM.P17_was_motivated_by, self)

    def add_gesture(self, gesture, lang=''):
        if is_invalid(gesture):
            return
        self.gesture_id += 1
        gest_uri = path.join(self.uri, 'gesture', str(self.gesture_id))
        gest = URIRef(gest_uri)

        # if 'vomit' in gesture:
        #     typ = VocManager.get('olfactory-gestures').interlink_long(gesture, lang, fallback=None)
        #     print(gesture, typ)

        add(gest, RDF.type, ODEUROPA.L7_Gesture)
        add(gest, RDFS.label, gesture, lang)
        self.add(ODEUROPA.F5_involved_gesture, gest)

    def evoked(self, what, lang=''):
        self.add(ODEUROPA.F6_evoked, what, lang)
