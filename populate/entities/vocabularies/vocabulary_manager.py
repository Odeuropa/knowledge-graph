import re
from nltk.stem import WordNetLemmatizer as Lemmatizer
from .lemma import Lemma
from .vocabulary import Vocabulary

import nltk

nltk.download('omw-1.4')

controller = {}

ARTICLE_REGEX = {
    'en': r'^(the|an?|some|any) ',
    'it': r'^(le|gli|il?|dei|delle|un[oa]?) ',
    'fr': r'^(les?|la|des?|du|une?) '
}


class VocabularyController:
    def __init__(self, scheme, endpoint, name=None):
        self.scheme = scheme
        self.endpoint = endpoint
        self.name = name or scheme

    def get(self, lemma):
        return Vocabulary.get_all(self.name, self.scheme, self.endpoint).get(lemma)

    def search(self, q, lang, n=10, autocomplete=False):
        voc = Vocabulary.get_all(self.name, self.scheme, self.endpoint)
        if not q:
            return voc
        return voc.search(q, lang, n, autocomplete)

    def interlink(self, q, lang='en', fallback=None):
        q = re.sub(ARTICLE_REGEX.get(lang, ARTICLE_REGEX['en']), '', q.lower())
        lemmatizer = Lemmatizer()
        q = lemmatizer.lemmatize(q)
        x = self.search(q, lang, 1, False).lemmata[0]
        if x.score > 0.6:
            return x.id
        elif fallback == 'text':
            return q
        else:
            return None


def setup(opt):
    global controller
    if not opt or 'vocabularies' not in opt:
        raise Exception('Bad options for VocabularyManager')

    Lemma.set_weights(opt['weights'])
    endpoint = opt['endpoint']
    vocabularies = opt['vocabularies']
    families = set([vocabularies[k]['family'] for k in vocabularies if 'family' in vocabularies[k]])

    for k in vocabularies:
        scheme = vocabularies[k]['scheme']
        controller[k] = VocabularyController(scheme, endpoint)

    for family in families:
        vocs = [vocabularies[k] for k in vocabularies]
        vocs = [v for v in vocs if v.get('family') == family]
        vocs.sort(key=lambda v: v.get('priority', 0))

        controller[family] = VocabularyController([v['scheme'] for v in vocs], endpoint, family)


def listing():
    global controller
    return controller.keys()


def get(id):
    global controller
    return controller[id]
