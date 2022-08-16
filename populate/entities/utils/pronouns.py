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


class Pronouns:
    def __init__(self, lang):
        with open(f'./entities/utils/pronouns_{lang}.txt', 'r') as f:
            self.lst = [x.strip() for x in f.readlines()]

    def as_regex(self):
        return '^(' + '|'.join(self.lst) + ')$'

    @classmethod
    def myself(cls, lang):
        return MYSELF.get(lang, [])

    @classmethod
    def is_pronoun(cls, what, lang):
        return what in MYSELF.get(lang, []) or what in HER.get(lang, [])
