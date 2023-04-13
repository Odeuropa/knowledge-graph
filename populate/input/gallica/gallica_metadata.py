import os
import re
import yaml
from tqdm import tqdm
import pandas as pd

root = '/data/odeuropa/FR/gallica'

meta = []
to_process = []
for root, dirs, files in os.walk(root, topdown=False):
    for name in files:
        if not name.endswith('yaml'):
            continue
        id = name.replace('yaml', 'txt')
        # print(id)
        to_process.append((name, id))
        
for name, id in tqdm(to_process):
        with open(os.path.join(root, name), 'r') as f:
            data = yaml.load(f, Loader=yaml.CLoader)
        out = {
            'id': id,
            'title': data['Titre'].replace('..\\\n', ' ').replace('\\', ' '),
            'year': data["Date d'\xE9dition"],
            'sameAs': 'https://data.bnf.fr/' + data['Identifiant'],
            'author': re.sub(r'\. Auteur du texte(.+)?', '', data.get('Auteur', '')),
            'license': data['Droits'],
            'publisher': data.get('\xC9diteur'),
            'type': data['Type'],
            'archive': data['Conservation num\xE9rique'],
            'link': 'https://gallica.bnf.fr/' + data['Identifiant']
        }
        meta.append(out)

pd.DataFrame(meta).to_csv('metadata.tsv', index=False, sep='\t')

