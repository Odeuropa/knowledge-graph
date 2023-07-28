import rdflib.plugins.parsers.notation3
import validators
import numpy as np
from rdflib import Graph, URIRef, Literal, TIME, SDO, OWL, PROV, RDF, XSD
from .ontologies import *
from .Entity import Entity

g = Graph()

ODEUROPA_PROJECT = URIRef('http://data.odeuropa.eu/odeuropa')


def set_prefixes(gx):
    gx.bind("od", ODEUROPA)
    gx.bind("crm", CRM)
    gx.bind("crmsci", CRMsci)
    gx.bind("time", TIME)
    gx.bind("schema", SDO)
    gx.bind("owl", OWL)
    gx.bind("oa", OA)
    gx.bind("ma", MA)
    gx.bind("reo", REO)
    gx.bind("prov", PROV)
    gx.bind("nsa", NINSUNA)


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

    if isinstance(lang, URIRef):
        statement = (subj, pred, Literal(obj, datatype=lang))
    elif isinstance(obj, URIRef) or isinstance(obj, Literal):
        statement = (subj, pred, obj)
    elif type(obj) == float:
        statement = (subj, pred, Literal(str(obj), datatype=XSD.float))
    elif validators.url(str(obj)):
        statement = (subj, pred, URIRef(obj))
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
    add_rdfstar(statement, PROV.wasGeneratedBy, prov.res)
    pass


def set_score(statement, score):
    if not statement or not score:
        return
    # under development in rdflib https://github.com/RDFLib/rdflib/discussions/1554
    # workaround = use a string and then re-convert afterwords
    add_rdfstar(statement, RDF.value, score)
    pass

def add_rdfstar(s, p, o):
    if type(s) == tuple:
        s = wrap_statement(s)
    if type(o) == tuple:
        o = wrap_statement(o)
    return add(s, p, o)


def is_invalid(what):
    return what is None or what == '' or (type(what) == float and np.isnan(what))


reset()

