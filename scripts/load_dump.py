import time
import re
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
    'owl': 'text/turtle',
    'ttl': 'text/turtle'
}

LANG_FINAL = r"_(it|en|de|nl|sl|fr)\d*$"


def load_dump(name, keep_data=False):
    start = time.time()
    main_graph = path.join(BASE_GRAPH, name)
    folder = path.join(ROOT, name)
    delete_graph = True

    if re.search(LANG_FINAL, main_graph):
        main_graph = re.sub(LANG_FINAL, '', main_graph)
        delete_graph = False

    # clear graph
    headers = {'Authorization': get_auth()}
    params = (('graph', main_graph),)

    if delete_graph:
        if not keep_data:
            print('Deleting graph...')
            response = requests.delete(f'{base}/repositories/odeuropa/rdf-graphs/service',
                                       headers=headers, params=params)
            if response.status_code != 204:
                print(response.status_code)
                print(response.content)
                return
            end = time.time()
            print('Graph Deleted | Elapsed time:', end - start)
            start = end

    print('Uploading new resources...')
    # upload new resources
    for filename in sorted(os.listdir(folder)):
        if not '.' in filename:
            continue
        name, ext = filename.rsplit('.', 2)
        if ext in C_TYPE:
            print('- ' + name)
            headers['Content-Type'] = C_TYPE[ext]

            with open(path.join(folder, filename), 'r', encoding='utf-8') as f:
                data = f.read()

            response = requests.post(f'{base}/repositories/odeuropa/rdf-graphs/service',
                                     headers=headers, params=params, data=data.encode('utf-8'))
            if response.status_code != 204:
                print(response.status_code)
                print(response.content)
            end = time.time()
            print('   dump loaded | Elapsed time:', end - start)
            start = end
        else:
            continue
    print('completed')


parser = argparse.ArgumentParser(description='Load dump in a graph.')
parser.add_argument('name')
parser.add_argument('-k', '--keep_data', description='Skip the deletion of the graph', action='store_true')
args = parser.parse_args()
load_dump(args.name, args.keep_data)
