from os import path

from rdflib import SKOS

from .AttributeAssignment import AttributeAssignment
from .Entity import Entity, MiniEntity
from .Gesture import Gesture
from .Graph import add, is_invalid
from .ontologies import ODEUROPA, CRM, REO
from .vocabularies import VocabularyManager as VocManager


class OlfactoryExperience(Entity):
    def __init__(self, seed, smell, place=''):
        super().__init__(seed, 'experience')
        self.assignment_id = 0
        self.gesture_id = 0

        self.smell = smell
        self.perceiver = None

        self.set_class(ODEUROPA.L13_Olfactory_Experience)
        self.add(ODEUROPA.F2_perceived, smell)
        self.add(CRM.P7_took_place_at, place)

    def add_perceiver(self, perceiver):
        self.perceiver = perceiver
        self.add(CRM.P14_carried_out_by, perceiver)

    def add_quality(self, adjective, lang):
        if is_invalid(adjective):
            return
        self.assignment_id += 1
        attr_uri = path.join(self.uri, 'assignment', str(self.assignment_id))
        assignment = AttributeAssignment(attr_uri, adjective, lang, self.smell, self.perceiver)

        add(assignment, CRM.P17_was_motivated_by, self)

    def add_gesture(self, gesture, lang=''):
        if isinstance(gesture, Gesture):
            self.add(ODEUROPA.F5_involved_gesture, gesture)

        # TODO
        if is_invalid(gesture):
            return
        # self.gesture_id += 1
        # gest_uri = path.join(self.uri, 'gesture', str(self.gesture_id))
        # gest = URIRef(gest_uri)

        # if 'vomit' in gesture:
        #     typ = VocManager.get('olfactory-gestures').interlink_long(gesture, lang, fallback=None)
        #     print(gesture, typ)

        # add(gest, RDF.type, ODEUROPA.L7_Gesture)
        # add(gest, RDFS.label, gesture, lang)
        # self.add(ODEUROPA.F5_involved_gesture, gest)

    def evoked(self, what, lang=''):
        self.add(ODEUROPA.F6_evoked, what, lang)

    def add_emotion(self, label, typ, sentiment):
        typ = [t for t in typ.split(' | ') if t != 'Smell_Word'][0]
        em = Emotion(self.seed, label, typ, sentiment)
        # print(label, typ, sentiment)
        em.add(REO.readP27, self)


class Emotion(Entity):
    def __init__(self, seed, label, typ, sentiment):
        super().__init__(seed, 'emotion')

        self.set_class(REO.REO21)
        self.add_label(label)
        self.add(CRM.P2_has_type, MiniEntity('sentiment', sentiment.lower(), sentiment, SKOS.Concept))

        if typ:
            match = VocManager.get('emotion').search(typ)
            if len(match.lemmata) and match.lemmata[0].score == 1:
                self.add(CRM.P137_exemplifies, match.lemmata[0].id)
            else:
                self.add(CRM.P137_exemplifies, MiniEntity('emotion-type', typ, typ, SKOS.Concept))
