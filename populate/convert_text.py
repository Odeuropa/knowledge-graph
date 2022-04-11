from math import isnan
from os import path
import re

import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

from entities import *
from entities.ontologies import CRM
from entities.vocabularies import vocabulary_manager as VocabularyManager
from entities.utils.smell_words import get_all_smell_words
from entities.utils.pronouns import Pronouns

# xlsx_file = path.join('./', 'input', 'benchmark-annotation-output.xlsx')
docs_file = path.join('./', 'input', 'benchmark.xlsx')

DOC_ID_REGEX = "\d{3}[A-Z]"

lang_map = {
    'English': 'en',
    'French': 'fr',
    'German': 'de',
    'Slovenian': 'sl',
    'Dutch': 'nl',
    'Italian': 'it'
}
docs = {}


def get_safe(name, obj):
    r = obj[name]
    if type(r) == float and isnan(r):
        return ''
    return r


WORKAROUND_DOC_ID = {
    "108 Antilles.txt": "108F",
    "107 Moreau 1639.txt": "107F"
}

not_found = []


def extract_id(lang, title):
    if title in WORKAROUND_DOC_ID:
        id = WORKAROUND_DOC_ID[title]
        return id, docs[id]
    x = re.search(DOC_ID_REGEX, title)
    if x is not None:
        x = x.group(0)
    else:
        ctitle = re.sub(r"_potentially_smelly_passages_\d+\.txt", "", title)
        ctitle = re.sub(r"\.txt.+", "", ctitle)
        ctitle = re.sub(r"^_", "", ctitle)
        ctitle = ctitle.replace(' ', '-')

        x = [k for k in docs.keys() if k in ctitle or ctitle in k]
        if len(x) > 0:
            # print(title , x)
            x = x[0]
        else:
            not_found.append(lang + ' | ' + title)
            return title, None
    return x, docs[x]


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


def process_benchmark_sheet(language):
    df = pd.read_excel(docs_file, sheet_name=language, dtype=str)
    df.fillna('', inplace=True)

    lang = lang_map[language]

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        id = r.get('File Name', r['Document Identifier'])
        if id == '':
            continue
        id = id.replace(' ', '-')

        year = r['Year of Publication'].replace('.0', '')
        if "(" in year:
            # the content in parentheses is normally the date in which has been written
            cont = re.search(r'\((.*?)\)', year)
            year = cont.group(1) if not cont.group(1).startswith('from') else year.replace(cont.group(0), '')

        to = TextualObject(id, r['Title'], r['Author'], year,
                           r['Place of Publication'], lang, r['Genre'])
        docs[id] = to


# init
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
VocabularyManager.setup(config['vocabularies'])

# convert

for x in ['English', 'Italian', 'Dutch', 'French', 'German', 'Slovenian', 'Dutch']:
    process_benchmark_sheet(x)
Graph.g.serialize(destination=f"../dump/main/docs.ttl")
Graph.reset()

for x in ['en', 'fr', 'it', 'de', 'sl', 'nl']:
    with open(f"./input/{x}-frame-elements.tsv") as file:
        tsv_data = pd.read_csv(file, sep='\t')
        process_annotation_sheet(tsv_data, lang=x)
        Graph.g.serialize(destination=f"../dump/main/{x}.ttl")
        Graph.reset()

print(np.unique(not_found))
