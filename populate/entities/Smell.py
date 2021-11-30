from .Entity import Entity
from .ontologies import ODEUROPA


class Smell(Entity):
    def __init__(self, seed):
        super().__init__(seed)
        self.setclass(ODEUROPA.L11_Smell)
