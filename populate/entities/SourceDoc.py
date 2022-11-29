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
    def __init__(self, _id, title, author=None, date=None, lang=None):
        super().__init__(str(date) + (title or _id) + str(author), 'source')
        self.author = None

        self.title = title

        self.add_label(title, lang)

        if date:
            t = Time.parse(date)
            self.add(SDO.dateCreated, t)
            date = t.start if t else None
            self.time = t

        if author:
            birth = death = None
            dt = re.search(AUTHOR_DATES, author)

            if dt:
                author = author.replace(dt.group(0), '')

                birth = dt.group(1)
                death = dt.group(2)
            self.author = Actor(author.strip(), lang=lang, alive_in=date, birth=birth, death=death, is_person=True)
            self.add(SDO.author, self.author)

    def add_author(self, author, lang=None, birth=None, death=None):
        name = author.strip()
        if birth or death:
            person = Actor(name, lang=lang, birth=birth, death=death)
        else:
            person = Actor(name, lang=lang, alive_in=self.time)
        self.add(SDO.author, person)

    def add_place(self, place):
        if not isinstance(place, Place):
            place = Place.from_text(place)
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
