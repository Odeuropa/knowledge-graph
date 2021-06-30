import yaml
import requests

base = 'http://localhost:7200'
token = None


def load_config():
    global base
    global user
    global pwd

    with open('scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    base = config['base_uri']
    user = config['user']
    pwd = config['password']


def get_auth():
    global token
    if token is None:
        token = login(user, pwd)
    return token


def login(user, pwd):
    headers = {'X-GraphDB-Password': pwd}
    response = requests.post(f'{base}/rest/login/{user}', headers=headers)
    return response.headers['Authorization']


load_config()
