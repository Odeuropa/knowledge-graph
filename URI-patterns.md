URI patterns for EOKG data
==============================

This is the documentation of the URI design pattern used by the European Olfactory Knowledge Graph (EOKG).
The following SPARQL query provides the number of instances of each
type ([results](http://data.odeuropa.eu/sparql?savedQueryName=Count%20classes&owner=admin&execute)):

```sparql
SELECT ?class (COUNT(DISTINCT ?s) as ?count) (SAMPLE(?s) as ?ex)
WHERE {
    GRAPH ?g {
       ?s a ?class
    }
    
    VALUES(?g ) {(<http://data.odeuropa.eu/text-annotation>) (<http://data.odeuropa.eu/image-annotation>)}
}
GROUP BY ?class
ORDER BY DESC(?count)
```

## Main entities

Pattern:

```turtle
http://data.odeuropa.eu/<group>/<uuid>
# e.g. http://data.odeuropa.eu/Smell/055b8a36-1515-502c-8974-5a1e2850f498
```

The `<group>` is taken from this table

| Class                           | Group               |
|---------------------------------|---------------------|
| od:L11_Smell                    | Smell               |
| od:L12_Smell_Emission           | SmellEmission       |
| od:L13_Olfactory_Experience     | OlfactoryExperience |
| crm:E22_Human-Made_Object       | SmellSource         |
| crmsci:S10_Material_Substantial | SmellSource         |
| crm:E39_Actor                   | Actor               |
| crm:E21_Person                  | Actor               |
| crm:E53_Place                   | Place               |
| time:TemporalEntity             | Time                |
| crm:E33_Linguistic_Object       | TextualObject       |
| crm:E36_Visual_Item             | ImageObject         |
| oa:Annotation                   | Annotation          |
| prov:Activity                   | Provenance          |

## Secondary entities

This group includes entities that cover specific information about the main entities. The URI is realized appending a
suffix to the parent main entity.

The used pattern is the following:

``` turtle
<uri of the main entity>/<suffix>/<sub identifier>
# i.e. <http://data.odeuropa.eu/OlfactoryExperience/ffd3be49-13ae-59ce-bc76-366070a17756/assignment/1>
```

The `<suffix>` is taken from this table:

| Class | Group                | Suffix                        |
| --- |----------------------|-------------------------------|
| od:L7_Gesture | OlfactoryExperience  | /gesture/{progressive int}    |
| crm:E13_Attribute_Assignment    | OlfactoryEnxperience | /assignment/{progressive int  |
| ma:MediaFragment | ImageObject          | #xywh={coordinates}           |

## UUID and seed generation

The UUID is computed deterministically starting from a seed string.
A real UUID taken from an example above looks like this: `ffd3be49-13ae-59ce-bc76-366070a17756`.

The seed is usually generated based on:

* class (e.g. 'L11_Smell', ...)
* source (e.g. 'image-annotation', 'text-annotation', ...)
* the id of the current document id (filename ID)
* the id of the current annotation (in the input file or generated as a progressive integer)

There are some exceptions to this rule, in order to allow automatic cross-source alignment:

* For Visual Item, only class and filename are used
* For Linguistic Object, only class and the document id are used.
* For Places and Actors, only the class and label (e.g. 'Rome') are used.
* For Temporal Entity, we use the class and the [EDTF](https://www.loc.gov/standards/datetime/) representation of the
  time (when successfully parsed, otherwise the label).
* For prov:Activity, we use the source and (if available) the annotator id
* For Annotation, we use the URI of the target Media Fragment

Examples:

* For most classes: [class] + [source] + [document_id] + [annotation_internal_id]
* For Place (E53) and Actors (E39): [class]+[label]
* For Visual Item  (E36): [class]+[filename]
* For Linguistic Object  (E33): [class]+[document_id]
* For Temporal Entity: [class] + [edtf]
* For prov:Activity : [source] + [annotator_name]
* For Annotation : [media_fragment_uri]