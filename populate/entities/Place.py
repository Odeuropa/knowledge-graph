import os
import re
import string
from urllib import request

import geocoder
import yaml
from rdflib import RDFS

from .Entity import Entity
from .Graph import is_invalid
from .config import GEONAMES, GEONAMES_CACHE
from .ontologies import CRM
from .utils.pos import Pronouns
from .vocabularies import VocabularyManager as VocManager
from .vocabularies.VocabularyManager import ARTICLE_REGEX

with open(GEONAMES_CACHE, 'r') as _f:
    cache = yaml.load(_f, Loader=yaml.CLoader)
    if cache is None:
        cache = {}

IN_PREFIX = {
    'en': r'(?i)^(all |here |(any|every)where |certain (parts )?)?(at|i[un](to)?|hot|upon|between|below|down ([oi]n)?|every|all|the whole|many|about|beyond|above|across|his|her|our|out(side)?( in| of)?|near|throughout|even( in)?|of|on|along|from|to|before|over) ',
    'it': r"(?i)^(d ?'|a |i[un] |(da|ne|su|a)(gl)?i |presso |per |(da|ne|su|a)(l(l[aoe])?)? |(da|ne|su)ll ?')",
    'fr': r"(?i)^(coin )?((de|en|dans|à|aux?|sur|autur du?) |d')",
    'nl': r'(?i)^(by|te|op|in) ',
    'de': r'(?i)^(by|te|op|in|im|von|au[sß]|auff?) ',
    'sl': r'(?i)^(v|pod?|o[bd]|na|iz) '
}

VERBAL_PREFIX = r"((first time )?(auction|report|record|purchas|deposit|mention|exhibit|acquir|signale|sight)ed|shown|sold|" \
                r"gesignaleer?d|getoond|(verworv|geschonk|overled)en|tentoongesteld|geveild)"


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
        print(text, geonames_id)
        request.urlretrieve(f'https://sws.geonames.org/{geonames_id}/about.rdf', f'../dump/geonames/{geonames_id}.rdf')
    cache[text] = geonames_id

    with open(GEONAMES_CACHE, 'w') as f:
        f.write(yaml.dump(cache, Dumper=yaml.CDumper))


def to_geonames_uri(geonames_id):
    return f'https://sws.geonames.org/{geonames_id}/'


class Place(Entity):
    IN_PREFIX = IN_PREFIX

    def __init__(self, name, typ=None, lang=None):
        super().__init__(name, 'place')
        self.set_class(CRM.E53_Place)
        if not name.startswith('http'):
            self.add(RDFS.label, name, lang)
        self.add(CRM.P137_exemplifies, typ)
        self.interlinked = name.startswith('http')

    @classmethod
    def from_text(cls, text, lang='en', only_interlinked=False):
        if is_invalid(text) or re.match(r'\d+(\\.\d+)?', text):
            return None
        text = text.strip('?').strip()
        if text in ['Whereabouts unknown', 'Ubicazione sconosciuta']:
            return None
        original_text = text

        text = re.sub(VERBAL_PREFIX, '', text.strip(), flags=re.I).strip()
        text = re.sub(IN_PREFIX.get(lang, IN_PREFIX['en']), '', text.strip(), flags=re.I).strip()
        text = text.strip(string.punctuation).strip()

        PRIVATE_COLLECTION_REGEX = \
            r'(?i)(Private Collection|Collezione privata|Mercato antiquario|art dealer)[^:,(-]*([:,-]? \(?)?'
        pc = re.match(PRIVATE_COLLECTION_REGEX, text)
        if pc:
            # we can't find a private collection in geonames
            text = re.sub(PRIVATE_COLLECTION_REGEX, '', text, flags=re.I)
            text = text.strip(string.punctuation).strip()
            p = Place(original_text)
            if len(text) > 0:
                # I try to search where this private collection is
                parent = Place.from_text(text, lang, only_interlinked=True)
                p.falls_within(parent)

            return p

        if is_invalid(text) or re.match(r'\d+(\\.\d+)?', text):
            return None

        feature_class, text = extract_feature(text)

        text_clean = text
        pron_regex = Pronouns(lang or 'en').as_regex()
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
            return None if only_interlinked else Place(original_text, typ)

        if text in cache:
            if cache[text] is None:  # already searched, no match
                return None if only_interlinked else Place(original_text)
            else:  # we have it in the cache!
                geonames_id = cache[text]
                file = f'../dump/geonames/{geonames_id}.rdf'
                if not os.path.isfile(file):
                    try:
                        request.urlretrieve(f'https://sws.geonames.org/{geonames_id}/about.rdf', file)
                    except:
                        pass
                return Place(to_geonames_uri(geonames_id))

        else:  # search
            res = False
            if text != 'station': #workaround
                res = geocoder.geonames(text, key=GEONAMES, featureClass=feature_class, orderby='relevance',
                                    isNameRequired=True, searchlang=lang, lang=lang)
            if res:  # found
                add_to_cache(text, res.geonames_id)
                return Place(to_geonames_uri(res.geonames_id))
            else:  # generic place
                add_to_cache(text, None)
                # create new object
                return None if only_interlinked else Place(original_text)

    def falls_within(self, place):
        self.add(CRM.P89_falls_within, place)
