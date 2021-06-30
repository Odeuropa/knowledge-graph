import requests
from db_utils import base, get_auth


def create_repo(config):
    headers = {'Authorization': get_auth()}

    files = {
        'config': (config, open(config, 'rb'))
    }

    response = requests.post(f'{base}/rest/repositories', headers=headers, files=files)

    if response.status_code == 200:
        print('success')
    else:
        print(response.status_code)
        print(response.content)


create_repo('graphdb/repo-config.ttl')
