from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace
class MA(DefinedNamespace):
    """
    Created by Tobias Buerger, Jean Pierre Evain and Pierre-Antoine Champin with the RDFS Taskforce within the W3C
    Media Annotation Working Group.
    
    Generated from: http://www.w3.org/ns/ma-ont.ttl
    Date: 2022-04-08 15:52:36.712470

    <http://www.w3.org/ns/ma-ont> dc:date "2013-03-20"^^xsd:date
    rdfs:comment "THE CONTENT OF THIS MA-ONT.RDF AND DERIVED MA-ONT.TTL FILES PREVAIL OVER THE SPECIFICATION."
    owl:imports <http://dublincore.org/2008/01/14/dcelements.rdf>
    owl:versionInfo "R36"
    """
    
    # http://www.w3.org/2002/07/owl#Class
    Agent: URIRef                   # A person or organisation contributing to the media resource.
    AudioTrack: URIRef              # A specialisation of Track for Audio to provide a link to specific data properties such as sampleRate, etc. Specialisation is defined through object properties.
    Collection: URIRef              # Any group of media resource e.g. a series.
    DataTrack: URIRef               # Ancillary data track e.g. captioning  in addition to video and audio tracks. Specialisation is made through the use of appropriate object properties.
    Image: URIRef                   # A still image / thumbnail / key frame related to the media resource or being the media resource itself.
    Location: URIRef                # A location related to the media resource, e.g. depicted in the resource (possibly fictional) or where the resource was created (shooting location), etc.
    MediaFragment: URIRef           # A media fragment (spatial, temporal, track...) composing a media resource. In other ontologies fragment is sometimes referred to as a 'part' or 'segment'.
    MediaResource: URIRef           # An image or an audiovisual media resource, which can be composed of one or more fragment / track.
    Organisation: URIRef            # An organisation or moral agent.
    Person: URIRef                  # A physical person.
    Rating: URIRef                  # Information about the rating given to a media resource.
    TargetAudience: URIRef          # Information about The target audience (target region, target audience category but also parental guidance recommendation) for which a media resource is intended.
    Track: URIRef                   # A specialisation of MediaFragment for audiovisual content.
    VideoTrack: URIRef              # A specialisation of Track for Video to provide a link to specific data properties such as frameRate, etc. Signing is another possible example of video track. Specialisation is defined through object properties.

    # http://www.w3.org/2002/07/owl#DatatypeProperty
    alternativeTitle: URIRef        # Corresponds to 'title.title' in the Ontology for Media Resources with a 'title.type' meaning "alternative".
    averageBitRate: URIRef          # Corresponds to 'averageBitRate' in the Ontology for Media Resources, expressed in kilobits/second.
    collectionName: URIRef          # The name by which a collection (e.g. series) is known.
    copyright: URIRef               # Corresponds to 'copyright.copyright' in the Ontology for Media Resources.
    creationDate: URIRef            # Corresponds to 'date.date' in the Ontology for Media Resources with a 'date.type' meaning "creationDate".
    date: URIRef                    # Corresponds to date.date in the ontology for Media Resources. Subproperties can be used to distinguish different values of 'date.type'. The recommended range is 'xsd:dateTime' (for compliance with OWL2-QL and OWL2-RL) but other time-related datatypes may be used (e.g. 'xsd:gYear', 'xsd:date'...).
    description: URIRef             # Corresponds to 'description' in the Ontology for Media Resources. This can be specialised by using sub-properties e.g. 'summary' or 'script'.
    duration: URIRef                # Corresponds to 'duration' in the Ontology for Media Resources.
    editDate: URIRef                # Corresponds to 'date.date' in the Ontology for Media Resources with a 'date.type' meaning "editDate".
    fragmentName: URIRef            # Corresponds to 'namedFragment.label' in the Ontology for Media Resources.
    frameHeight: URIRef             # Corresponds to 'frameSize.height' in the Ontology for Media Resources, measured in frameSizeUnit.
    frameRate: URIRef               # Corresponds to 'frameRate' in the Ontology for Media Resources, in frame per second.
    frameSizeUnit: URIRef           # Corresponds to 'frameSize.unit' in the Ontology for Media Resources.
    frameWidth: URIRef              # Corresponds to 'frameSize.width' in the Ontology for Media Resources measured in frameSizeUnit.
    locationAltitude: URIRef        # Corresponds to 'location.altitude' in the Ontology for Media Resources.
    locationLatitude: URIRef        # Corresponds to 'location.latitude' in the Ontology for Media Resources.
    locationLongitude: URIRef       # Corresponds to 'location.longitude' in the Ontology for Media Resources.
    locationName: URIRef            # Corresponds to 'location.name' in the Ontology for Media Resources.
    locator: URIRef                 # Corresponds to 'locator' in the Ontology for Media Resources.
    mainOriginalTitle: URIRef       # Corresponds to 'title.title' in the Ontology for Media Resources with a 'title.type' meaning "original".
    numberOfTracks: URIRef          # Corresponds to 'numTracks.number' in the Ontology for Media Resources. Subproperties can be used to distinguish different values of 'numTracks.type'.
    ratingScaleMax: URIRef          # Corresponds to 'rating.max' in the Ontology for Media Resources.
    ratingScaleMin: URIRef          # Corresponds to 'rating.min' in the Ontology for Media Resources.
    ratingValue: URIRef             # Corresponds to 'rating.value' in the Ontology for Media Resources.
    recordDate: URIRef              # Corresponds to 'date.date' in the Ontology for Media Resources with a 'date.type' meaning "recordDate".
    releaseDate: URIRef             # Corresponds to 'date.date' in the Ontology for Media Resources with a 'date.type' meaning "releaseDate".
    samplingRate: URIRef            # Corresponds to 'samplingRate' in the Ontology for Media Resources, in samples per second.
    title: URIRef                   # Corresponds to 'title.title' in the Ontology for Media Resources. Subproperties can be used to distinguish different values of 'title.type'.
    trackName: URIRef               # Corresponds to 'fragment.name' in the Ontology for Media Resources, for Track fragments.

    # http://www.w3.org/2002/07/owl#ObjectProperty
    createdIn: URIRef               # A subproperty of 'hasRelatedLocation" used to specify where material shooting took place.
    depictsFictionalLocation: URIRef  # A subproperty of 'hasRelatedLocation' used to specify where the action depicted in the media is supposed to take place, as opposed to the location where shooting actually took place (see 'createdIn').
    features: URIRef                # Corresponds to 'contributor.contributor' in the Ontology for Media Resources with a 'contributor.role' meaning "actor".
    hasAccessConditions: URIRef     # Corresponds to 'policy' in the Ontology for Media Resources with a 'policy.type' "access conditions".
    hasAudioDescription: URIRef     # Corresponds to 'fragment' in the Ontology for Media Resources with a 'fragment.role' meaning "audio-description".
    hasCaptioning: URIRef           # Corresponds to 'fragment' in the Ontology for Media Resources with a 'fragment.role' meaning "captioning". This property can for example point to a spatial fragment, a VideoTrack or a DataTrack. The language of the captioning track can be expressed by attaching a 'hasLanguage' property to the specific track.
    hasChapter: URIRef              # Corresponds to 'fragment' in the Ontology for Media Resources with a 'fragment.role' meaning "chapter".
    hasClassification: URIRef       # Corresponds to 'targetAudience.classification' in the Ontology for Media Resources. This property is used to provide a value characterising the target audience.
    hasClassificationSystem: URIRef  # Corresponds to 'targetAudience.identifier' in the Ontology for Media Resources. This is used to identify the reference sheme against which the target audience has been characterised.
    hasCompression: URIRef          # Corresponds to 'compression' in the Ontology for Media Resources.
    hasContributedTo: URIRef        # 
    hasContributor: URIRef          # Corresponds to 'contributor.contributor' in the Ontology for Media Resources. Subproperties can be used to distinguish different values of 'contributor.role'.
    hasCopyrightOver: URIRef        # 
    hasCreated: URIRef              # 
    hasCreator: URIRef              # Corresponds to 'creator.creator' in the Ontology for Media Resources. Subproperties can be used to distinguish different values of 'creator.role'. Note that this property is semantically a subproperty of 'hasContributor'.
    hasFormat: URIRef               # Corresponds to 'format' in the Ontology for Media Resources.
    hasFragment: URIRef             # Corresponds to 'fragment' in the Ontology for Media Resources. Subproperties can be used to distinguish different values of 'fragment.role'.
    hasGenre: URIRef                # Corresponds to 'genre' in the Ontology for Media Resources.
    hasKeyword: URIRef              # Corresponds to 'keyword' in the Ontology for Media Resources.
    hasLanguage: URIRef             # Corresponds to 'language' in the Ontology for Media Resources. The language used in the resource. A controlled vocabulary such as defined in BCP 47 SHOULD be used. This property can also be used to identify the presence of sign language (RFC 5646). By inheritance, the hasLanguage property applies indifferently at the media resource / fragment / track levels.  Best practice recommends to use to best possible level of granularity fo describe the usage of language within a media resource including at fragment and track levels.
    hasLocationCoordinateSystem: URIRef  # Corresponds to 'location.coordinateSystem' in the Ontology for Media Resources.
    hasMember: URIRef               # 
    hasNamedFragment: URIRef        # Corresponds to 'namedFragment' in the Ontology for Media Resources.
    hasPermissions: URIRef          # Corresponds to 'policy' in the Ontology for Media Resources with a  'policy.type' meaning "permissions".
    hasPolicy: URIRef               # Corresponds to 'policy' in the Ontology for Media Resources. Subproperties can be used to distinguish different values of 'policy.type'.
    hasPublished: URIRef            # 
    hasPublisher: URIRef            # Corresponds to 'publisher' in the Ontology for Media Resources.
    hasRating: URIRef               # Corresponds to 'rating' in the Ontology for Media Resources.
    hasRatingSystem: URIRef         # Corresponds to 'rating.type' in the Ontology for Media Resources.
    hasRelatedImage: URIRef         # Corresponds to 'relation' and in the Ontology for Media Resources with a 'relation.type' meaning "related image".
    hasRelatedLocation: URIRef      # Corresponds to 'location' in the Ontology for Media Resources. Subproperties are provided to specify, when possible, the relation between the media resource and the location.
    hasRelatedResource: URIRef      # Corresponds to 'relation' and in the Ontology for Media Resources. Subproperties can be used to distinguish different values of 'relation.type'.
    hasSigning: URIRef              # Corresponds to 'fragment' in the Ontology for Media Resources with a 'fragment.role' meaning "signing". This property can for example point to a spatial fragment or a VideoTrack. The sign language of the captioning track can be expressed by attaching a 'hasLanguage' property to the specific track.
    hasSource: URIRef               # Corresponds to 'relation' and in the Ontology for Media Resources with a 'relation.type' meaning "source".
    hasSubtitling: URIRef           # Corresponds to 'fragment' in the Ontology for Media Resources with a 'fragment.role' meaning "subtitling".
    hasTargetAudience: URIRef       # Corresponds to 'targetAudience' in the Ontology for Media Resources.
    hasTrack: URIRef                # Corresponds to 'fragment' in the Ontology for Media Resources with a 'fragment.role' meaning "track".
    isCaptioningOf: URIRef          # 
    isChapterOf: URIRef             # 
    isCopyrightedBy: URIRef         # Corresponds to 'copyright.identifier' in the Ontology for Media Resources.
    isCreationLocationOf: URIRef    # 
    isFictionalLocationDepictedIn: URIRef  # 
    isFragmentOf: URIRef            # 
    isImageRelatedTo: URIRef        # 
    isLocationRelatedTo: URIRef     # 
    isMemberOf: URIRef              # Corresponds to 'collection' in the Ontology for Media Resources.
    isNamedFragmentOf: URIRef       # 
    isProvidedBy: URIRef            # Corresponds to 'rating.identifier' in the Ontology for Media Resources.
    isRatingOf: URIRef              # 
    isRelatedTo: URIRef             # 
    isSigningOf: URIRef             # 
    isSourceOf: URIRef              # 
    isTargetAudienceOf: URIRef      # 
    isTrackOf: URIRef               # 
    playsIn: URIRef                 # 
    provides: URIRef                # 

    _NS = Namespace("http://www.w3.org/ns/ma-ont#")
