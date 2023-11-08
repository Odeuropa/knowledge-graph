from os import path
import re
from rdflib import SKOS

from .AttributeAssignment import AttributeAssignment
from .Entity import Entity, MiniEntity
from .Thing import Thing
from .Gesture import Gesture
from .Place import Place
from .SmellSource import SmellSource
from .Graph import add, is_invalid
from .utils.pos import Prepositions
from .ontologies import ODEUROPA, CRM, REO
from .vocabularies import VocabularyManager as VocManager


class OlfactoryExperience(Entity):
    def __init__(self, seed, smell, place=''):
        super().__init__(seed, 'experience')
        self.assignment_id = 0
        self.gesture_id = 0
        self.emotion_id = 0

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
        if is_invalid(gesture):
            return

        if isinstance(gesture, Gesture):
            self.add(ODEUROPA.F5_involved_gesture, gesture)
            return

        self.gesture_id += 1

        lemma, role = VocManager.get('olfactory-gestures').interlink(gesture, lang)
        if lemma is not None:
            print('found!', gesture, lemma)
            gest = Gesture(self.seed + '$' + str(self.gesture_id), gesture, lang, lemma)
            self.add(ODEUROPA.F5_involved_gesture, gest)

        # nothing more for now
        # TODO better strategy: here there are mostly long texts

    def evoked(self, what, lang=''):
        if is_invalid(what):
            return

        what = re.sub(Prepositions(lang).as_regex(as_start=True), '', what.lower())

        uri, role, voc = VocManager.interlink_multiple(what, lang, ['olfactory-objects', 'fragrant-spaces'])
        if uri is None:
            # TODO check if it can be a proper place!
            # no choice, generic
            obj = Thing(self.seed + '$' + what, what, lang)
        elif voc == 'fragrant-spaces':
            obj = Place(what, typ=uri)
        else:
            obj = SmellSource(self.seed + '$' + what, what, lang=lang, lemma=uri, role=role)

        self.add(ODEUROPA.F6_evoked, obj)

    def add_emotion(self, label, typ, sentiment=None):
        typ = [t for t in typ.split(' | ') if t != 'smell_word'][0]
        self.emotion_id += 1

        em = Emotion(self.seed + '$' + str(self.emotion_id), label.strip(), typ.strip(), sentiment)
        return em.add(REO.readP27, self)


class Emotion(MiniEntity):
    def __init__(self, seed, label, typ, sentiment):
        super().__init__('emotion-type', typ, typ, SKOS.Concept)

        self.set_class(REO.REO21)
        if sentiment and sentiment.strip():
            self.add(CRM.P2_has_type, MiniEntity('sentiment', sentiment.strip().lower(), sentiment, SKOS.Concept))

        if typ and typ.strip():
            typ = typ.strip()
            match = VocManager.get('emotion').search(typ)
            if len(match.lemmata) and match.lemmata[0].score == 1:
                self.set_uri(match.lemmata[0].id)
                # self.add(CRM.P137_exemplifies, match.lemmata[0].id)
            else:
                self.add_label(label)
            #     self.add(CRM.P137_exemplifies, MiniEntity('emotion-type', typ, typ, SKOS.Concept))
