from SPARQLWrapper import SPARQLWrapper, JSON, TSV
import os

from tqdm import tqdm

test_mode = True
def _default_sparql(endpoint):
    sparql = SPARQLWrapper(endpoint)

    def exec_query(q, format=JSON):
        sparql.setReturnFormat(format)
        sparql.setQuery(q)
        res = sparql.query()
        if format == JSON:
            return res.convert()['results']['bindings']
        else:
            return res.convert().decode('utf-8')

    return exec_query


query = '''
PREFIX schema: <https://schema.org/>
PREFIX od: <http://data.odeuropa.eu/ontology/>
PREFIX crm: <http://erlangen-crm.org/current/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX reo: <https://read-it.acc.hum.uu.nl/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX gn: <http://www.geonames.org/ontology#>
PREFIX onto: <http://www.ontotext.com/>

select distinct * 
FROM <http://www.ontotext.com/disable-sameAs>
where { 
    GRAPH ?g {
        ?smell rdfs:label ?smell_word .
    }
    ?emission od:F1_generated ?smell .
    OPTIONAL {
        ?emission od:F3_had_source ?smell_source . 
        ?smell_source rdfs:label|skos:prefLabel ?smell_source_label .
        FILTER(LANG(?smell_source_label) = ?lang)
    }
    OPTIONAL {
        ?emission od:F3_had_carrier ?carrier .
        ?carrier rdfs:label|skos:prefLabel ?carrier_label .
        FILTER(LANG(?carrier_label) = ?lang)

    }
    OPTIONAL {
        ?emission crm:P7_took_place_at ?place .
        ?place gn:name | rdfs:label ?place_label .
        FILTER(LANG(?place_label) = ?lang)
    }
    OPTIONAL {?emission time:hasTime / rdfs:label ?time}
    ?experience od:F2_perceived ?smell .
    OPTIONAL {
        ?experience crm:P14_carried_out_by ?perceiver.
        ?perceiver rdfs:label ?perceiver_label .
    }
    OPTIONAL {
        ?experience od:F6_evoked ?evoked.
        ?evoked rdfs:label|skos:prefLabel ?evoked_label .
        FILTER(LANG(?evoked_label) = ?lang)
    }
    OPTIONAL {[] crm:P141_assigned ?quality ; 
                 crm:P140_assigned_attribute_to ?smell .
        ?quality skos:prefLabel | rdfs:label ?quality_label .
        FILTER(LANG(?quality_label) = ?lang)
    }
    OPTIONAL {?emotion reo:readP27 ?experience ; 
            rdfs:label|skos:prefLabel ?emotion_label 
            FILTER(LANG(?emotion_label) = ?lang)
    }
    
    [] crm:P67_refers_to ?smell ; rdf:value ?sentence.
    ?book rdfs:label [];  crm:P67_refers_to ?smell ; schema:inLanguage ?lang .

    VALUES ?smell {<%s>}
}
'''

sparql = _default_sparql('https://data.odeuropa.eu/repositories/odeuropa')

graphs_query = '''
PREFIX dcmi: <http://purl.org/dc/dcmitype/>
SELECT DISTINCT ?g
FROM <http://www.ontotext.com/disable-sameAs>
WHERE {
	?g a dcmi:Dataset    
}'''

smells_query = '''
PREFIX od: <http://data.odeuropa.eu/ontology/>
SELECT DISTINCT * FROM <%s>
WHERE {
        ?s a od:L11_Smell .
} %s
'''

graphs_list = sparql(graphs_query)

for i, graph in enumerate(graphs_list):
    g = graph['g']['value']
    id = g.split('/')[-1]
    print(f'* Graph {i}/{len(graphs_list)}: {id}')
    if id in ['image-annotation', 'odor', 'nuk', 'europeana', 'rijksmuseum']:
        continue

    if id + '.tsv' in os.listdir('out'):
        continue
    smells_list = sparql(smells_query % (g, 'LIMIT 100' if test_mode else ''))

    with open(os.path.join('out', id + '.tsv'), 'w') as f:
        first = True
        for smell in tqdm(smells_list):
            s = smell['s']['value']

            props = sparql(query % s, format=TSV)
            if not first:
                props = props.split('\n', maxsplit=1)[-1]

            f.write(props)

            first = False
