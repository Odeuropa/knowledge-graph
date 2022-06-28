import Levenshtein


def move(array, oldIndex, newIndex):
    array.insert(newIndex, array.pop(oldIndex))
    return array


def as_array(input):
    if not input:
        return []
    if isinstance(input, list):
        return input
    return [input]


DEFAULT_OPTIONS = {
    'unique': True,
    'includesUntagged': False,
}


def computeSimilarityScore(l, q, accepted, autocomplete, lowerBound):
    value = l['@value'] if '@value' in l else l

    if not value or not isinstance(value, str):
        return 0

    value = value.lower()
    if autocomplete and q in value:
        return 1

    curlang = l['@language']
    langQuality = Lemma.OTHER_LANG_WEIGHT if accepted else 1  # untagged values
    # if accepted and curlang:
    # langQuality = [a.quality for a in accepted if a.code.startswith(curlang)]  # FIXME
    # langQuality = langQuality[0] if len(langQuality) > 0 else lowerBound
    if accepted == curlang:
        langQuality = 1

    score = Levenshtein.ratio(q, value)
    value_comp = q[0:-1] if accepted[0:2] == 'it' else q
    startQual = 1 if value.startswith(value_comp) else Lemma.UNMATCHING_START_WEIGHT
    return score * langQuality * startQual


class Lemma:
    ALT_WEIGHT = 0.7
    OTHER_LANG_WEIGHT = 0.6
    UNMATCHING_START_WEIGHT = 0.7

    def __init__(self, data, score=0):
        self.data = data
        self.prefLabel = as_array(data['prefLabel'])
        self.altLabel = as_array(data.get('altLabel'))
        self.id = data['@id']
        self.collection = data.get('collection', None)
        self.score = score

        for x in as_array(self.data.get('exactMatch', [])):
            if 'prefLabel' in x:
                self.prefLabel.extend(as_array(x['prefLabel']))
                self.altLabel.extend(as_array(x.get('altLabel')))

        self.labels = self.prefLabel + self.altLabel
        self.untagged = [x for x in self.labels if '@language' not in x]

    def flatten(self, lang='en'):
        l = {
            'id': self.id,
            'label': self.pick_best_lang(lang, {'unique': True}),
            'confidence': self.score
        }
        return l

    def pick_best_lang(self, accepted, options={}, array=None):
        opt = DEFAULT_OPTIONS | options
        _list = array or self.prefLabel
        if not list or not len(_list):
            return None if opt['unique'] else []

        if len(_list) == 1:
            label = _list[0]['@value'] if '@value' in _list[0] else _list[0]
            return label if opt['unique'] else [label]

        first = accepted[0, 2]

        available = [x['@language'] for x in _list if x and '@language' in x]

        if 'en' in available:
            available = move(available, available.index('en'), 0)

        best = first if first in available else available[0]

        pick_untagged = not best or (not best.startswith(first) and not best.startswith('en'))

        if pick_untagged:
            label = self.untagged
        else:
            label = [x for x in _list if x['@language'] == best]
            if opt['includesUntagged']:
                label.extend(self.untagged)

        if not label:
            # prefer latin transliterations
            label = [x for x in _list if x['@language'] and x['@language'].lower().endswith('latn')]

        if not label:
            label = [_list[0]]

        label = [l['@value'] if '@value' in l else l for l in label]

        return label[0] if opt['unique'] else label

    def similar_to(self, q, lang, autocomplete=False):
        q = q.lower()
        lowerBound = 0.2

        scores = [computeSimilarityScore(l, q, lang, autocomplete, lowerBound) for l in self.prefLabel]

        altScores = [computeSimilarityScore(l, q, lang, autocomplete, lowerBound) for l in self.altLabel]
        altScores = [s * Lemma.ALT_WEIGHT for s in altScores]

        return max(scores + altScores)

    @classmethod
    def set_weights(cls, weights):
        if not weights:
            return

        Lemma.ALT_WEIGHT = weights['alternate_labels'] or Lemma.ALT_WEIGHT
        Lemma.OTHER_LANG_WEIGHT = weights['other_languages'] or Lemma.OTHER_LANG_WEIGHT
        Lemma.UNMATCHING_START_WEIGHT = weights['unmatching_start'] or Lemma.UNMATCHING_START_WEIGHT
