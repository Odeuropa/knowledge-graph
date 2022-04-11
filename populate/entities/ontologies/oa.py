from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace
class OA(DefinedNamespace):
    """
    Web Annotation Ontology
    
    The Web Annotation ontology defines the terms of the Web Annotation vocabulary. Any changes to this document
    MUST be from a Working Group in the W3C that has established expertise in the area.
    
    Generated from: https://www.w3.org/ns/oa.ttl
    Date: 2022-04-08 16:06:03.191555

    dcterms:modified "2016-11-12T21:28:11Z"
    rdfs:seeAlso <http://www.w3.org/TR/annotation-vocab/>
    owl:versionInfo "2016-11-12T21:28:11Z"
    prov:wasRevisionOf <http://www.openannotation.org/spec/core/20130208/oa.owl>
    """
    
    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    annotationService: URIRef       # The object of the relationship is the end point of a service that conforms to the annotation-protocol, and it may be associated with any resource.  The expectation of asserting the relationship is that the object is the preferred service for maintaining annotations about the subject resource, according to the publisher of the relationship.    This relationship is intended to be used both within Linked Data descriptions and as the  rel  type of a Link, via HTTP Link Headers rfc5988 for binary resources and in HTML <link> elements.  For more information about these, please see the Annotation Protocol specification annotation-protocol.
    bodyValue: URIRef               # The object of the predicate is a plain text string to be used as the content of the body of the Annotation.  The value MUST be an  xsd:string  and that data type MUST NOT be expressed in the serialization. Note that language MUST NOT be associated with the value either as a language tag, as that is only available for  rdf:langString .
    cachedSource: URIRef            # A object of the relationship is a copy of the Source resource's representation, appropriate for the Annotation.
    canonical: URIRef               # A object of the relationship is the canonical IRI that can always be used to deduplicate the Annotation, regardless of the current IRI used to access the representation.
    end: URIRef                     # The end property is used to convey the 0-based index of the end position of a range of content.
    exact: URIRef                   # The object of the predicate is a copy of the text which is being selected, after normalization.
    hasBody: URIRef                 # The object of the relationship is a resource that is a body of the Annotation.
    hasEndSelector: URIRef          # The relationship between a RangeSelector and the Selector that describes the end position of the range.
    hasPurpose: URIRef              # The purpose served by the resource in the Annotation.
    hasScope: URIRef                # The scope or context in which the resource is used within the Annotation.
    hasSelector: URIRef             # The object of the relationship is a Selector that describes the segment or region of interest within the source resource.  Please note that the domain ( oa:ResourceSelection ) is not used directly in the Web Annotation model.
    hasSource: URIRef               # The resource that the ResourceSelection, or its subclass SpecificResource, is refined from, or more specific than. Please note that the domain ( oa:ResourceSelection ) is not used directly in the Web Annotation model.
    hasStartSelector: URIRef        # The relationship between a RangeSelector and the Selector that describes the start position of the range.
    hasState: URIRef                # The relationship between the ResourceSelection, or its subclass SpecificResource, and a State resource. Please note that the domain ( oa:ResourceSelection ) is not used directly in the Web Annotation model.
    hasTarget: URIRef               # The relationship between an Annotation and its Target.
    motivatedBy: URIRef             # The relationship between an Annotation and a Motivation that describes the reason for the Annotation's creation.
    prefix: URIRef                  # The object of the property is a snippet of content that occurs immediately before the content which is being selected by the Selector.
    processingLanguage: URIRef      # The object of the property is the language that should be used for textual processing algorithms when dealing with the content of the resource, including hyphenation, line breaking, which font to use for rendering and so forth.  The value must follow the recommendations of BCP47.
    refinedBy: URIRef               # The relationship between a Selector and another Selector or a State and a Selector or State that should be applied to the results of the first to refine the processing of the source resource.
    renderedVia: URIRef             # A system that was used by the application that created the Annotation to render the resource.
    sourceDate: URIRef              # The timestamp at which the Source resource should be interpreted as being applicable to the Annotation.
    sourceDateEnd: URIRef           # The end timestamp of the interval over which the Source resource should be interpreted as being applicable to the Annotation.
    sourceDateStart: URIRef         # The start timestamp of the interval over which the Source resource should be interpreted as being applicable to the Annotation.
    start: URIRef                   # The start position in a 0-based index at which a range of content is selected from the data in the source resource.
    styleClass: URIRef              # The name of the class used in the CSS description referenced from the Annotation that should be applied to the Specific Resource.
    styledBy: URIRef                # A reference to a Stylesheet that should be used to apply styles to the Annotation rendering.
    suffix: URIRef                  # The snippet of text that occurs immediately after the text which is being selected.
    textDirection: URIRef           # The direction of the text of the subject resource. There MUST only be one text direction associated with any given resource.
    via: URIRef                     # A object of the relationship is a resource from which the source resource was retrieved by the providing system.

    # http://www.w3.org/2000/01/rdf-schema#Class
    Annotation: URIRef              # The class for Web Annotations.
    Choice: URIRef                  # A subClass of  as:OrderedCollection  that conveys to a consuming application that it should select one of the resources in the  as:items  list to use, rather than all of them.  This is typically used to provide a choice of resources to render to the user, based on further supplied properties.  If the consuming application cannot determine the user's preference, then it should use the first in the list.
    CssSelector: URIRef             # A CssSelector describes a Segment of interest in a representation that conforms to the Document Object Model through the use of the CSS selector specification.
    CssStyle: URIRef                # A resource which describes styles for resources participating in the Annotation using CSS.
    DataPositionSelector: URIRef    # DataPositionSelector describes a range of data by recording the start and end positions of the selection in the stream. Position 0 would be immediately before the first byte, position 1 would be immediately before the second byte, and so on. The start byte is thus included in the list, but the end byte is not.
    Direction: URIRef               # A class to encapsulate the different text directions that a textual resource might take.  It is not used directly in the Annotation Model, only its three instances.
    FragmentSelector: URIRef        # The FragmentSelector class is used to record the segment of a representation using the IRI fragment specification defined by the representation's media type.
    HttpRequestState: URIRef        # The HttpRequestState class is used to record the HTTP request headers that a client SHOULD use to request the correct representation from the resource.
    Motivation: URIRef              # The Motivation class is used to record the user's intent or motivation for the creation of the Annotation, or the inclusion of the body or target, that it is associated with.
    RangeSelector: URIRef           # A Range Selector can be used to identify the beginning and the end of the selection by using other Selectors. The selection consists of everything from the beginning of the starting selector through to the beginning of the ending selector, but not including it.
    ResourceSelection: URIRef       # Instances of the ResourceSelection class identify part (described by an oa:Selector) of another resource (referenced with oa:hasSource), possibly from a particular representation of a resource (described by an oa:State). Please note that ResourceSelection is not used directly in the Web Annotation model, but is provided as a separate class for further application profiles to use, separate from oa:SpecificResource which has many Annotation specific features.
    Selector: URIRef                # A resource which describes the segment of interest in a representation of a Source resource, indicated with oa:hasSelector from the Specific Resource. This class is not used directly in the Annotation model, only its subclasses.
    SpecificResource: URIRef        # Instances of the SpecificResource class identify part of another resource (referenced with oa:hasSource), a particular representation of a resource, a resource with styling hints for renders, or any combination of these, as used within an Annotation.
    State: URIRef                   # A State describes the intended state of a resource as applied to the particular Annotation, and thus provides the information needed to retrieve the correct representation of that resource.
    Style: URIRef                   # A Style describes the intended styling of a resource as applied to the particular Annotation, and thus provides the information to ensure that rendering is consistent across implementations.
    SvgSelector: URIRef             # An SvgSelector defines an area through the use of the Scalable Vector Graphics [SVG] standard. This allows the user to select a non-rectangular area of the content, such as a circle or polygon by describing the region using SVG. The SVG may be either embedded within the Annotation or referenced as an External Resource.
    TextPositionSelector: URIRef    # The TextPositionSelector describes a range of text by recording the start and end positions of the selection in the stream. Position 0 would be immediately before the first character, position 1 would be immediately before the second character, and so on.
    TextQuoteSelector: URIRef       # The TextQuoteSelector describes a range of text by copying it, and including some of the text immediately before (a prefix) and after (a suffix) it to distinguish between multiple copies of the same sequence of characters.
    TextualBody: URIRef             # 
    TimeState: URIRef               # A TimeState records the time at which the resource's state is appropriate for the Annotation, typically the time that the Annotation was created and/or a link to a persistent copy of the current version.
    XPathSelector: URIRef           # An XPathSelector is used to select elements and content within a resource that supports the Document Object Model via a specified XPath value.

    # http://www.w3.org/2000/01/rdf-schema#Resource
    PreferContainedDescriptions: URIRef  # An IRI to signal the client prefers to receive full descriptions of the Annotations from a container, not just their IRIs.
    PreferContainedIRIs: URIRef     # An IRI to signal that the client prefers to receive only the IRIs of the Annotations from a container, not their full descriptions.

    # http://www.w3.org/ns/oa#Direction
    ltrDirection: URIRef            # The direction of text that is read from left to right.
    rtlDirection: URIRef            # The direction of text that is read from right to left.

    # http://www.w3.org/ns/oa#Motivation
    assessing: URIRef               # The motivation for when the user intends to provide an assessment about the Target resource.
    bookmarking: URIRef             # The motivation for when the user intends to create a bookmark to the Target or part thereof.
    classifying: URIRef             # The motivation for when the user intends to that classify the Target as something.
    commenting: URIRef              # The motivation for when the user intends to comment about the Target.
    describing: URIRef              # The motivation for when the user intends to describe the Target, as opposed to a comment about them.
    editing: URIRef                 # The motivation for when the user intends to request a change or edit to the Target resource.
    highlighting: URIRef            # The motivation for when the user intends to highlight the Target resource or segment of it.
    identifying: URIRef             # The motivation for when the user intends to assign an identity to the Target or identify what is being depicted or described in the Target.
    linking: URIRef                 # The motivation for when the user intends to link to a resource related to the Target.
    moderating: URIRef              # The motivation for when the user intends to assign some value or quality to the Target.
    questioning: URIRef             # The motivation for when the user intends to ask a question about the Target.
    replying: URIRef                # The motivation for when the user intends to reply to a previous statement, either an Annotation or another resource.
    tagging: URIRef                 # The motivation for when the user intends to associate a tag with the Target.

    _NS = Namespace("http://www.w3.org/ns/oa#")
