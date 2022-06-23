import json
import os
import re
from math import isnan
from os import path

import pandas as pd
import yaml
from tqdm import tqdm

from entities import *
from entities.vocabularies import VocabularyManager as VocManager

# xlsx_file = path.join('./', 'input', 'benchmark-annotation-output.xlsx')
docs_file = path.join('./', 'input', 'image-odor-dataset', 'metadata.csv')
out_folder = '../dump/image-annotation'
os.makedirs(out_folder, exist_ok=True)

DOC_ID_REGEX = r"\d{3}[A-Z]"

docs = {}


def get_safe(label, obj):
    r = obj[label]
    if type(r) == float and isnan(r):
        return ''
    return r


def process_metadata(df):
    df.fillna('', inplace=True)

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        idf = r['File Name']
        if idf == '':
            continue
        date = r['Earliest Date'].replace('.0', '').ljust(4, 'X')
        if 'Latest Date' in r and len(r['Latest Date']) > 0:
            date += '/' + r['Latest Date'].replace('.0', '').ljust(4, 'X')
        if date == 'XXXX':
            date = None

        author = r['Artist']
        author = None if author == "Autore non indicato" else author
        if author is not None:
            author = re.sub(r'\[ [A-Z]+ ]', '', author)
            author = re.sub(r'\|', '', author)
            author = re.sub(r'(,? )?\(?\?\)?', '', author).strip()
        to = ImageObject(idf, r['Title'].strip(), author, date,
                         r['Original Location'], r['Current Location'], r['Genre'], r['Image URL'])
        docs[idf] = to


# init
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
VocManager.setup(config['vocabularies'])
voc = VocManager.get('olfactory-objects')

# convert
process_metadata(pd.read_csv(docs_file, dtype=str))
Graph.g.serialize(destination=f"{out_folder}/figs.ttl")
Graph.reset()

image_map = {}
cat_map = {}

BASE_OO = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/'

prov = Provenance('D2.2', 'Manual image annotation',
                  'Manual annotation of image resources realised according to the Odeuropa deliverable D2.2 '
                  '"Annotated image data version 1" ')


def guess_annotation(body, seed):
    uri = body.get('uri')
    if uri is None:
        # no choice, generic
        annotation = Thing(seed, body['name'])
    else:
        lemma = voc.get(uri).lemmata[0]

        annotation = SmellSource(seed, body['name'], lang='en', lemma=lemma.id, role=lemma.collection)
    return annotation


with open('input/image-odor-dataset/annotations.json') as f:
    res = json.load(f)

    for x in res['images']:
        image_map[x['id']] = docs[x['file_name']]

    for x in res['categories']:
        name = x['name'].replace('other ', '')
        x['uri'], x['type'] = voc.interlink(name, 'en', fallback=None)
        if x['uri'] is None:
            print('Missing in vocabularies:', x['name'], x['supercategory'])
        cat_map[x['id']] = x

    annotations = res['annotations']
    sorted(annotations, key=lambda k: k['image_id'])

    cur_id = -1
    current = []
    for x in tqdm(annotations):
        if x['image_id'] != cur_id:
            if cur_id != -1:
                # print(current)
                current = []
            cur_id = x['image_id']

        cur_img = image_map[cur_id]
        frag = cur_img.add_fragment(x['bbox'])
        ann = cat_map[x['category_id']]
        cat = guess_annotation(ann, 'image-annotation' + cur_img.title + str(x['id']))
        current.append(cat)
        frag.add_annotation(cat, prov)

out = Graph.g.serialize(format='ttl')
out = out.replace('"<<', '<<').replace('>>"', '>>')
with open(f"{out_folder}/figs_annotated.ttl", 'w') as outfile:
    outfile.write(out)
