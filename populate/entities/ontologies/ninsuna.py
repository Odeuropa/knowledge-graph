from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class NINSUNA(DefinedNamespace):
    """
    NinSuna Ontology
    
    The base ontology of the NinSuna platform. It is, amongst others, used to perform model-driven content
    adaptation
    
    Generated from: /Users/pasquale/git/odeuropa-kg/dump/ontology/ninsuna.ttl
    Date: 2022-09-28 15:22:17.188146

    a owl:Thing
    dc:creator <http://multimedialab.elis.ugent.be/dvdeurse-foaf.rdf#me>
    dc:format "OWL Full"
    dc:identifier "nsa"
    dc:language "English"
    dc:publisher <http://multimedialab.elis.ugent.be>
    rdfs:seeAlso <http://ninsuna.elis.ugent.be/>
        <http://www.springerlink.com/content/461380502m756877/>
    """

    # http://www.w3.org/2002/07/owl#Class
    CombinedMediaFragment: URIRef  # Represents a media fragment combining multiple media fragment axes.
    SpatialFragment: URIRef  # Represents a spatial media fragment.
    SpatialUnit: URIRef  # Represents a spatial unit.
    TemporalFragment: URIRef  # Represents a temporal media fragment.
    TemporalUnit: URIRef  # Represents a temporal unit.

    # http://www.w3.org/2002/07/owl#DatatypeProperty
    maxBitrate: URIRef  # The maximum bit rate (in kbps) of a media resource.
    spatialH: URIRef  # The height of the spatial fragment.
    spatialW: URIRef  # The width of the spatial fragment.
    spatialX: URIRef  # The x position of the spatial fragment.
    spatialY: URIRef  # The y position of the spatial fragment.
    temporalEnd: URIRef  # The end time in terms of seconds (in case of npt and smpte time unites) or date-time (in case of clock unit) of the temporal fragment.
    temporalStart: URIRef  # The start time in terms of seconds (in case of npt and smpte time unites) or date-time (in case of clock unit) of the temporal fragment.

    # http://www.w3.org/2002/07/owl#ObjectProperty
    combines: URIRef  # Points to the different media fragments to combine.
    hasMediaFragment: URIRef  # Points to a media fragment.
    isMediaFragmentOf: URIRef  # isMediaFragmentOf
    spatialUnit: URIRef  # Points to a spatial unit.
    temporalUnit: URIRef  # Points to a temporal unit.

    _NS = Namespace("http://organon.elis.ugent.be/ontologies/ninsuna#")
