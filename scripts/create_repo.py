import os

import requests
from db_utils import base, get_auth, repo


def create_repo(config):
    headers = {'Authorization': get_auth()}

    files = {
        'config': (config, open(config, 'rb'))
    }

    response = requests.post(f'{base}/rest/repositories', headers=headers, files=files)

    if response.status_code == 200:
        print('repository created')
    else:
        print(response.status_code)
        print(response.content)

        # return

    with open('graphdb/connector.rq', 'r') as f:
        connector_query = f.read()

    params = {
        'query': connector_query
    }
    response = requests.get(f'{base}/repositories/{repo}/statements', params=params, headers=headers)

    if response.status_code == 200:
        print('connector to Lucene ready')
    else:
        print(response.status_code)
        print(response.content)

    print('done')


create_repo('graphdb/repo-config.ttl')
