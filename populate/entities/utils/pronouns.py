class Pronouns:
    def __init__(self, lang):
        with open(f'./entities/utils/pronouns_{lang}.txt', 'r') as f:
            self.lst = [x.strip() for x in f.readlines()]

    def as_regex(self):
        return '^(' + '|'.join(self.lst) + ')'
