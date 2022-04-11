from .Entity import Entity
from .ontologies import CRM


class Thing(Entity):
    def __init__(self, seed, label):
        super().__init__(seed)
        self.setclass(CRM.E1_CRM_Entity)
        self.add_label(label)
