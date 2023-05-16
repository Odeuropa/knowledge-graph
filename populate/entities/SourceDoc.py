# This class is thought to serve as superclass for TextualObject and ImageObject
import re

from rdflib import SDO

from . import Actor, Time, Place
from .Entity import Entity
from .SmellSource import SmellSource
from .Thing import Thing
from .vocabularies import VocabularyManager as VocManager

subj_map = {}
AUTHOR_DATES = r'\((\d+)-(\d+)\)'


class SourceDoc(Entity):
    def __init__(self, _id, title, author=None, date=None, lang=None, creator_property=SDO.author):
        super().__init__(str(date) + (title or _id) + str(author), 'source')
        self.creators = []
        self.author = None

        self.title = title

        self.add_label(title, lang)

        self.add_creation_date(date, lang)

        if author:
            birth = death = None
            dt = re.search(AUTHOR_DATES, author)

            if dt:
                author = author.replace(dt.group(0), '')

                birth = dt.group(1)
                death = dt.group(2)

            self.author = self.add_creator(author, lang=lang, birth=birth, death=death, property=creator_property)

    def add_creation_date(self, date, lang='en'):
        if not date:
            return
        t = date if isinstance(date, Time) else Time.parse(date, lang)
        self.add(SDO.dateCreated, t)
        self.time = t

    def add_pub_date(self, date, lang='en'):
        if not date:
            return
        t = date if isinstance(date, Time) else Time.parse(date, lang)
        self.add(SDO.datePublished, t)

    def add_creator(self, author, lang=None, birth=None, death=None, property=SDO.author):
        name = author.strip()
        if birth or death:
            person = Actor.create(name, lang=lang, birth=birth, death=death, is_person=True)
        else:
            t = self.time.start if self.time else None
            person = Actor.create(name, lang=lang, alive_in=t, is_person=True)
        self.creators.append(person)
        self.add(property, person)
        return person

    def add_actor(self, role, actor, lang=None, place=None):
        if actor is None:
            return

        pub = actor if isinstance(actor, Actor) else Actor.create(actor, lang=lang)
        if pub:
            pub.add_place(place, lang=lang)
            self.add(role, pub)

    def add_editor(self, editor, lang=None, place=None):
        self.add_actor(SDO.editor, editor, lang, place)

    def add_publisher(self, publisher, lang=None, place=None):
        self.add_actor(SDO.publisher, publisher, lang, place)

    def add_place(self, place, lang=None):
        if not isinstance(place, Place):
            place = Place.from_text(place, lang)
        self.add(SDO.locationCreated, place)

    def add_subject(self, subject, lang=None):
        if subject is None:
            return

        # is it an olfactory object ?
        label = re.sub(r'\(.+\)', '', subject).lower()
        if label in subj_map:
            return subj_map[label]

        lemma, role = VocManager.get('olfactory-objects').interlink(label, lang)
        if lemma:
            obj = SmellSource(subject, lang=lang, lemma=lemma, role=role)
            subj_map[label] = obj
        else:
            lemma, role = VocManager.get('fragrant-spaces').interlink(label, lang)
            if lemma:
                obj = Place(subject, typ=lemma, lang=lang)
            else:
                # we go generic
                obj = Thing(subject, subject, lang)
            subj_map[label] = obj

        self.add(SDO.about, obj)

    def add_url(self, url):
        self.add(SDO.url, url)

    def add_license(self, text):
        if not text:
            return
        CC_REGEX = r'CC (.+) (\d\.\d)'
        m = re.match(CC_REGEX, text)
        if m:
            self.add(SDO.license, f'https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2)}/')
        elif text == 'Public Domain':
            self.add(SDO.license, 'https://creativecommons.org/publicdomain/mark/1.0/')
        else:
            self.add(SDO.license, text)
