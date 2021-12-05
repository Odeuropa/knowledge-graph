from os import path
from tqdm import tqdm
import pandas as pd
from entities import *
from entities.ontologies import CRM, CRMsci, ODEUROPA

xlsx_file = path.join('./', 'benchmark-annotation-output.xlsx')


def process_annotation_sheet(lang):
    print('processing ' + lang)
    df = pd.read_excel(xlsx_file, sheet_name=lang)
    df.fillna('')

    title_map = {}

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        title = r['Title']
        if not title in title_map:
            title_map[title] = 0

        j = title_map[title]
        title_map[title] += 1

        txt = TextualObject(title)

        smell = Smell(title)
        emission = SmellEmission(title + str(j), smell, r['Smell_Source'], r['Odour_Carrier'], lang=lang)
        experience = OlfactoryExperience(title + str(j), smell, r['Perceiver'], r['Quality'], lang=lang)
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


for x in ['en', 'fr', 'de', 'sl', 'nl'][0:1]:
    process_annotation_sheet(x)
    Graph.g.serialize(destination=f"../dump/main/{x}.ttl")
    Graph.reset()
