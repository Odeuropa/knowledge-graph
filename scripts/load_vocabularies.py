import os
from os import path

import requests

from db_utils import base, get_auth

BASE_GRAPH = 'http://data.odeuropa.eu'
VOCAB_GRAPH = path.join(BASE_GRAPH, 'vocabulary')

ROOT = './dump'
VOCAB = path.join(ROOT, 'vocabularies')
INTERNAL_ROOT = '/opt/graphdb/home/graphdb-import'


C_TYPE = {
    'rdf': 'application/rdf+xml',
    'ttl': 'text/turtle'
}


def upload_in(file_path, content_type, graph_name):
    # clear graph
    headers = {'Authorization': get_auth()}
    params = (('graph', graph_name),)

    response = requests.delete(f'{base}/repositories/odeuropa/rdf-graphs/service',
                               headers=headers, params=params)
    if response.status_code != 204:
        print(response.status_code)
        print(response.content)
        return

    # upload new resource
    headers['Content-Type'] = content_type

    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()

    response = requests.post(f'{base}/repositories/odeuropa/rdf-graphs/service',
                             headers=headers, params=params, data=data.encode('utf-8'))
    if response.status_code != 204:
        print(response.status_code)
        print(response.content)


for filename in os.listdir(VOCAB):
    name, ext = filename.rsplit('.')
    print('- ' + name)
    if C_TYPE[ext]:
        upload_in(path.join(VOCAB, filename), C_TYPE[ext], path.join(VOCAB_GRAPH, name))
    else:
        continue
print('completed')
