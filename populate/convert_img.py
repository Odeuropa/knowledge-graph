import json
import os
import re
from math import isnan
from os import path
from urllib.parse import urlparse

import pandas as pd
import yaml
from tqdm import tqdm

from convert_text import lang_map
from entities import *
from entities.vocabularies import VocabularyManager as VocManager

docs_file = path.join('./', 'input', 'image-odor-dataset', 'metadata.csv')
out_folder = '../dump/image-annotation'
os.makedirs(out_folder, exist_ok=True)

DOC_ID_REGEX = r"\d{3}[A-Z]"

docs = {}


# COMPOSED_LOCATION_REGEX = r'([^(\n]+), ([^0-9\n(]+) \(([^0-9\n()]+)\)'


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

        langs = [lang_map.get(l, 'en') for l in r['Language'].split(',')]
        if len(langs) == 0:
            tld = str(urlparse(r['Photo Archive']).hostname).split('.')[-1]
            if tld in lang_map.values():
                langs = [tld, tld]
            elif tld in ['gov', 'edu']:
                langs = ['en', 'en']
            else:
                langs = [None, None]
        elif len(langs) == 1:
            langs.append(langs[0])
        lang = langs[0]

        date = r['Earliest Date'].strip().replace('.0', '').ljust(4, 'X')
        if 'Latest Date' in r and len(r['Latest Date']) > 0:
            date += '/' + r['Latest Date'].strip().replace('.0', '').ljust(4, 'X')
        if date == 'XXXX':
            date = None

        author = r['Artist']
        author = None if author == "Autore non indicato" else author
        if author is not None:
            author = re.sub(r'\[ [A-Z]+ ]', '', author)
            author = re.sub(r'\|', '', author)
            author = re.sub(r'(,? )?\(?\?\)?', '', author).strip()

        to = ImageObject(idf, r['Title'].strip(), author, date, r['Original Location'], r['Image Credits'], lang)

        # parse locations
        loc = r['Current Location']
        splitting = r'(; | - )'
        if re.match("^(.{1,15}) ;", loc):
            splitting = r'\$'  # no split
        for m in re.split(splitting, loc):
            m = re.sub(r'\(city\)', "", m)
            m = re.sub(r'Inventar-Nr\..+', "", m)
            m = re.sub(r'inv\./cat\.nr.+', "", m)
            m = re.sub(r'\d{4}-\d{2}(-\d{2})?', "", m)
            m = re.sub(r'((\d{2}-)?\d{2}-)?\d{4}', "", m)
            m = re.sub(r'donated to (the )?', "", m)
            m = re.sub(r'[-.,;]$', "", m.strip()).strip()
            if len(m) > 1 and not m.startswith('seen'):
                to.add_location(m, lang)

        to.add_identifier(r['Repository Number'])
        to.add_url(r['Details URL'])
        to.add_descr(r['Additional Information'], lang)
        to.add_descr(r['Description'], lang)
        to.add_license(r['License'])

        genre = r['Genre']
        if genre != 'unknown':
            for g in genre.split(','):
                g = g.strip()
                match, role = art.interlink(g, None, fallback=None)
                if match is None:
                    to.add_subject(g)
                else:
                    to.add_type(match)

        material = r['Material']
        if material:
            material = material.replace(' su ', ', ').lower()
            material = material.replace(' auf ', ', ')
            material = material.replace('(bis)', '')
            material = re.sub(r'\((.+)\)', '', material)
            material = re.sub(r': .+', '', material)
            for m in material.split(r','):
                m = m.strip()
                if len(m) == 0:
                    continue
                to.add_material(m)

        for x in r['Keywords'].split(','):
            to.add_subject(x, 'en')

        to.add_subject(r['Iconography'])
        docs[idf] = to


# init
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
VocManager.setup(config['vocabularies'])
objects = VocManager.get('olfactory-objects')
gestures = VocManager.get('olfactory-gestures')
art = VocManager.get('visual-art-types')

# convert
process_metadata(pd.read_csv(docs_file, dtype=str))

Graph.g.serialize(destination=f"{out_folder}/figs.ttl")
Graph.reset()

image_map = {}
smell_map = {}
cat_map = {}

BASE_OO = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/'

prov = Provenance('D2.4', 'Manual image annotation',
                  'Manual annotation of image resources realised according to the Odeuropa deliverable D2.4 '
                  '"Annotated image data version 2" ')


def guess_annotation(body, seed):
    uri = body.get('uri')
    role = body.get('type')

    if uri is None:
        # no choice, generic
        annotation = Thing(seed, body['name'])
    elif role == 'gesture':
        annotation = Gesture(seed, body['name'], lemma=uri)
    else:
        lemma = objects.get(uri).lemmata[0]

        annotation = SmellSource(seed, body['name'], lang='en', lemma=lemma.id, role=lemma.collection)
    return annotation


not_found = []
with open('input/image-odor-dataset/annotations.json') as f:
    res = json.load(f)

    for x in res['images']:
        if x['file_name'] not in docs:
            not_found.append(x['file_name'])
            continue
        img = docs[x['file_name']]
        image_map[x['id']] = img

        # init basic smell entities
        # policy: 1 image = 1 smell
        codename = 'image annotation'
        curid = codename + str(x['id'])
        smell = Smell(curid)
        emission = SmellEmission(curid, smell)
        experience = OlfactoryExperience(curid, smell)
        emission.add_time(img.time, inferred=True)
        experience.add_time(img.time, inferred=True)
        smell_map[curid] = (smell, emission, experience)

    print('Not found', not_found)

    for x in res['categories']:
        name = x['name'].replace('other ', '')
        x['uri'], x['type'] = objects.interlink(name, 'en', fallback=None)
        if x['uri'] is None:
            x['uri'], x['type'] = gestures.interlink(name, 'en', fallback=None)
            x['type'] = 'gesture'
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

        if cur_id not in image_map:
            continue
        cur_img = image_map[cur_id]
        frag = cur_img.add_fragment(x['bbox'])
        ann = cat_map[x['category_id']]
        cat = guess_annotation(ann, 'image-annotation' + cur_img.title + str(x['id']))

        smell, emission, experience = smell_map[curid]
        if isinstance(cat, Gesture):
            experience.add_gesture(cat)
        elif cat.role == 'carrier':
            emission.add_carrier(cat)
        else:
            emission.add_source(cat)

        current.append(cat)
        frag.add_annotation(cat, prov)


out = Graph.g.serialize(format='ttl')
out = out.replace('"<<', '<<').replace('>>"', '>>')
with open(f"{out_folder}/figs_annotated.ttl", 'w') as outfile:
    outfile.write(out)
