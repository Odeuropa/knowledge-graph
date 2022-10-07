import time
import yaml
import requests

API_ENDPOINT = "https://www.wikidata.org/w/api.php"
SPARQL_ENDPOINT = 'https://query.wikidata.org/sparql'

WIKIDATA_CACHE = 'wikidata.yml'
with open(WIKIDATA_CACHE, 'r') as _f:
    cache = yaml.load(_f, Loader=yaml.CLoader)
    if cache is None:
        cache = {}


def add_to_cache(text, uri):
    cache[text] = uri

    with open(WIKIDATA_CACHE, 'w') as f:
        f.write(yaml.dump(cache, Dumper=yaml.CDumper))


def wbsearchentities(query, lang='en'):
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': lang,
        'search': query
    }
    r = requests.get(API_ENDPOINT, params=params)
    res = r.json()['search']
    if res and len(res) > 0:
        return res[0]['concepturi']


def searchperson(name, lang='en', alive_in=None, birth=None, death=None):
    if name in cache:
        return cache[name]
    #return None
    time.sleep(5)
    if birth or death:
        alive_condition = f'FILTER(year(?dateOfBirth) = {birth})' if birth is not None else '' \
                          f'FILTER(year(?dateOfDeath) = {death})' if death is not None else '' \
                          f'BIND(1 AS ?alive)' if alive_in is not None else ''
    else:
        alive_condition = f'BIND((year(?dateOfBirth) < {alive_in}) && (year(?dateOfDeath) >= {alive_in} ) AS ?alive)' if alive_in is not None else ''

    query = '''
    SELECT DISTINCT ?item ?itemLabel ?alive
    WHERE {
      SERVICE wikibase:mwapi {
        bd:serviceParam wikibase:api "EntitySearch";
                        wikibase:endpoint "www.wikidata.org";
                        mwapi:search "%s"; 
                        mwapi:language "%s".
        ?item wikibase:apiOutputItem mwapi:item .
        ?num wikibase:apiOrdinal true # for sorting by relevance
      }
      ?item (wdt:P279|wdt:P31) wd:Q5
      OPTIONAL {?item wdt:P569 ?dateOfBirth . }
      OPTIONAL {?item wdt:P570 ?dateOfDeath . }
      %s

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
     } ORDER BY ASC(?num)
    ''' % (name.replace('"', ''), lang, alive_condition)

    params = {'format': 'json', 'query': query}
    r = requests.get(SPARQL_ENDPOINT, params=params)
    if r.status_code != 200:
        print(query, r.status_code, r.text)
    res = r.json()['results']['bindings']

    if res and len(res) > 0:
        if alive_condition:
            ok = [x for x in res if 'alive' in x and x['alive']]
            if len(ok) == 0:
                ok = [x for x in res if 'alive' not in x]

            if len(ok) > 0:
                res = ok
            else:
                res = []
        if len(res) > 0:
            uri = res[0]['item']['value']
    else:
        uri = None
    add_to_cache(name, uri)
    return uri

# P569
# P570
