from .Entity import Entity
from .ontologies import CRM


class Thing(Entity):
    def __init__(self, seed, label, lang):
        super().__init__(seed, 'thing')
        self.set_class(CRM.E70_Thing)
        self.add_label(label, lang)
