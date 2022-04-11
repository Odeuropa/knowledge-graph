from SPARQLTransformer import sparqlTransformer
from .lemma import Lemma

SKOS = 'http://www.w3.org/2004/02/skos/core#'


class Vocabulary:
    list = {}

    @classmethod
    def createVocabulary(cls, name, trunkNamespace, namespaces, prop, lang):
        Vocabulary.add(name, Vocabulary(name, trunkNamespace, namespaces, prop, lang))

    @classmethod
    def add(cls, name, vocabulary):
        Vocabulary.list[name] = vocabulary

    @classmethod
    def load(cls, name, schema, endpoint):
        query = {
            '@context': SKOS,
            '@graph': [{
                '@type': 'Concept',
                '@id': '?id',
                'prefLabel': '$skos:prefLabel$required',
                'altLabel': '$skos:altLabel|skos:hiddenLabel',
                'exactMatch': '$skos:exactMatch',
                'inScheme': '?namespace',
                'collection': '$skos:member$reverse'
            }],
            '$where': '{ ?id skos:inScheme|skos:topConceptOf ?namespace } UNION { ?namespace skos:member ?id}',
            '$values': {
                'namespace': schema,
            },
            '$prefixes': {
                'skos': 'http://www.w3.org/2004/02/skos/core#'
            }
        }
        options = {
            'endpoint': endpoint,
            'debug': False}
        result = sparqlTransformer(query, options)

        if isinstance(schema, list):
            result['@graph'].sort(key=lambda _x: schema.indexOf(_x))

            def search_id(ex):
                lemma = next((l for l in result['@graph'] if l['@id'] == ex), None)
                if lemma:
                    result['@graph'].pop(result['@graph'].indexOf(lemma))
                    return lemma
                return ex

            for x in result['@graph']:
                if 'exactMatch' in x:
                    if x not in result['@graph']:
                        continue

                    exm = x['exactMatch']
                    if not isinstance(exm, list):
                        exm = [exm]
                    x.exactMatch = [search_id(ex) for ex in exm]

        voc = Vocabulary(result, schema)
        Vocabulary.add(name, voc)
        return voc

    @classmethod
    def get_all(cls, name, scheme, endpoint):
        if name not in Vocabulary.list:
            Vocabulary.load(name, scheme, endpoint)
        return Vocabulary.list[name]

    def __init__(self, data, family=None):
        self.family = family
        if isinstance(data, list):
            self.lemmata = data
            return

        self.lemmata = [Lemma(l) for l in data['@graph']]

    def flatten(self, lang='en'):
        return [l.flatten(lang) for l in self.lemmata]

    def get_data(self):
        return {
            '@context': SKOS,
            '@graph': [l.data for l in self.lemmata]
        }

    def get(self, _id):
        return Vocabulary([l for l in self.lemmata if l.id == _id])

    def autocomplete(self, q, lang, n=10):
        return self.search(q, lang, n, True)

    def search(self, q, lang, n=10, autocomplete=False):
        matches = [Lemma(l.data, l.similar_to(q, lang, autocomplete)) for l in self.lemmata]
        matches.sort(key=lambda a: -a.score)
        matches = [a for a in matches if a.score][0:n]
        return Vocabulary(matches)
