import json
import math
import os
import re
from os import path
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import yaml
from SPARQLTransformer import sparqlTransformer
from tqdm import tqdm

from convert_text import lang_map
from entities import *
from entities.Graph import ODEUROPA_PROJECT
from entities.vocabularies import VocabularyManager as VocManager

source_folder = path.join('./', 'input', 'image-odor-dataset')
docs_file = path.join(source_folder, 'metadata.csv')
out_folder = '../dump/image-annotation'
os.makedirs(out_folder, exist_ok=True)

DOC_ID_REGEX = r"\d{3}[A-Z]"

docs = {}


# COMPOSED_LOCATION_REGEX = r'([^(\n]+), ([^0-9\n(]+) \(([^0-9\n()]+)\)'


def process_metadata(df):
    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        idf = r['File Name']
        if idf == '':
            continue

        url = r['Details URL']

        if r['Language']:
            lang = lang_map.get(r['Language'], 'en')
        else:
            tld = str(urlparse(r['Photo Archive']).hostname).split('.')[-1]
            if tld in lang_map.values():
                lang = tld
            elif tld in ['gov', 'edu']:
                lang = 'en'
            else:
                lang = None

        date = r['Earliest Date'].strip().replace('.0', '')
        end_date = r.get('Latest Date', '').strip().replace('.0', '')

        if len(date) < 3:
            # This is a bad crawling of the metadata:
            if len(end_date) == 4:
                # I use this as date!
                date = end_date
                end_date = ''
            elif len(date) == 2 and ('rkd.nl' in url or 'sammlung.staedelmuseum' in url or 'nga.gov' in url):
                # it is the century
                date = date.ljust(4, 'X')
            # elif len(date) != 0:
            #     print(date, end_date, len(end_date), r['Details URL'])

        date = date.ljust(4, 'X')
        if len(end_date) > 0 and end_date != date:
            date += '/' + end_date.strip().replace('.0', '').ljust(4, 'X')
        if date == 'XXXX':
            date = None

        author = r['Artist']
        if author is not None:
            author = re.sub(r'\[ [A-Z]+ ]', '', author)
            author = re.sub(r'\|', '', author)
            author = re.sub(r'(,? )?\(?\?\)?', '', author).strip()

        loc = r.get('Original Location', "").replace('|', '')
        to = ImageObject(idf, r['Title'].strip(), author, date, loc, r.get('Image Credits'), lang)

        # parse locations
        loc = r.get('Current Location', '')
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
            m = re.sub(r'[-.,;]$', "", m.strip()).replace('|', '').strip()
            if len(m) > 1 and not m.startswith('seen'):
                to.add_location(m, lang)

        to.add_identifier(r.get('Repository Number'))
        if 'beniculturali' in url:
            q = {
                "proto": {
                    "id": "?id",
                    "depiction": "$foaf:depiction$required$var:dep"
                },
                "$where": [
                    "?id a arco:HistoricOrArtisticProperty"
                ],
                "$values": {
                    "?dep": f"http://www.sigecweb.beniculturali.it/images/fullsize/ICCD1004087/ICCD10023739_185047.JPG"
                }
            }
            qres = sparqlTransformer(q, {
                'endpoint': 'https://dati.cultura.gov.it/sparql'
            })
            url = qres[0]['id']
            to.same_as(url)

        to.add_url(url)
        to.add_descr(r['Additional Information'], lang)
        to.add_descr(r['Description'], lang)
        to.add_license(r['License'])

        genre = r['Genre']
        if genre != 'unknown':
            for g in genre.split(','):
                if ">" in g:
                    g = g.split('>')[0]
                g = g.replace('|', '').strip()
                match, role = art.interlink(g, None, fallback=None)
                if match is None:
                    to.add_subject(g)
                else:
                    to.add_type(match)

        material = r['Material']
        if material:
            material = material.replace('|', '').replace(' su ', ', ').lower()
            material = material.replace(' auf ', ', ')
            material = material.replace('(bis)', '')
            material = re.sub(r'\((.+)\)', '', material)
            material = re.sub(r': .+', '', material)
            for m in material.split(r','):
                if ">" in m:
                    m = m.split('>')[0]

                m = m.strip()
                if len(m) == 0:
                    continue
                to.add_material(m)

        for k in r['Keywords'].split(','):
            to.add_subject(k.replace('|', ''), 'en')

        to.add_subject(r['Iconography'])
        docs[idf] = to


# init
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
VocManager.setup(config['vocabularies'])
art = VocManager.get('visual-art-types')

# convert
raw_metadata = pd.read_csv(docs_file, dtype=str)
raw_metadata.fillna('', inplace=True)

batch_dim = 10000
batches = np.arange(0, len(raw_metadata), batch_dim)
for i, batch_start in enumerate(batches):
    print(f'Batch {i + 1}/{len(batches)}')
    batch = raw_metadata.iloc[batch_start:batch_start + batch_dim, :]

    process_metadata(batch)

    Graph.g.serialize(destination=f"{out_folder}/figs_{i}.ttl")
    Graph.reset()

