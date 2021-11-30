import numpy as np
from rdflib import Graph, URIRef, Literal
from .ontologies import *
from .Entity import Entity


def reset():
    global g
    g = Graph()

    g.bind("od", ODEUROPA)
    g.bind("crm", CRM)
    g.bind("crmsci", CRMsci)


def add(subj, pred, obj, lang=''):
    if is_invalid(subj) or is_invalid(pred) or is_invalid(obj):
        return
    if isinstance(obj, Entity):
        obj = obj.res
    if isinstance(subj, Entity):
        subj = subj.res

    if isinstance(obj, URIRef) or isinstance(obj, Literal):
        g.add((subj, pred, obj))
    else:
        g.add((subj, pred, Literal(obj, lang=lang)))


def is_invalid(what):
    return what is None or what == '' or (type(what) == float and np.isnan(what))


reset()
