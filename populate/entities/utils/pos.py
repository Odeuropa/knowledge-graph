MYSELF = {
    'en': ['i', 'me', 'my', 'myself', 'mine'],
    'it': ['io', 'me', 'mio', 'mia', 'miei', 'mie', 'io stesso', 'me stesso'],
    'fr': ['je', 'moi', 'moi même', 'mon', 'ma', 'mes']
}

HER = {
    'en': ['her'],
    'it': ['lei', 'ella', 'essa'],
    'fr': ['elle', 'lui']
}

root = './entities/utils/pos_lang'


class Pronouns:
    def __init__(self, lang):
        with open(f'{root}/pronouns_{lang}.txt', 'r') as f:
            self.lst = [x.strip() for x in f.readlines()]

    def as_regex(self):
        return '^(' + '|'.join(self.lst) + ')$'

    @classmethod
    def myself(cls, lang):
        return MYSELF.get(lang, [])

    @classmethod
    def is_pronoun(cls, what, lang):
        return what in MYSELF.get(lang, []) or what in HER.get(lang, [])


class Prepositions:
    def __init__(self, lang):
        with open(f'{root}/preposition_{lang}.txt', 'r') as f:
            self.lst = [x.strip() for x in f.readlines()]
            self.lst = [(x if x.endswith("'") else x + ' ') for x in self.lst]

    def as_regex(self, as_start=False):
        prep = '^' if as_start else ''
        return prep + '(' + '|'.join(self.lst) + '| )+'
