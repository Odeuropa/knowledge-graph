import os
import re
import string
from urllib import request
from rdflib import RDFS, URIRef
import geocoder
import yaml
from .Entity import Entity
from .vocabularies.VocabularyManager import ARTICLE_REGEX
from .Graph import is_invalid
from .ontologies import CRM
from .vocabularies import VocabularyManager as VocManager
from .utils.pronouns import Pronouns
from .config import GEONAMES, GEONAMES_CACHE

with open(GEONAMES_CACHE, 'r') as _f:
    cache = yaml.load(_f, Loader=yaml.CLoader)
    if cache is None:
        cache = {}

IN_PREFIX = {
    'en': r'(?i)^(at|in(to)?|upon|near|even( in)?|of|on|along|from|to) ',
    'it': r"(?i)^(d'|a |in |(da|ne|su|a)(gl)?i |presso |per |(da|ne|su|a)(l(l[aoe])?)? |(da|ne|su)ll ?')",
    'fr': r"(?i)^((en|dans|à|aux?|sur) |d')",
    'nl': r'(?i)^(by|te|op|in) ',
    'de': r'(?i)^(by|te|op|in|im|von) ',
    'sl': r'(?i)^(v|pod?|o[bd]|na|iz) '
}


def extract_feature(text):
    map_features = [
        ('the (city|village) of ', 'P')
    ]
    for rg, ft in map_features:
        if re.search(rg, text):
            return ft, re.sub(rg, '', text).strip()
    return None, text


def add_to_cache(text, geonames_id):
    if geonames_id is not None:
        request.urlretrieve(f'https://sws.geonames.org/{geonames_id}/about.rdf', f'../dump/geonames/{geonames_id}.rdf')
    cache[text] = geonames_id

    with open(GEONAMES_CACHE, 'w') as f:
        f.write(yaml.dump(cache, Dumper=yaml.CDumper))


def to_geonames_uri(geonames_id):
    return f'https://sws.geonames.org/{geonames_id}/'


class Place(Entity):
    IN_PREFIX = IN_PREFIX

    def __init__(self, name, typ=None):
        super().__init__(name, 'place')
        self.set_class(CRM.E53_Place)
        self.add(RDFS.label, name)
        self.add(CRM.P137_exemplifies, typ)

    @classmethod
    def from_text(cls, text, lang='en'):
        if is_invalid(text) or re.match(r'\d+(\\.\d+)?', text):
            return None

        if text.startswith('art dealer'):
            return  # TODO
        text = re.sub(IN_PREFIX.get(lang, IN_PREFIX['en']), '', text.strip(), flags=re.I).strip()
        text = re.sub(r'(Private Collection|Collezione privata|Mercato antiquario)([:,]? \(?)?', '', text, flags=re.I)
        text = text.strip(string.punctuation).strip()
        feature_class, text = extract_feature(text)

        text_clean = text
        pron_regex = Pronouns(lang).as_regex()
        disambiguate = True
        if re.match(pron_regex, text):
            text_clean = re.sub(pron_regex, '', text)
            disambiguate = False
        article_prefix = ARTICLE_REGEX.get('lang', ARTICLE_REGEX['en']) + r'(?=[a-zA-Z])'
        if re.match(article_prefix, text):
            text_clean = re.sub(article_prefix, '', text)
            disambiguate = text_clean[0].isupper()

        # TODO
        if not text_clean or re.match(r'\d+(\\.\d+)?', text_clean):
            return None

        typ, role = VocManager.get('fragrant-spaces').interlink(text_clean, lang, fallback=None)
        if typ or not disambiguate:
            return Place(text, typ)

        if text in cache:
            if cache[text] is None:  # already searched, no match
                return Place(text)
            else:  # we have it in the cache!
                geonames_id = cache[text]
                file = f'../dump/geonames/{geonames_id}.rdf'
                if not os.path.isfile(file):
                    request.urlretrieve(f'https://sws.geonames.org/{geonames_id}/about.rdf', file)
                return URIRef(to_geonames_uri(geonames_id))

        else:  # search
            res = geocoder.geonames(text, key=GEONAMES, featureClass=feature_class, orderby='relevance',
                                    isNameRequired=True, searchlang=lang, lang=lang)
            if res:  # found
                add_to_cache(text, res.geonames_id)
                return URIRef(to_geonames_uri(res.geonames_id))
            else:  # generic place
                add_to_cache(text, None)
                # create new object
                return Place(text)
