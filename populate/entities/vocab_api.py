from os import path
import requests

API = 'http://data.odeuropa.eu/api/vocabulary/'


def query(domain, q, lang):
    r = requests.get(path.join(API, domain), params={
        'q': q,
        'lang': lang
    })
    return r.json()


def query_one(domain, q, lang):
    return query(domain, q, lang)[0]


def interlink(domain, q, lang, fallback='text'):
    x = query_one(domain, q, lang)
    if x['confidence'] > 0.8:
        return x['id']
    elif fallback == 'text':
        return q
    else:
        return None
