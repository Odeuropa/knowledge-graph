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
