import json
from math import isnan
from os import path

import pandas as pd
import yaml
from tqdm import tqdm

from entities import *
from entities.ontologies import CRM
from entities.utils.pronouns import Pronouns
from entities.utils.smell_words import get_all_smell_words
from entities.vocabularies import vocabulary_manager as VocManager

# xlsx_file = path.join('./', 'input', 'benchmark-annotation-output.xlsx')
docs_file = path.join('./', 'input', 'benchmark.xlsx')

DOC_ID_REGEX = "\d{3}[A-Z]"

docs = {}


def get_safe(name, obj):
    r = obj[name]
    if type(r) == float and isnan(r):
        return ''
    return r


def process_annotation_sheet(df, lang):
    print('processing ' + lang)
    df.fillna('', inplace=True)

    doc_map = {}

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        title = r['Title']
        if title == 'annotator1.xmi':
            continue

        id, doc = extract_id(lang, title)
        if not id in doc_map:
            doc_map[id] = 0

        j = doc_map[id]
        doc_map[id] += 1

        txt = doc or TextualObject(id, title)
        prov = Provenance(r['Annotator'])

        smell = Smell(id + str(j))
        emission = SmellEmission(id + str(j), smell, get_safe('Smell_Source', r), get_safe('Odour_Carrier', r),
                                 lang=lang)
        perceiver = set([p for p in r['Perceiver'].split(' | ') if p not in get_all_smell_words(lang)])
        experience = OlfactoryExperience(id + str(j), smell, quality=r['Quality'], lang=lang)
        for p in perceiver:
            if p.lower() in Pronouns.myself(lang) and id in docs:  # fixme
                doc = docs[id]
                if doc.genre not in ['LIT', 'THE']:
                    experience.add_perceiver(doc.author)
                    continue
            experience.add_perceiver(p)
        for x in r['Effect'].split('|'):
            experience.add_gesture(x, lang=lang)
        experience.evoked(r['Evoked_Odorant'], lang=lang)

        if type(r['Location']) == str:
            for x in r['Location'].split('|'):
                place = Place.from_text(x, lang)
                experience.add_place(place)
                emission.add_place(place)

        if type(r['Time']) == str:
            for x in r['Time'].split('|'):
                tim = Time.parse(x, lang, fallback='text')
                experience.add_time(tim)
                emission.add_time(tim)

        set_prov(add(txt, CRM.P67_refers_to, emission), prov)
        add(txt, CRM.P67_refers_to, smell)
        add(txt, CRM.P67_refers_to, experience)


def process_metadata(df):
    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        id = r['File Name']
        if id == '':
            continue
        date = r['Earliest Date'].replace('.0', '').ljust(4, 'X')
        if 'Latest Date' in r and len(r['Latest Date']) > 0:
            date += '/' + r['Latest Date'].replace('.0', '').ljust(4, 'X')

        to = ImageObject(id, r['Title'], r['Artist'], date,
                         r['Original Location'], r['Current Location'], r['Genre'], r['Image URL'])
        docs[id] = to


# init
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
VocManager.setup(config['vocabularies'])
voc = VocManager.get('olfactory-objects')

# convert
df = pd.read_csv('input/image-odor-dataset/metadata.csv', dtype=str)
df.fillna('', inplace=True)
process_metadata(df)
Graph.g.serialize(destination=f"../dump/main/figs.ttl")
Graph.reset()


image_map = {}
cat_map = {}

BASE_OO = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/'


def guess_annotation(body, seed):
    uri, role = body.get('uri')
    if uri is None:
        # no choice, generic
        ann = Thing(seed, body['name'])
    else:
        x = voc.get(uri).lemmata[0]
        ann = SmellSource(seed, body['name'], lang='en', lemma=x.id, role=x.collection)
    return ann


with open('input/image-odor-dataset/annotations.json') as f:
    res = json.load(f)

    for x in res['images']:
        image_map[x['id']] = docs[x['file_name']]

    for x in res['categories']:
        name = x['name'].replace('other ', '')
        x['uri'] = voc.interlink(name, 'en', fallback=None)
        # if x['uri'] is None:
        #     print(x['name'])
        cat_map[x['id']] = x

    annotations = res['annotations']
    sorted(annotations, key=lambda k: k['image_id'])

    cur_id = -1
    current = []
    for x in annotations: # [0:100]:
        if x['image_id'] != cur_id:
            if cur_id != -1:
                # print(current)
                current = []
            cur_id = x['image_id']

        cur_img = image_map[cur_id]
        frag = cur_img.add_fragment(x['bbox'])
        ann = cat_map[x['category_id']]
        cat = guess_annotation(ann, cur_img.title + str(x['id']))
        current.append(cat)
        frag.add_annotation(cat)

Graph.g.serialize(destination=f"../dump/main/figs_annotated.ttl")
