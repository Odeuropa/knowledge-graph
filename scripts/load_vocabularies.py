import os
from os import path
import argparse
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


def upload_in(file_path, content_type, graph_name, keep_data=False):
    # clear graph
    headers = {'Authorization': get_auth()}
    params = (('graph', graph_name),)

    if not keep_data:
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


def load_vocabularies(keep_data=False):
    for filename in sorted(os.listdir(VOCAB)):
        name, ext = filename.rsplit('.')
        if ext == 'DS_Store':
            continue
        print('- ' + name)
        if C_TYPE[ext]:
            upload_in(path.join(VOCAB, filename), C_TYPE[ext], path.join(VOCAB_GRAPH, name), keep_data)
        else:
            continue
    print('completed')


parser = argparse.ArgumentParser(description='Load dump in a graph.')
parser.add_argument('-k', '--keep_data', help='Skip the deletion of the graph', action='store_true')
args = parser.parse_args()
load_vocabularies(args.keep_data)
