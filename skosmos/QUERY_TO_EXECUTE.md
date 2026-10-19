PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX cheminf: <http://semanticscience.org/resource/CHEMINF_>

INSERT {
    GRAPH <http://data.odeuropa.eu/vocabulary/expert-taxonomy-chemical> {

        # ConceptScheme
        <http://data.odeuropa.eu/vocabulary/expert-taxonomy-chemical>
            a skos:ConceptScheme ;
            skos:prefLabel "Expert Taxonomy - Chemical"@en ;
            skos:hasTopConcept ?category .

        # Top concepts (categories)
        ?category
            a skos:Concept ;
            skos:prefLabel ?categoryLabel ;
            skos:inScheme
                <http://data.odeuropa.eu/vocabulary/expert-taxonomy-chemical> ;
            skos:topConceptOf
                <http://data.odeuropa.eu/vocabulary/expert-taxonomy-chemical> ;
            skos:narrower ?compound .

        # Compounds
        ?compound
            a skos:Concept ;
            skos:prefLabel ?compoundLabel ;
            skos:inScheme
                <http://data.odeuropa.eu/vocabulary/expert-taxonomy-chemical> ;
            skos:broader ?category .
    }
}
WHERE {
    GRAPH <http://data.odeuropa.eu/vocabulary/expert-taxonomy-chemical> {

        # Category -> Compound
        ?category cheminf:000143 ?compound .

        FILTER(STRSTARTS(
            STR(?category),
            "http://data.odeuropa.eu/vocabulary/expert-taxonomy/"
        ))

        FILTER(STRSTARTS(
            STR(?compound),
            "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"
        ))

        # Retrieve SMILES descriptors
        OPTIONAL {
            ?descriptor
                a cheminf:000032 ;
                cheminf:000143 ?compound ;
                cheminf:CHEMINF_000012 ?smiles .

            FILTER(isLiteral(?smiles))
        }
    }

    # Category label from URI
    BIND(
        STRLANG(
            STRAFTER(
                STR(?category),
                "http://data.odeuropa.eu/vocabulary/expert-taxonomy/"
            ),
            "en"
        )
        AS ?categoryLabel
    )

    # Compound label: SMILES, fallback to CID
    BIND(
        STRLANG(
            COALESCE(
                STR(?smiles),
                STRAFTER(
                    STR(?compound),
                    "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"
                )
            ),
            "en"
        )
        AS ?compoundLabel
    )
}
