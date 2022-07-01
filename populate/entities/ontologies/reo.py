from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class REO(DefinedNamespace):
    """
    READ-IT ongoing
    
    
    
    Generated from: https://read-it.acc.hum.uu.nl/ontology#
    Date: 2022-07-01 15:44:26.681770

    owl:imports <http://www.cidoc-crm.org/cidoc-crm/>
    owl:versionInfo "Exported from OntoME: READ-IT ongoing"
    """

    # http://www.w3.org/2002/07/owl#Class
    REO1: URIRef  # Circumstances
    REO10: URIRef  # Nationality
    REO11: URIRef  # Occupation
    REO12: URIRef  # Outcomes (external processes)
    REO13: URIRef  # Position
    REO14: URIRef  # Provenance
    REO15: URIRef  # Religion
    REO16: URIRef  # Status
    REO17: URIRef  # Habit
    REO18: URIRef  # Aim
    REO19: URIRef  # Reading Ability
    REO2: URIRef  # Disposition
    REO20: URIRef  # Understanding
    REO21: URIRef  # Emotions
    REO22: URIRef  # Evaluation
    REO23: URIRef  # Effects (internal processes)
    REO26: URIRef  # Summary
    REO27: URIRef  # Mental Imagery
    REO28: URIRef  # Memories (of reading)
    REO29: URIRef  # Memories (other)
    REO3: URIRef  # Environment
    REO30: URIRef  # Expectations
    REO31: URIRef  # Action
    REO32: URIRef  # Change in Thinking
    REO33: URIRef  # Output
    REO35: URIRef  # Age
    REO36: URIRef  # Citizenship
    REO37: URIRef  # Linguistic Communities
    REO38: URIRef  # Ethnic Communities
    REO39: URIRef  # Educational Level
    REO4: URIRef  # Frequency
    REO40: URIRef  # Subject Matter
    REO41: URIRef  # Medium
    REO42: URIRef  # Effects/Outcomes
    REO5: URIRef  # Gender
    REO6: URIRef  # Genre
    REO7: URIRef  # Intensity
    REO8: URIRef  # Lighting
    REO9: URIRef  # Location

    # http://www.w3.org/2002/07/owl#ObjectProperty
    has_age: URIRef  # has age
    has_aim: URIRef  # has aim
    has_citizenship: URIRef  # has citizenship
    has_disposition: URIRef  # has disposition
    has_educational_level: URIRef  # has educational level
    has_frequency: URIRef  # has frequency
    has_genre: URIRef  # has genre
    has_habit: URIRef  # has habit
    has_intensity: URIRef  # has intensity
    has_medium: URIRef  # has medium
    has_nationality: URIRef  # has nationality
    has_provenance: URIRef  # has provenance
    has_religion: URIRef  # has religion
    has_skill: URIRef  # has reading ability
    has_status: URIRef  # has status
    is_context_of: URIRef  # is context of
    is_gender_of: URIRef  # is gender of
    is_occupation_of: URIRef  # is occupation of
    readP1: URIRef  # has occupation
    readP10: URIRef  # is outcome type of
    readP11: URIRef  # is disposition of
    readP12: URIRef  # is habit of
    readP13: URIRef  # is reading ability of
    readP15: URIRef  # is aim of
    readP17: URIRef  # is effect type of
    readP2: URIRef  # is nationality of
    readP21: URIRef  # is age of
    readP22: URIRef  # is citizenship of
    readP23: URIRef  # is educational level of
    readP24: URIRef  # is member of (linguistic communities)
    readP25: URIRef  # is member of (ethnic communities)
    readP26: URIRef  # is medium of
    readP27: URIRef  # is triggered by (effects)
    readP28: URIRef  # is triggered by (outcomes)
    readP29: URIRef  # is name of
    readP29i_has_appellation: URIRef  # has name
    readP3: URIRef  # has gender
    readP4: URIRef  # is religion of
    readP5: URIRef  # is genre of
    readP56_has_context: URIRef  # has context
    readP6: URIRef  # is provenance of
    readP7: URIRef  # is status of
    readP8: URIRef  # is frequency of
    readP9: URIRef  # is intensity of

    # Valid non-python identifiers 
    _extras = ['REO43_Appellation_(temporal_entity)', 'has_member_(ethnic_communities)',
               'has_member_(linguistic_communities)', 'has_part_(effects)', 'has_part_(outcomes)', 'triggers_(effects)',
               'triggers_(outcomes)']

    _NS = Namespace("https://read-it.acc.hum.uu.nl/ontology#")
