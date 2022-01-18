import os
from os import path
import requests
import argparse

from db_utils import base, get_auth

BASE_GRAPH = 'http://data.odeuropa.eu'

ROOT = './dump'
INTERNAL_ROOT = '/opt/graphdb/home/graphdb-import'

C_TYPE = {
    'rdf': 'application/rdf+xml',
    'owl': 'application/rdf+xml',
    'ttl': 'text/turtle'
}


def load_dump(name):
    main_graph = path.join(BASE_GRAPH, name)
    folder = path.join(ROOT, name)

    # clear graph
    headers = {'Authorization': get_auth()}
    params = (('graph', main_graph),)

    response = requests.delete(f'{base}/repositories/odeuropa/rdf-graphs/service',
                               headers=headers, params=params)
    if response.status_code != 204:
        print(response.status_code)
        print(response.content)
        return

    # upload new resources
    for filename in os.listdir(folder):
        name, ext = filename.rsplit('.')
        print('- ' + name)
        if C_TYPE[ext]:
            headers['Content-Type'] = C_TYPE[ext]

            with open(path.join(folder, filename), 'r', encoding='utf-8') as f:
                data = f.read()

            response = requests.post(f'{base}/repositories/odeuropa/rdf-graphs/service',
                                     headers=headers, params=params, data=data.encode('utf-8'))
            if response.status_code != 204:
                print(response.status_code)
                print(response.content)

        else:
            continue
    print('completed')


parser = argparse.ArgumentParser(description='Load dump in a graph.')
parser.add_argument('name')
args = parser.parse_args()
load_dump(args.name)
