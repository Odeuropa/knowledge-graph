import argparse
import os
from os import path
from math import isnan
import re

import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm
from rdflib import SDO, RDF, SKOS

from entities import *
from entities.vocabularies import VocabularyManager as VocabularyManager
from entities.utils.smell_words import get_all_smell_words
from entities.utils.pos import Pronouns

DEFAULT_ROOT = path.join('./', 'input', 'text-annotation')
DEFAULT_OUT = path.join('../', 'dump')

NAN_REGEX = r'(^| )nan( |$)'
DOC_ID_REGEX = r"\d{3}[A-Z]"
PROV_DESCR = 'Manual annotation of textual resources realised according to the Odeuropa deliverable D3.2 ' \
             '"Multilingual historical corpora and annotated benchmarks" '

lang_map = {
    'English': 'en',
    'French': 'fr',
    'German': 'de',
    'Deutsch': 'de',
    'Slovenian': 'sl',
    'Dutch': 'nl',
    'Italian': 'it'
}

docs = {}


def get_safe(name, obj):
    if name not in obj:
        return ''
    r = obj[name]
    if type(r) == float and isnan(r):
        return ''
    return r


WORKAROUND_DOC_ID = {
    "108 Antilles.txt": "108F",
    "108 Antilles.tsv": "108F",
    "107 Moreau 1639.txt": "107F",
    "107 Moreau 1639.tsv": "107F",
    "Wander_Deutsches-Sprichwörter-Lexikon_1867.txt": "076G",
    "Wander_Deutsches-Sprichwörter-Lexikon_1867.tsv": "076G",
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
        ctitle = ctitle.replace(' ', '-').strip()

        x = docs.get(ctitle, None)
        if x is None:
            x = [k for k in docs.keys() if k in ctitle or ctitle in k]
        else:
            x = [ctitle]

        if len(x) > 0:
            x = x[0]
        else:
            not_found.append(lang + ' | ' + title)
            return title, None
    return x, docs[x]


sentence_archive = []


def process_annotation_sheet(df, lang, codename):
    print('processing ' + lang)

    doc_map = {}

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        # too many spaces = fake sentence
        if len(re.findall(r"\w", r['Sentence'])) - len(re.findall(r"\W", r['Sentence'])) < 10:
            continue

        if r['Sentence'] in sentence_archive:
            continue
        sentence_archive.append(r['Sentence'])

        title = r.get('Title', r.get('Book', None)).replace('.tsv', '.txt')
        if 'annotator1.xmi' in title:
            continue

        identifier, doc = extract_id(lang, title)
        if identifier not in doc_map:
            doc_map[identifier] = 0

        j = doc_map[identifier]
        doc_map[identifier] += 1

        txt = doc or TextualObject(identifier, title)
        frag = txt.add_fragment(r['Sentence'].replace(' | ', ''), lang)

        if 'Annotator' in r:
            prov = Provenance(codename + r['Annotator'], 'Manual text annotation', PROV_DESCR, r['Annotator'])
        else:
            prov = Provenance(codename, 'Automatic annotation', 'Automatic Annotation for the PastScent workshop', None)
            prov.add_software('PastScent', 'https://github.com/Odeuropa/PastScent')

        curid = codename + identifier + '$' + str(j)
        smell = Smell(curid)
        for x in r['Smell_Word'].split('|'):
            smell.add_label(x, lang)
        emission = SmellEmission(curid, smell, get_safe('Smell_Source', r), get_safe('Odour_Carrier', r), lang=lang)

        perceiver = set([p for p in r.get('Perceiver', '').split(' | ') if p not in get_all_smell_words(lang)])

        experience = OlfactoryExperience(curid, smell)
        for p in perceiver:
            if p.lower() in Pronouns.myself(lang) and identifier in docs:  # fixme
                doc = docs[identifier]
                if doc.genre not in ['LIT', 'THE']:
                    experience.add_perceiver(doc.author)
                    continue
            p = p.replace(Place.IN_PREFIX[lang], '').strip()
            p = p.replace(VocabularyManager.ARTICLE_REGEX[lang], '').strip()
            if len(p) > 0:
                experience.add_perceiver(Actor(p, lang))

        for x in r.get('Quality', '').split('|'):
            experience.add_quality(x.strip(), lang)

        for x in r.get('Effect', '').split('|'):
            experience.add_gesture(x, lang=lang)
        for x in r.get('Evoked_Odorant', '').split('|'):
            experience.evoked(x, lang=lang)

        if type(r.get('Location', None)) == str:
            for x in r['Location'].split('|'):
                place = Place.from_text(x, lang)
                experience.add_place(place)
                emission.add_place(place)

        if type(r.get('Time', None)) == str:
            for x in r['Time'].split('|'):
                tim = Time.parse(x, lang, fallback='text')
                experience.add_time(tim)
                emission.add_time(tim)
        if not experience.time or not experience.time.is_parsed():
            # add creation time as time
            experience.add_time(txt.time)
            emission.add_time(txt.time)

        # emotion
        emotion = r.get('Emotion', None)
        if emotion:
            for e in np.unique(emotion.split(' | ')):
                if r['Emotion_Type'] == 'Smell_Word':
                    return
                typ = r['Emotion_Other'] if r['Emotion_Type'] == 'Other' else r['Emotion_Type']
                experience.add_emotion(e, typ.lower(), r['Emotion_Sentiment'])

        frag.add_annotation(emission, prov)
        frag.add_annotation(smell, prov)
        frag.add_annotation(experience, prov)


def process_benchmark_sheet(language, docs_file):
    if docs_file.endswith('.xlsx'):
        df = pd.read_excel(docs_file, sheet_name=language, dtype=str)
    else:
        df = pd.read_csv(docs_file, sep='\t')
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

        author = r['Author'].replace('\\amp;', '&')

        to = TextualObject(identifier, r['Title'], author, year,
                           r['Place of Publication'], lang, r['Genre'])
        to.add_url(r['Link to source'])
        docs[identifier] = to


def process_metadata(lang, docs_file, map_file):
    df = pd.read_csv(docs_file, dtype=str, sep='\t', encoding='utf-8')
    df.fillna('', inplace=True)
    intermediate_map = None

    if path.isfile(map_file):
        intermediate_map = pd.read_csv(map_file, dtype=str, sep='\t', encoding='utf-8', names=['id', 'filename'])
        intermediate_map['real_id'] = intermediate_map['filename'].apply(lambda x: x.split('text_')[-1])

    splitting = ',' if 'old-bailey-corpus' in docs_file else '|'
    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        identifier = r['id'].replace('.xml', '').replace('.txt', '')
        year = r['year'].replace('.0', '')

        if 'eebo' in docs_file:
            identifier = identifier.replace('/', '_')
            year = re.sub(r'-\??(?!\d)', '.?', year)

        # print(identifier, year)
        to = TextualObject(identifier, title=r['title'], date=year, place='London', lang=lang)
        for author in r['author'].split(splitting):
            author = author.replace('\\amp;', '&')

            m = re.search(r"(, )?\(?(\d{4}\??)-(\d{4}\??)\)?", author)
            birth = death = None
            if m is not None:
                birth = m.group(1)
                death = m.group(1)
                author = author.replace(m.group(0), '')
            if ',' in author:
                parts = re.sub(r'\.$', '', author).split(',')
                author = f'{parts[1]} {parts[0]}'

            to.add_author(author, lang, birth, death)
        to.add_url(r.get('doiLink'))
        to.add_url(r.get('link'))
        to.same_as(r.get('sameAs'))
        to.add_license(r.get('license'))
        to.add(SKOS.editorialNote, r.get('note'))
        to.add(SDO.issn, r.get('issn'))
        if 'royal-society-corpus' in docs_file:
            to.add(RDF.type, SDO.ScholarlyArticle)
        to.add(SDO.about, r.get('primaryTopic'))
        if 'journal' in r:
            to.add(SDO.isPartOf, TextualObject(r['journal'], r['journal'], date=year))

        if intermediate_map is not None:
            real_id = intermediate_map[intermediate_map['real_id'] == identifier + '.txt']['id'].iloc[0]
            docs[real_id] = to
        else:
            docs[identifier] = to


def run(root, output, lang=None):
    docs_file = path.join(root, 'metadata.xlsx')
    codename = root.split('/')[-1]
    folder_name = path.split(root)[-1]
    out_folder = path.join(output, folder_name)
    os.makedirs(out_folder, exist_ok=True)

    # init
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    VocabularyManager.setup(config['vocabularies'])

    # convert
    if lang is None:
        lang_list = ['en', 'fr', 'it', 'de', 'sl', 'nl']
        for lg in ['English', 'Italian', 'Dutch', 'French', 'German', 'Slovenian', 'Dutch']:
            process_benchmark_sheet(lg, docs_file)
    else:
        lang_list = [lang]
        docs_file = path.join(root, 'metadata.tsv')
        map_file = path.join(root, 'map.tsv')

        process_metadata(lang, docs_file, map_file)

    Graph.g.serialize(destination=f"{out_folder}/docs.ttl")
    Graph.reset()

    for lg in lang_list:
        em_tsv = path.join(root, f"{lg}-frame-elements-emotion.tsv")
        tsv_data = None

        if os.path.isfile(em_tsv):
            with open(em_tsv) as file:
                tsv_data = pd.read_csv(file, sep='\t', index_col=False)

        with open(path.join(root, f"{lg}-frame-elements.tsv")) as file:
            temp = pd.read_csv(file, sep='\t', index_col=False)
            tsv_data = temp if tsv_data is None else pd.concat([tsv_data, temp], ignore_index=True)
            tsv_data.fillna('', inplace=True)
            tsv_data.replace(NAN_REGEX, regex=True, inplace=True)
            tsv_data.replace(NAN_REGEX, regex=True, inplace=True)

            # dividing in batches of 10K rows
            step = 10000
            for i in tqdm(np.arange(0, len(tsv_data) - 1, step), desc="Batches: "):
                process_annotation_sheet(tsv_data[i:i + step], lang=lg, codename=codename)
                out = Graph.g.serialize(format='ttl')
                out = out.replace('"<<', '<<').replace('>>"', '>>')
                with open(f"{out_folder}/{lg}{i}.ttl", 'w') as outfile:
                    outfile.write(out)
                Graph.reset()

    print(np.unique(not_found))


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert csv from text into the Odeuropa Model.')
    parser.add_argument('--input', '-i', type=dir_path, default=DEFAULT_ROOT)
    parser.add_argument('--output', '-o', type=dir_path, default=DEFAULT_OUT)
    parser.add_argument('--lang', type=str)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run(args.input, args.output, args.lang)
