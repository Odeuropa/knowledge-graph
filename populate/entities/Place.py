import re
from urllib import request
from rdflib import RDFS, URIRef
import geocoder
import yaml
from .Entity import Entity
from .vocabularies.vocabulary_manager import ARTICLE_REGEX
from .Graph import is_invalid
from .ontologies import CRM
from .vocabularies import vocabulary_manager as VocManager
from .utils.pronouns import Pronouns
from .config import GEONAMES, GEONAMES_CACHE

with open(GEONAMES_CACHE, 'r') as _f:
    cache = yaml.load(_f, Loader=yaml.CLoader)
    if cache is None:
        cache = {}


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
    def __init__(self, name, typ=None):
        super().__init__(name)
        self.setclass(CRM.E53_Place)
        self.add(RDFS.label, name)
        self.add(CRM.P137_exemplifies, typ)

    @classmethod
    def from_text(cls, text, lang='en'):
        if is_invalid(text):
            return None

        IN_PREFIX = r'^(at|in|upon|even( in)?|of|on|along|from|to) '
        text = re.sub(IN_PREFIX, '', text.strip(), flags=re.I).strip()
        feature_class, text = extract_feature(text)

        text_clean = text
        pron_regex = Pronouns(lang).as_regex()
        disambiguate = True
        if re.match(pron_regex, text):
            text_clean = re.sub(pron_regex, '', text)
            disambiguate = False
        article_prefix = ARTICLE_REGEX.get('lang', ARTICLE_REGEX['en']) + '(?=[a-zA-Z])'
        if re.match(article_prefix, text):
            text_clean = re.sub(article_prefix, '', text)
            disambiguate = False

        # TODO
        if not text_clean:
            return None

        typ = VocManager.get('fragrant-spaces').interlink(text_clean, lang, fallback=None)
        if typ or not disambiguate:
            return Place(text, typ)

        if text in cache:
            if cache[text] is None:  # already searched, no match
                return Place(text)
            else:  # we have it in the cache!
                return URIRef(to_geonames_uri(cache[text]))

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
