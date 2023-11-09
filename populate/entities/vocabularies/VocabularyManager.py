import spacy
from .lemma import Lemma
from .vocabulary import Vocabulary

nlp = {
    'en': spacy.load("en_core_web_sm"),
    'fr': spacy.load("fr_core_news_sm"),
    'nl': spacy.load("nl_core_news_sm"),
    'de': spacy.load("de_core_news_sm"),
    'it': spacy.load("it_core_news_sm")
}

controller = {}

ARTICLE_REGEX = {
    'en': r'(?i)^(the|an?|some( of( the)?)?|any|this|that|th[eo]se) ',
    'it': r"(?i)^((?:l[ea]|gli|il?|dei|delle|un[oa]?) |l ?' ?|quest('|[oaei] )|"
          r"quei|quel( |l ?' ?|l[oaei] |poco|qualche|un po' di))",
    'fr': r"(?i)^((?:les?|la|des?|du|une?) |l ?' ?)",
    'de': r'(?i)^(die|das|de[rnms]?|ein(e[smnr]?)?|eene? ) ',
    'nl': r"(?i)^(de|het|een|' ?t) ",
    'sl': r''  # no articles in slovene
}


class VocabularyController:
    def __init__(self, scheme, endpoint, name=None):
        self.scheme = scheme
        self.endpoint = endpoint
        self.name = name or scheme

    def get(self, lemma):
        return Vocabulary.get_all(self.name, self.scheme, self.endpoint).get(lemma)

    def search(self, q, lang='en', n=10, autocomplete=False):
        voc = Vocabulary.get_all(self.name, self.scheme, self.endpoint)
        if not q:
            return voc
        return voc.search(q, lang, n, autocomplete)

    def interlink(self, word, lang='en', fallback=None, disable_preproc=False):
        # TODO repeat without adjectives if not found?
        if len(word) < 3:
            return None, None
        q = word.lower()

        if not disable_preproc and lang in nlp:
            tk = nlp[lang](q)
            tokens = []
            root_found = False
            for x in tk:
                if not root_found and x.dep_ in ['det', 'quantmod']:
                    continue

                tokens.append(x)
                if x.dep_ == 'ROOT':
                    root_found = True

            if len(tokens) == 1 and tokens[0].pos_ == 'PRON' and tokens[0].text != 'aegypt':
                # TODO detect male and females, detect me and you
                return None, 'Pronoun'
                # return 'http://data.odeuropa.eu/vocabulary/olfactory-objects/539', 'person'
            q = ' '.join([x.lemma_ if x.pos_ == 'NOUN' else x.text for x in tokens])
        lms = self.search(q, lang, 1, False).lemmata
        x = lms[0] if lms else None

        # the score can be lower if the word is longer
        if x is not None and (x.score >= 0.8 or (x.score >= 0.7 and len(q) > 7)):
            return x.id, x.collection
        elif fallback == 'text':
            return word, None
        elif fallback == 'best':
            return x.id, x.collection
        else:
            return None, None

    def interlink_long(self, q, lang='en', fallback=None):
        # TODO for long texts, for which we want to "classify" rather than match
        pass


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


def get(identifier):
    global controller
    return controller[identifier]


def interlink_multiple(label, lang, vocs):
    for x in vocs:
        uri, type = get(x).interlink(label, lang, fallback=None, disable_preproc='gesture' in x)
        if uri is not None:
            return uri, type, x
    return None, None, None
