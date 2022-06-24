import os
from os import path
from math import isnan
import re

import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

from entities import *
from entities.ontologies import CRM
from entities.vocabularies import VocabularyManager as VocabularyManager
from entities.utils.smell_words import get_all_smell_words
from entities.utils.pronouns import Pronouns

# xlsx_file = path.join('./', 'input', 'benchmark-annotation-output.xlsx')
docs_file = path.join('./', 'input', 'benchmark.xlsx')
out_folder = '../dump/text-annotation'
os.makedirs(out_folder, exist_ok=True)

DOC_ID_REGEX = r"\d{3}[A-Z]"
PROV_DESCR = 'Manual annotation of textual resources realised according to the Odeuropa deliverable D3.2 ' \
             '"Multilingual historical corpora and annotated benchmarks" '

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
    "107 Moreau 1639.txt": "107F",
    "Wander_Deutsches-Sprichwörter-Lexikon_1867.txt": "076G",
}

not_found = []


def extract_id(lang, title):
    if title in WORKAROUND_DOC_ID:
        _id = WORKAROUND_DOC_ID[title]
        return _id, docs[_id]
    x = re.search(DOC_ID_REGEX, title)
    if x is not None:
        x = x.group(0)
    else:
        ctitle = re.sub(r"_potentially_smelly_passages_\d+\.txt", "", title)
        ctitle = re.sub(r"\.txt.+", "", ctitle)
        ctitle = re.sub(r"^_", "", ctitle)
        ctitle = re.sub(r"^LITERATURE_", "0", ctitle)
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
        if 'annotator1.xmi' in title:
            continue

        identifier, doc = extract_id(lang, title)
        if identifier not in doc_map:
            doc_map[identifier] = 0

        j = doc_map[identifier]
        doc_map[identifier] += 1

        txt = doc or TextualObject(identifier, title)
        txt.add_fragment(r['Sentence'], lang)

        prov = Provenance('text_annotation' + r['Annotator'], 'Manual text annotation', PROV_DESCR, r['Annotator'])

        curid = 'text_annotation' + identifier + str(j)
        smell = Smell(curid)
        emission = SmellEmission(curid, smell, get_safe('Smell_Source', r), get_safe('Odour_Carrier', r), lang=lang)
        perceiver = set([p for p in r['Perceiver'].split(' | ') if p not in get_all_smell_words(lang)])
        experience = OlfactoryExperience(curid, smell, quality=r['Quality'], lang=lang)
        for p in perceiver:
            if p.lower() in Pronouns.myself(lang) and identifier in docs:  # fixme
                doc = docs[identifier]
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
        identifier = r.get('File Name', r['Document Identifier'])
        if identifier == '':
            continue
        identifier = identifier.replace(' ', '-')

        year = r['Year of Publication'].replace('.0', '')
        if "(" in year:
            # the content in parentheses is normally the date in which has been written
            cont = re.search(r'\((.*?)\)', year)
            year = cont.group(1) if not cont.group(1).startswith('from') else year.replace(cont.group(0), '')

        to = TextualObject(identifier, r['Title'], r['Author'], year,
                           r['Place of Publication'], lang, r['Genre'])
        to.add_url(r['Link to source'])
        docs[identifier] = to


# init
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
VocabularyManager.setup(config['vocabularies'])

# convert

for lg in ['English', 'Italian', 'Dutch', 'French', 'German', 'Slovenian', 'Dutch']:
    process_benchmark_sheet(lg)
Graph.g.serialize(destination=f"{out_folder}/docs.ttl")
Graph.reset()

for lg in ['en', 'fr', 'it', 'de', 'sl', 'nl']:
    with open(f"./input/{lg}-frame-elements.tsv") as file:
        tsv_data = pd.read_csv(file, sep='\t')
        process_annotation_sheet(tsv_data, lang=lg)
        out = Graph.g.serialize(format='ttl')
        out = out.replace('"<<', '<<').replace('>>"', '>>')
        with open(f"{out_folder}/{lg}.ttl", 'w') as outfile:
            outfile.write(out)
        Graph.reset()

print(np.unique(not_found))