cat_map = {}

BASE_OO = 'http://data.odeuropa.eu/vocabulary/olfactory-objects/'

prov = Provenance('D2.4', 'Manual image annotation',
                  'Manual annotation of image resources realised according to the Odeuropa deliverable D2.4 '
                  '"Annotated image data version 2" ', ODEUROPA_PROJECT)
prov_automatic = Provenance('D2.3', 'Automatic image annotation',
                            'Automatic annotation of image resources realised according to the Odeuropa deliverable D2.3 '
                            '"Object Detection/Image analysis version 1" ', ODEUROPA_PROJECT)
prov_automatic.add_software('Detrex fork for the application on the ODOR dataset',
                            'https://github.com/mathiaszinnen/detrex')


def guess_annotation(body, seed):
    uri = body.get('uri')
    role = body.get('type')

    if uri is None:
        # no choice, generic
        annotation = Thing(seed, body['name'], 'en')
    elif role == 'gesture':
        annotation = Gesture(seed, body['name'], 'en', lemma=uri)
    else:
        annotation = SmellSource(seed, body['name'], lang='en', lemma=uri, role=role)
    return annotation


not_found = []
done = []


def init_base_smell_entities(id, img, smell_map, _prov):
    # policy: 1 image = 1 smell
    print(id)
    if id in smell_map:
        return smell_map[id]

    # init basic smell entities
    codename = 'image annotation'
    curid = codename + str(id)

    smell = Smell(curid)
    emission = SmellEmission(curid, smell)
    experience = OlfactoryExperience(curid, smell)
    emission.add_time(img.time, inferred=True)
    experience.add_time(img.time, inferred=True)
    img.add_annotation(smell, _prov)
    img.add_annotation(emission, _prov)
    img.add_annotation(experience, _prov)

    smell_map[id] = (smell, emission, experience)
    return smell, emission, experience


def process_annotations(annotations, image_map, smell_map, automatic, _prov):
    for x in tqdm(annotations):
        image_id = x.get('image_id', x.get('iid'))
        if image_id not in image_map:
            continue

        cur_img = image_map[image_id]

        # if an image has manual annotations, I ignore the automatic ones
        # if an image miss manual annotations, I take the automatic
        if automatic:
            if cur_img.has_manual_annotations:
                continue
            if x['score'] < 0.3:
                continue  # just to remove some noise
        else:
            cur_img.has_manual_annotations = True

        frag = cur_img.add_fragment(x['bbox'])
        ann = cat_map[x.get('category_id', x.get('cid'))]
        cat = guess_annotation(ann, 'image-annotation' + cur_img.title + str(x['id']))
        smell, emission, experience = init_base_smell_entities(cur_img.internal_id, cur_img, smell_map, _prov)

        if isinstance(cat, Gesture):
            experience.add_gesture(cat)
        elif isinstance(cat, SmellSource) and cat.role == 'carrier':
            emission.add_carrier(cat)
        else:
            emission.add_source(cat)

        frag.add_annotation(cat, _prov, x.get('score', 1))


iterator = 0


def parse_annotations_file(json_file):
    global iterator

    automatic = 'automatic' in json_file
    image_map = {}
    smell_map = {}
    _prov = prov_automatic if automatic else prov

    with open(json_file) as f:
        res = json.load(f)

        for x in res['images']:
            fname = x['file_name'].replace('/media/prathmeshmadhu/myhdd/odeuropa/annotations-nightly/mmodor_imgs/', '')
            if fname not in docs:
                not_found.append(fname)
                continue

            if x['id'] in image_map:
                print('duplicate!', x['id'])
                continue

            img = docs[fname]
            image_map[x['id']] = img

        print('Eventual not found images: ', not_found)

        for x in res['categories']:
            name = x['name'].replace('other ', '')
            x['uri'], x['type'], x['voc'] = VocManager.interlink_multiple(name, 'en',
                                                                          ['olfactory-objects', 'olfactory-gestures'])
            if x['uri'] is None:
                print('Missing in vocabularies:', x['name'], x['supercategory'])
            elif x['voc'] == 'olfactory-gestures':
                x['type'] = 'gesture'
            cat_map[x['id']] = x

        annotations = res['annotations']
        sorted(annotations, key=lambda k: k.get('image_id', k.get('iid')))

        # dividing in batches of 50K annotations
        step = 50000
        for i in np.arange(0, len(annotations) - 1, step):
            print(f'Batch {int(i / step + 1)}/{math.ceil(len(annotations) / step)}')
            process_annotations(annotations[i:i + step], image_map, smell_map, automatic, _prov)
            out = Graph.g.serialize(format='ttl')
            out = out.replace('"<<', '<<').replace('>>"', '>>')
            with open(f"{out_folder}/figs_annotated_{iterator}.ttl", 'w') as outfile:
                outfile.write(out)
                iterator += 1
            Graph.reset()


for i, f in enumerate(['annotations.json', 'annotations_automatic.json']):
    print('Parse ', f)
    parse_annotations_file(path.join(source_folder, f))
