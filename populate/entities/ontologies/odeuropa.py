from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class OD(DefinedNamespace):
    """
    Generated from: https://raw.githubusercontent.com/Odeuropa/ontology/master/odeuropa-ontology.owl
    Date: 2021-11-17 19:00:07.066966

    <http://data.odeuropa.eu/ontology> owl:imports crm:
    owl:versionInfo "0.2"
    """

    # http://www.w3.org/2002/07/owl#AsymmetricProperty
    F1_generated: URIRef  #
    F2_perceived: URIRef  #
    F7_has_species: URIRef  #

    # http://www.w3.org/2002/07/owl#Class
    L11_Smell: URIRef  #
    L12_Smell_Emission: URIRef  #
    L13_Olfactory_Experience: URIRef  # 
    L14_Smell_Transformation: URIRef  # 
    L15_Smell_Interaction: URIRef  #
    L16_Odorizing: URIRef  #
    L1_Sensory_Stimulus: URIRef  #
    L2_Stimulus_Generation: URIRef  # 
    L3_Sensory_Experience: URIRef  #
    L4_Stimuli_Transformation: URIRef  # 
    L5_Stimuli_Interaction: URIRef  # 
    L6_Animal: URIRef  #
    L7_Gesture: URIRef  #

    # http://www.w3.org/2002/07/owl#ObjectProperty
    F10_targeted: URIRef  #
    F9_involved_smell: URIRef  #
    F3_had_source: URIRef  #
    F4_had_carrier: URIRef  #
    F5_involved_gesture: URIRef  #
    F6_evoked: URIRef  #
    F8_has_nose_quality: URIRef  #

    _NS = Namespace("http://data.odeuropa.eu/ontology/")
