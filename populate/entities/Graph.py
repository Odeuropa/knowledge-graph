import validators
import numpy as np
from rdflib import Graph, URIRef, Literal, TIME, SDO, OWL, PROV
from .ontologies import *
from .Entity import Entity


def reset():
    global g
    g = Graph()

    g.bind("od", ODEUROPA)
    g.bind("crm", CRM)
    g.bind("crmsci", CRMsci)
    g.bind("time", TIME)
    g.bind("schema", SDO)
    g.bind("owl", OWL)


def add(subj, pred, obj, lang=''):
    if is_invalid(subj) or is_invalid(pred) or is_invalid(obj):
        return
    if isinstance(obj, Entity):
        obj = obj.res
    if isinstance(subj, Entity):
        subj = subj.res

    if isinstance(obj, URIRef) or isinstance(obj, Literal):
        statement = (subj, pred, obj)
    elif validators.url(obj):
        statement = (subj, pred, URIRef(obj))
    elif isinstance(lang, URIRef):
        statement = (subj, pred, Literal(obj, datatype=lang))
    else:
        statement = (subj, pred, Literal(obj, lang=lang))

    g.add(statement)
    return statement


def set_prov(statement, prov):
    if not statement or not prov:
        return
    # under development in rdflib https://github.com/RDFLib/rdflib/discussions/1554
    # g.add((statement, PROV.wasGeneratedBy, prov))
    pass

def is_invalid(what):
    return what is None or what == '' or (type(what) == float and np.isnan(what))


reset()
