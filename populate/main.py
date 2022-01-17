from math import isnan
from os import path

import pandas as pd
import yaml
from tqdm import tqdm

from entities import *
from entities.ontologies import CRM
from entities.vocabularies import vocabulary_manager as VocabularyManager
from entities.utils.smell_words import get_all_smell_words
from entities.utils.pronouns import Pronouns

xlsx_file = path.join('./', 'input', 'benchmark-annotation-output.xlsx')
docs_file = path.join('./', 'input', 'benchmark.xlsx')

lang_map = {
    'English': 'en',
    'French': 'fr',
    'German': 'de',
    'Slovenian': 'sl',
    'Dutch': 'nl'
}
docs = {}


def get_safe(name, obj):
    r = obj[name]
    if type(r) == float and isnan(r):
        return ''
    return r


def process_annotation_sheet(lang):
    print('processing ' + lang)
    df = pd.read_excel(xlsx_file, sheet_name=lang)
    df.fillna('', inplace=True)

    doc_map = {}

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        title = r['Title']
        id = title.split(' ')[0]
        if not id in doc_map:
            doc_map[id] = 0

        j = doc_map[id]
        doc_map[id] += 1

        txt = TextualObject(id, title)
        prov = Provenance(r['Annotator'])

        smell = Smell(id + str(j))
        emission = SmellEmission(id + str(j), smell, get_safe('Smell_Source', r), get_safe('Odour_Carrier', r),
                                 lang=lang)
        perceiver = set([p for p in r['Perceiver'].split(' | ') if p not in get_all_smell_words(lang)])
        experience = OlfactoryExperience(id + str(j), smell, quality=r['Quality'], lang=lang)
        for p in perceiver:
            if p.lower() in Pronouns.myself(lang) and id in docs: #fixme
                doc = docs[id]
                if doc.genre not in ['LIT', 'THE']:
                    experience.add_perceiver(doc.author)
                    continue
            experience.add_perceiver(p)
        experience.add_gesture(r['Effect'], lang=lang)
        experience.evoked(r['Evoked_Odorant'], lang=lang)

        if type(r['Location']) == str:
            for x in r['Location'].split('|'):
                place = Place.from_text(x)
                experience.add_place(place)
                emission.add_place(place)

        if type(r['Time']) == str:
            for x in r['Time'].split('|'):
                experience.add_time(Time.parse(x, lang, fallback='text'))
                emission.add_time(Time.parse(x, lang, fallback='text'))

        set_prov(add(txt, CRM.P67_refers_to, emission), prov)
        add(txt, CRM.P67_refers_to, smell)
        add(txt, CRM.P67_refers_to, experience)


def process_benchmark_sheet(language):
    df = pd.read_excel(docs_file, sheet_name=language, dtype=str)
    df.fillna('', inplace=True)

    lang = lang_map[language]

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        id = r['Document Identifier']
        to = TextualObject(id, r['Title'], r['Author'], r['Year of Publication'],
                           r['Place of Publication'], lang, r['Genre'])
        docs[id] = to


# init
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
VocabularyManager.setup(config['vocabularies'])

# convert

for x in ['English', 'French', 'German', 'Slovenian', 'Dutch']:
    process_benchmark_sheet(x)
Graph.g.serialize(destination=f"../dump/main/docs.ttl")
Graph.reset()

for x in ['en', 'fr', 'it', 'de', 'sl', 'nl']:
    process_annotation_sheet(x)
    Graph.g.serialize(destination=f"../dump/main/{x}.ttl")
    Graph.reset()
