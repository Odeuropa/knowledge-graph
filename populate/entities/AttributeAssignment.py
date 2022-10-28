import re
from os import path
from rdflib import URIRef, RDFS, RDF
from urllib import parse as urlparse

from .ontologies import CRM
from .config import BASE
from .Entity import Entity
from .Graph import add
from .vocabularies import VocabularyManager as VocManager

nlp = VocManager.nlp

ROLES = {}


def get_role(role):
    if role not in ROLES:
        r = URIRef(path.join(BASE, 'attribute-type', role))
        add(r, RDF.type, CRM.E55_Type)
        add(r, RDFS.label, role)
        ROLES[role] = r

    return ROLES[role]


class AttributeAssignment(Entity):
    def __init__(self, uri, adjective, lang, smell, perceiver):
        self.uri = uri
        self.res = URIRef(uri)

        lemma = None
        role = None
        # TODO link even if contains words as 'very', 'too', ...
        adjective = re.sub(r'tr[èeé]s ?- ?', 'très ', adjective)
        modifier = None

        if adjective not in ['very']:

            for role in ['intensity', 'hedonic', 'character']:
                lemma, _ = VocManager.get(role).interlink(adjective, lang)
                if lemma is not None:
                    # print(adjective, lemma)
                    break

            if lemma is None and lang in nlp.keys():
                # cases: very good, less intense ...
                doc = nlp[lang](adjective)
                roles = [token.dep_ for token in doc]
                if len(roles) > 1 and roles.count('ROOT') == 1 and \
                        (roles.count('ROOT') + roles.count('advmod') == len(doc)):
                    t = doc[roles.index('ROOT')].lemma_
                    for role in ['intensity', 'hedonic', 'character']:
                        lemma, _ = VocManager.get(role).interlink(t, lang)
                        if lemma is not None:
                            break
                    modifier = ' '.join([token.text for token in doc if token.dep_ == 'advmod'])

        self.set_class(CRM.E13_Attribute_Assignment)
        self.add_label(adjective, lang)
        self.add(RDFS.comment, modifier, lang)

        self.add(CRM.P141_assigned, lemma or Attribute(adjective, lang))

        if lemma is not None:
            self.add(CRM.P2_has_type, get_role(role))

        self.add(CRM.P140_assigned_attribute_to, smell)
        self.add(CRM.P14_carried_out_by, perceiver)


class Attribute(Entity):
    def __init__(self, adjective, lang):
        self.uri = path.join(BASE, 'attribute', urlparse.quote(adjective) + '_' + lang)
        self.res = URIRef(self.uri)
        self.set_class(CRM.E90_Symbolic_Object)
        self.add_label(adjective, lang)
