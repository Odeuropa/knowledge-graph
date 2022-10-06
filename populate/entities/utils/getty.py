import os.path
import pandas as pd
from urllib import request

terms = pd.read_csv('./entities/utils/getty_materials.csv')
terms.replace(r'(.+) \(.+\)', '\\1', inplace=True, regex=True)
terms['label'] = terms['label'].str.lower()

# csv retrieved using
# SELECT DISTINCT * WHERE {
# 	<http://vocab.getty.edu/aat/300010358> skos:narrower* ?uri .
#     ?uri rdfs:label ?label
# }
# and same with <https://vocab.getty.edu/aat/300026031>

opener = request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0'), ('Host', 'data.odeuropa.eu'), ('Accept', '*/*')]
request.install_opener(opener)


def interlink_material(word):
    matches = terms[terms['label'] == word]
    if len(matches) > 0:
        mat = matches.to_dict(orient='records')[0]
        uri = mat['uri']
        out = f'../dump/getty/att_{uri.split("/")[-1]}.ttl'
        if not os.path.isfile(out):
            # print(word, f'http://vocab.getty.edu/download/n3?uri={uri}.n3')
            request.urlretrieve(f'http://vocab.getty.edu/download/n3?uri={uri}.n3', out)
        return uri
    else:
        # print('not found', word)
        return None
