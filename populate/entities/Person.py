from . import Actor


class Person(Actor):
    def __init__(self, name, anonymize=False):
        super().__init__(name, anonymize=anonymize, is_person=True)
