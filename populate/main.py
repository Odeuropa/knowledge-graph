from math import isnan
from os import path
from tqdm import tqdm
import pandas as pd
from entities import *
from entities.ontologies import CRM, CRMsci, ODEUROPA

xlsx_file = path.join('./', 'input', 'benchmark-annotation-output.xlsx')
docs_file = path.join('./', 'input', 'benchmark.xlsx')

lang_map = {
    'English': 'en',
    'French': 'fr',
    'German': 'de',
    'Slovenian': 'sl',
    'Dutch': 'nl'
}


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

        smell = Smell(id + str(j))
        emission = SmellEmission(id + str(j), smell, get_safe('Smell_Source', r), get_safe('Odour_Carrier', r),
                                 lang=lang)
        experience = OlfactoryExperience(id + str(j), smell, r['Perceiver'], r['Quality'], lang=lang)
        experience.add_gesture(r['Effect'], lang=lang)
        experience.evoked(r['Evoked_Odorant'], lang=lang)

        if type(r['Location']) == str:
            for x in r['Location'].split('|'):
                place = Place.from_text(x)
                experience.add_place(place)

        if type(r['Time']) == str:
            for x in r['Time'].split('|'):
                Time.parse(x)
                # place = Place.from_text(x)
                # experience.add_place(place)

        add(txt, CRM.P67_refers_to, emission)
        add(txt, CRM.P67_refers_to, smell)
        add(txt, CRM.P67_refers_to, experience)


def process_benchmark_sheet(language):
    df = pd.read_excel(docs_file, sheet_name=language, dtype=str)
    df.fillna('', inplace=True)

    lang = lang_map[language]

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        id = r['Document Identifier']
        TextualObject(id, r['Title'], r['Author'], r['Year of Publication'], r['Place of Publication'], lang, r['Genre'])


for x in ['English', 'French', 'German', 'Slovenian', 'Dutch'][0:1]:
    process_benchmark_sheet(x)
Graph.g.serialize(destination=f"../dump/main/docs.ttl")
Graph.reset()

# for x in ['en', 'fr', 'de', 'sl', 'nl'][0:1]:
#     process_annotation_sheet(x)
#     Graph.g.serialize(destination=f"../dump/main/{x}.ttl")
#     Graph.reset()
