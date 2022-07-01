"""from https://github.com/hsolbrig/definednamespace/blob/master/generators/generate_namespace.py """
import datetime
import re
import sys
import textwrap
from argparse import ArgumentParser
from keyword import kwlist
from typing import Dict, List, Union, Optional, Tuple

import requests
from rdflib import Graph, URIRef, Namespace, SKOS, RDFS, RDF, OWL, Literal, BNode
from rdflib.plugin import plugins as rdflib_plugins, Parser as rdflib_Parser


def fill_template(namespace: str, header: str, body: str) -> str:
    return f"""from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace
class {namespace.upper()}(DefinedNamespace):
    {header}
    {body}
"""


COMMENT_COL = 24  # Column for output columns

# Priority given to possible descriptions of individual elements
# Note: For no good reason we will use english text if it is available
descriptions = [
    SKOS.definition,
    SKOS.prefLabel,
    RDFS.comment,
    RDFS.label
]

# Indent level -- don't use "\t" in Python as it messes up other edits
TAB = "    "


def strident(s: str) -> str:
    return s


def manual(url: str) -> str:
    """ Fetch a URL with a turtle header """
    resp = requests.get(url, headers={"Accept": "text/turtle"})
    return resp.text


def generate_namespace(namespace: str, uri: Union[str, URIRef, Namespace], rdf_loc: Union[str, URIRef, Namespace],
                       rdf_format: str = "turtle") -> str:
    """
    Return a Python module that represents the namespace
    :param namespace: Namespace to generate (e.g. "skos")
    :param uri: Namespace uri (e.g. "http://www.w3.org/2004/02/skos/core#")
    :param rdf_loc: file or URL of rdf
    :param rdf_format: format of RDF
    :return: text for resource
    """
    g = Graph()
    # 'manual' format is a hack -- turtle format with accept header
    print(rdf_format)
    if rdf_format == 'manual':
        g.parse(data=manual(rdf_loc), format="turtle")
    else:
        g.load(rdf_loc, format=rdf_format)
    uri = URIRef(str(uri))
    g.bind(namespace.lower(), uri)

    return fill_template(namespace, _hdr(g, uri, rdf_loc), _body(g, uri))


def _hdr(g: Graph, uri: URIRef, url: str) -> str:
    """
    Generate a class header for URI
    :param g: Graph containing entire ontology
    :param uri: Ontology base to use for entries w/o ontology header
    :param url: URL that data was loaded from
    :return: String representation of class docstring
    """

    def wrap(s: str) -> str:
        return ('\n' + TAB).join(textwrap.wrap(s, width=110))

    # See whether we've got an ontology defined
    ontology_list = list(g.subjects(RDF.type, OWL.Ontology))
    if not ontology_list:
        ontology_list = [uri]

    # Copy the information that describes the ontology itself, ignoring anything complex (w/ BNodes)
    g2 = Graph()
    g2.namespace_manager = g.namespace_manager

    # List of lines to emit with corresponding sort order
    lines: List[Tuple[int, str]] = [(0, '"""'), (1000, '"""')]
    entry = 0
    for s in ontology_list:
        entry += 1
        order = entry * 10
        has_title = False
        has_description = False
        for p, o in g.predicate_objects(s):
            if not isinstance(o, BNode) and o != OWL.Ontology:
                if not has_title and ('title' in str(p) or 'label' in str(p)) and \
                        isinstance(o, Literal) and (not o.language or o.language == 'en'):
                    lines.append((order, wrap(str(o.value))))
                    lines.append((order + 1, ''))
                    has_title = True
                elif not has_description and ('description' in str(p) or 'comment' in str(p)) and \
                        isinstance(o, Literal) and (not o.language or o.language == 'en'):
                    lines.append((order + 3, wrap(str(o.value))))
                    lines.append((order + 4, ''))
                    has_description = True
                else:
                    g2.add((s, p, o))

    # Add the information header
    lines.append((90, f"Generated from: {url}"))
    lines.append((91, f"Date: {datetime.datetime.now()}\n"))

    # Prettify the class docstring
    order = 100
    for l in g2.serialize(format="turtle").split('\n'):
        if l and '@prefix' not in l:
            l = re.sub(r';$', '', re.sub(r'.$', '', l))
            l = l.replace('"""', "'''").replace('\\r', '\n').replace('@en', '').rstrip()
            if l.startswith(' '):
                l = re.sub(r'^ {4}', '', l)
            else:
                l = re.sub(r'\w+: ', '', l)
            lines.append((order, wrap(l)))
            order += 1

    return f"\n{TAB}".join([l[1] for l in sorted(lines)])


