import validators
import numpy as np
from rdflib import Graph, URIRef, Literal, TIME, SDO, OWL, PROV
from .ontologies import *
from .Entity import Entity

g = Graph()


def set_prefixes(gx):
    gx.bind("od", ODEUROPA)
    gx.bind("crm", CRM)
    gx.bind("crmsci", CRMsci)
    gx.bind("time", TIME)
    gx.bind("schema", SDO)
    gx.bind("owl", OWL)
    gx.bind("oa", OA)
    gx.bind("ma", MA)


def reset():
    global g
    g = Graph()

    set_prefixes(g)


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


def wrap_statement(statement):
    gx = Graph()
    set_prefixes(gx)
    gx.add(statement)
    gxt = gx.serialize(format='ttl').split(' .')[-2].strip()
    return Literal(f"<< {gxt} >>")


def set_prov(statement, prov):
    if not statement or not prov:
        return
    # under development in rdflib https://github.com/RDFLib/rdflib/discussions/1554
    # workaround = use a string and then re-convert afterwords
    g.add((wrap_statement(statement), PROV.wasGeneratedBy, prov.res))
    pass


def is_invalid(what):
    return what is None or what == '' or (type(what) == float and np.isnan(what))


reset()
