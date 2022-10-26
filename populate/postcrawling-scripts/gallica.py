import os
import re
import yaml
import pandas as pd

root = '/data/odeuropa/FR/gallica/'

meta = []
for root, dirs, files in os.walk(root, topdown=False):
    for name in files:
        if not name.endswith('yaml'):
            continue
        id = name.replace('yaml', 'txt')
        print(id)
        with open(os.path.join(root, name), 'r') as f:
            data = yaml.load(f, Loader=yaml.CLoader)
        out = {
            'id': id,
            'title': data['Titre'].replace('..\\\n', ' ').replace('\\', ' '),
            'year': data["Date d'\xE9dition"],
            'sameAs': 'https://data.bnf.fr/' + data['Identifiant'],
            'author': re.sub(r'\. Auteur du texte(.+)?', '', data.get('Auteur', '')),
            'license': data['Droits'],
            'editor': data.get('\xC9diteur'),
            'type': data['Type'],
            'archive': data['Conservation num\xE9rique'],
            'link': 'https://gallica.bnf.fr/' + data['Identifiant']
        }
        meta.append(out)

pd.DataFrame(meta).to_csv('metadata.tsv', index=False, sep='\t')