def _longest_type(s: URIRef, default: URIRef, g: Graph) -> URIRef:
    """
    Return the longest value associated with s, p, the general notion being that the longest is probably the most
    specific
    :param s: subject
    :param default: default value
    :param g: Graph
    :return: Longest value or default
    """
    rval = ""
    for o in sorted(g.objects(s, RDF.type)):
        if len(str(o)) > len(rval):
            rval = str(o)
    return URIRef(rval) if rval else default


def _description_for(node: URIRef, g: Graph) -> str:
    """
    Locate the most appropriate description for node in g
    :param node: Subject to look for a description on
    :param g: containing graph
    :return: Resulting description
    """
    rval = ""
    for p in descriptions:
        for desc in g.objects(node, p):
            if isinstance(desc, Literal) and (not desc.language or desc.language == 'en'):
                return str(desc)
            elif not rval:
                rval = str(desc)
        if rval:
            return str(rval)
    return rval


def _body(g: Graph, uri: URIRef) -> str:
    """
    Create the body of a DefinedNamespace from standard RDF
    :param g: Graph
    :param uri: Prefix to generate
    :return: Body for a DefinedNamespace
    """
    contents: Dict[URIRef, List[URIRef]] = dict()
    rval = ""

    # Sort the subjects in the namespace by type
    for s in sorted(set(g.subjects())):
        if str(s).startswith(uri):
            contents.setdefault(_longest_type(s, RDFS.Resource, g), []).append(s)

    uri_str = str(uri)
    extras: List[URIRef] = []
    for k in sorted(contents.keys()):
        vs = contents[k]
        if len(vs) and str(vs[0])[len(uri_str):]:
            rval += f"\n{TAB}# {k}\n"
            for v in sorted(vs):
                ident = str(v)[len(uri_str):]
                if ident.isidentifier() and not ident in kwlist:
                    doc = _description_for(v, g).strip().replace('\n', ' ')
                    pad = max(COMMENT_COL - len(ident), 2) * " "
                    rval += f"{TAB}{ident}: URIRef{pad}# {doc}\n"
                else:
                    extras.append(ident)  # Identifiers that aren't valid python

    if extras:
        extra_list = ', '.join([f"'{e}'" for e in extras])
        rval += f"\n{TAB}# Valid non-python identifiers "
        rval += f"\n{TAB}_extras = [{extra_list}]\n"
    rval += f'\n{TAB}_NS = Namespace("{uri}")'
    return rval


def genargs() -> ArgumentParser:
    """
    Generate an input string parser
    :return: parser
    """
    possible_formats = sorted(list(set(x.name for x in rdflib_plugins(None, rdflib_Parser) if '/' not in str(x.name))))

    parser = ArgumentParser(prog="generate_namespace", description="Generate a DefinedNamespace")
    parser.add_argument("prefix", help='Prefix to generate namespace for (example: skos)')
    parser.add_argument("uri", help="Prefix URI (example: http://www.w3.org/2004/02/skos/core#)")
    parser.add_argument("rdf_file", help="Location or URL of RDF file to parse")
    parser.add_argument("-f", "--format", help="RDF file format", choices=possible_formats, default="turtle")
    return parser


def main(argv: Optional[List[str]] = None):
    opts = genargs().parse_args(argv)
    with open(opts.prefix + '.py', 'w') as f:
        f.write(generate_namespace(opts.prefix, URIRef(opts.uri), opts.rdf_file, opts.format))


if __name__ == '__main__':
    main(sys.argv[1:])


#  python ontologies/generate_namespace.py -f xml od http://data.odeuropa.eu/ontology/  https://raw.githubusercontent.com/Odeuropa/ontology/master/odeuropa-ontology.owl
#  python ontologies/generate_namespace.py -f xml crm http://erlangen-crm.org/current/  https://raw.githubusercontent.com/Odeuropa/ontology/master/cidoc-crm.rdf
#  python ontologies/generate_namespace.py -f xml crmsci http://www.ics.forth.gr/isl/CRMsci/  https://raw.githubusercontent.com/Odeuropa/ontology/master/crmsci.rdf
#  python ontologies/generate_namespace.py -f ttl reo 'https://read-it.acc.hum.uu.nl/ontology#'  'https://read-it.acc.hum.uu.nl/ontology#'