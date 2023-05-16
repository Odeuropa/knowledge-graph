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
import rispy

from entities import *
from entities.Graph import ODEUROPA_PROJECT
from entities.vocabularies import VocabularyManager as VocabularyManager
from entities.utils.smell_words import get_all_smell_words
from entities.utils.pos import Pronouns

DEFAULT_ROOT = path.join('./', 'input', 'text-annotation')
DEFAULT_OUT = path.join('../', 'dump')

NAN_REGEX = r'(^| )nan( |$)'
DOC_ID_REGEX = r"\d{3}[A-Z]"
DLIB_BRACKETS_REGEX = r'\(([^\d]+)(. [\d\--]+)?\)'
PROV_DESCR = 'Manual annotation of textual resources realised according to the Odeuropa deliverable D3.2 ' \
             '"Multilingual historical corpora and annotated benchmarks" '

lang_map = {
    'English': 'en',
    'en': 'en',
    'French': 'fr',
    'fr': 'fr',
    'German': 'de',
    'Deutsch': 'de',
    'de': 'de',
    'Slovenian': 'sl',
    'sl': 'sl',
    'Dutch': 'nl',
    'nl': 'nl',
    'Italian': 'it',
    'it': 'it'
}

docs = {}

DEFAULT_PLACES = None


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


def get_multi(keys, obj):
    res = []
    for x in [obj[k].strip() for k in keys if k in obj and obj[k]]:
        res.extend(x.split('|'))
    return res


def process_annotation_sheet(df, lang, codename):
    print('processing ' + lang)

    doc_map = {}

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        sentence = r.get('SentenceBefore', '') + \
                   r.get('Sentence', r.get('Full_Sentence')) + \
                   r.get('SentenceAfter', '')

        # too many spaces = fake sentence
        if len(re.findall(r"\w", sentence)) - len(re.findall(r"\W", sentence)) < 10:
            continue

        if sentence in sentence_archive:
            continue
        sentence_archive.append(sentence)

        title = r.get('Title', r.get('Book', None)).replace('.tsv', '.txt')
        if 'annotator1.xmi' in title:
            continue

        identifier, pack = extract_id(lang, title)
        if pack is None:
            not_found.append(lang + ' | ' + title + f' ({identifier})')
            continue
        doc, frag_uri = pack
        if identifier not in doc_map:
            doc_map[identifier] = 0

        j = doc_map[identifier]
        doc_map[identifier] += 1

        txt = doc or TextualObject(identifier, title)
        frag = txt.add_fragment(sentence.replace(' | ', ''), lang, frag_uri)

        if 'Annotator' in r:
            prov = Provenance(codename + r['Annotator'], 'Manual text annotation', PROV_DESCR, r['Annotator'])
        else:
            prov = Provenance(codename, 'Automatic annotation', 'Automatic Annotation within the Odeuropa project',
                              ODEUROPA_PROJECT)
            prov.add_software('SmellClassifier', 'https://github.com/Odeuropa/wp3-information-extraction-system')

        curid = codename + identifier + '$' + str(j)
        smell = Smell(curid)
        for x in r['Smell_Word'].split('|'):
            smell.add_label(x, lang)
        emission = SmellEmission(curid, smell, get_safe('Smell_Source', r), get_safe('Odour_Carrier', r), lang=lang)

        perceiver = set([p for p in r.get('Perceiver', '').split(' | ') if p not in get_all_smell_words(lang)])

        experience = OlfactoryExperience(curid, smell)
        for p in perceiver:
            if p.lower() in Pronouns.myself(lang) and identifier in docs:  # fixme
                doc, url = docs[identifier]
                if doc.genre not in ['LIT', 'THE']:
                    experience.add_perceiver(doc.author)
                    continue
            p = p.replace(Place.IN_PREFIX[lang], '').strip()
            p = p.replace(VocabularyManager.ARTICLE_REGEX[lang], '').strip()
            if len(p) > 0:
                experience.add_perceiver(Actor.create(p, lang))

        for x in r.get('Quality', '').split('|'):
            experience.add_quality(x.strip(), lang)

        for x in r.get('Effect', '').split('|'):
            experience.add_gesture(x, lang=lang)
        for x in re.split(r'(?: ?\| ?)|(?: and )', r.get('Evoked_Odorant', '')):
            experience.evoked(x.strip(), lang=lang)

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
        if 'Emotion' in r:
            emotion = r.get('Emotion', None).split('|')
            emotion_types = r.get('Emotion_Type', None).split('|')
            emotion_other = r.get('Emotion_Other', None).split('|')
            emotion_sentiment = r.get('Emotion_Sentiment', None).split('|')
            for emot, typ, other, sentiment in zip(emotion, emotion_types, emotion_other, emotion_sentiment):
                if emot.strip() == '':
                    continue
                typ = typ.strip()
                if typ == 'Smell_Word':
                    continue
                typ = other.strip() if typ == 'Other' else typ
                experience.add_emotion(emot, typ.lower(), sentiment)

        used_words = get_multi(('Smell_Word', 'Smell_Source', 'Odour_Carrier', 'Perceiver', 'Quality', 'Effect',
                                'Evoked_Odorant', 'Location', 'Time', 'Emotion'), r)
        frag.add_words(used_words, lang)
        frag.add_annotation(emission, prov)
        frag.add_annotation(smell, prov)
        frag.add_annotation(experience, prov)


def process_benchmark_sheet(language, docs_file):
    if docs_file.endswith('.xlsx'):
        df = pd.read_excel(docs_file, sheet_name=language, dtype=str)
    else:
        df = pd.read_csv(docs_file, sep='\t')
    df.drop_duplicates(inplace=True)
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
        url = r['Link to source']
        to.add_url(url)
        docs[identifier] = to, url


def parse_editor(editor, lang):
    place = None
    if editor is not None:
        editor = editor.strip()
        m = re.search(DLIB_BRACKETS_REGEX, editor)
        if m is not None:
            editor = editor.replace(m.group(0), '').strip()
            if 's.n.' in editor:
                editor = None

            place = Place.from_text(m.group(1), lang=lang, only_interlinked=True)
    return editor, place


def process_metadata(lang, docs_file, intermediate_map, collection):
    df = pd.read_csv(docs_file, dtype=str, sep='\t', encoding='utf-8')
    df.fillna('', inplace=True)
    df.drop_duplicates(inplace=True)

    splitting = ',' if 'old-bailey-corpus' in docs_file else '|'
    internals = {}

    for i, r in tqdm(df.iterrows(), total=df.shape[0]):
        identifier = r['id'].replace('.xml', '').replace('.txt', '')
        if collection == 'eebo':
            identifier = identifier.replace('/', '_')
        internal_id = r.get('identifiers', identifier)

        if intermediate_map is not None:
            post = '' if collection in ['ecco', 'british-library'] else '.txt'
            pointer = intermediate_map[intermediate_map['real_id'] == identifier + post]['id']

            if len(pointer) > 0:
                real_id = pointer.iloc[0]
            else:
                continue
        else:
            real_id = identifier

        if internal_id in internals:
            docs[real_id] = internals[internal_id]
            continue

        year_orig = r['year']
        year = year_orig.replace('.0', '')

        if 'eebo' in docs_file:
            identifier = identifier.replace('/', '_')
            year = re.sub(r'[\[\]]', '.?', year)
            year = re.sub(r'-\??(?!\d)', '.', year)

        editor, edPlace = parse_editor(r.get('editor'), lang)
        publisher, place = parse_editor(r.get('publisher'), lang)
        place = r.get('pub_place', place)

        if collection == 'grimm':
            pt = re.split('[,;.]', r['head'])
            if len(pt) > 1:
                place = pt[0].replace('A ', '')
                year = pt[1]

        date = Time.parse(year, lang=lang)

        # print(identifier, year, date.label)
        place = r.get('archive') or place or DEFAULT_PLACES[collection]
        to = TextualObject(identifier, title=r['title'], date=date, place=place, lang=lang)

        for author in r['author'].split(splitting):
            author = author.replace('\\amp;', '&')

            m = re.search(r"(?:, )?\(?(\d{4}\??)-(\d{4}\??)\)?", author)
            birth = death = None
            if m is not None:
                birth = m.group(1)
                death = m.group(1)
                author = author.replace(m.group(0), '')
            if ',' in author:
                parts = re.sub(r'\.$', '', author).split(',')
                author = f'{parts[1]} {parts[0]}'

            to.add_creator(author, lang, birth, death)

        if editor:
            if editor == "l'auteur":
                to.add_editor(to.creators[0])
            elif ';' in editor:
                for ed in editor.split(';'):
                    to.add_editor(ed, lang, edPlace)
            else:
                to.add_editor(editor, lang, edPlace)

        if publisher:
            if publisher == "l'auteur":
                to.add_publisher(to.creators[0])
            elif ';' in publisher:
                for ed in publisher.split(';'):
                    to.add_publisher(ed, lang, place)
            else:
                to.add_publisher(publisher, lang, place)

        link = r.get('link')
        to.add_url(r.get('doiLink'))
        to.add_url(link)
        to.same_as(r.get('sameAs'))
        to.add_license(r.get('license'))
        to.add(SKOS.editorialNote, r.get('note'))
        to.add(SDO.issn, r.get('issn'))
        if 'pub_date' in r:
            pub_date = date
            if r['pub_date'] != year_orig:
                pub_date = Time.parse(r.get('pub_date', date), lang=lang)
            to.add_pub_date(pub_date)
        if 'royal-society-corpus' in docs_file:
            to.add(RDF.type, SDO.ScholarlyArticle)
        to.add(SDO.about, r.get('primaryTopic'))
        if 'journal' in r:
            to.add(SDO.isPartOf, TextualObject(r['journal'], r['journal'], date=date))

        docs[real_id] = (to, link)
        internals[internal_id] = (to, link)


def process_metadata_ris(lang, ris_file, intermediate_map, collection):
    filename = path.split(ris_file)[-1]
    with open(ris_file) as f:
        r = rispy.load(f, encoding='utf-8')[0]
    identifier = filename.replace('.ris', '')

    if intermediate_map is not None:
        pointer = intermediate_map[intermediate_map['real_id'] == identifier + '.txt']['id']
        if len(pointer) > 0:
            real_id = pointer.iloc[0]
        else:
            print('not found in map', identifier)
            return
    else:
        real_id = identifier

    date = r['date'].replace(' ', '-')

    jo = None
    place = None
    if 'journal_name' in r and r['journal_name'] != r['title']:
        journal = r['journal_name']
        m = re.search(DLIB_BRACKETS_REGEX, journal)
        if m is not None:
            place = Place.from_text(m.group(1))
        jo = TextualObject(collection + r.get('id', journal), journal)

    place = place or DEFAULT_PLACES[collection]
    to = TextualObject(identifier, title=r['title'], date=date, place=place, lang=lang)
    to.add(SDO.volumeNumber, r.get('volume'))
    to.add(SDO.issueNumber, r.get('number'))
    for k in r.get('keywords', []):
        to.add_genre_from_keyword(k)

    if 'publisher' in r:
        to.add(SDO.publisher, Actor(r['publisher']))

    link = None
    if collection == 'dlib':
        link = 'http://www.dlib.si/details/URN:NBN:SI:DOC-' + identifier.split('-')[-1]
        to.add_url(link)

    to.add(SDO.isPartOf, jo)

    docs[real_id] = (to, link)


def run(root, output, lang=None, organised_in_batches=False, metadata_format='tsv', collection=None):
    global DEFAULT_PLACES

    collection = collection or path.split(root)[-1]
    if organised_in_batches:
        for batch in sorted(os.listdir(root)):
            batch_path = path.join(root, batch)
            if not path.isdir(batch_path):
                continue
            run(batch_path, output, lang, False, metadata_format, collection)
        return

    docs_file = path.join(root, 'metadata.xlsx')
    rt = root.replace('/batch-', f'_{lang}')
    codename = rt.split('/')[-1]
    folder_name = path.split(rt)[-1]
    out_folder = path.join(output, folder_name)
    os.makedirs(out_folder, exist_ok=True)

    # init
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    VocabularyManager.setup(config['vocabularies'])

    DEFAULT_PLACES = {
        'ecco': Place.from_text('UK'), # missing
        'pulse': Place.from_text('UK'), # missing
        'british-library': Place.from_text('UK'), # missing
        'old-bailey-corpus': Place.from_text('London'),
        'royal-society-corpus': Place.from_text('London'),
        'eebo': Place.from_text('UK'),  # missing
        'dta': Place.from_text('Germany'),  # missing
        'dta_de2': Place.from_text('Germany'),  # missing
        'dbnl': Place.from_text('Netherlands'),  # missing,
        'dbnl_nl1': Place.from_text('Netherlands'),  # missing,
        'dbnl_nl3': Place.from_text('Netherlands'),  # missing,
        'liberliber': Place.from_text('Italy'),  # missing
        'gutenberg': Place.from_text('UK'),  # missing
        'gutenberg_it': Place.from_text('Italy'),  # missing
        'wikisource': Place.from_text('Italy'),  # missing,
        'gallica': Place.from_text('France'),
        'dlib': Place.from_text('Slovenia'),
        'bibbleue': Place.from_text('Troyes')
    }


    # convert
    if lang is None:
        lang_list = ['en', 'fr', 'it', 'de', 'sl', 'nl']
        for lg in ['English', 'Italian', 'Dutch', 'French', 'German', 'Slovenian', 'Dutch']:
            process_benchmark_sheet(lg, docs_file)
    elif collection == 'british-library':
        periods = [x for x in os.listdir(root) if x.endswith('frames.tsv')]
        for i, b in enumerate(periods):
            print(b)
            frames = path.join(root, b)
            map_file = frames.replace('frames.tsv', 'mapping.tsv')
            metadata = frames.replace('frames.tsv', 'metadata.tsv')

            intermediate_map = pd.read_csv(map_file, dtype=str, sep='\t', encoding='utf-8', names=['id', 'filename'])
            intermediate_map['real_id'] = intermediate_map['filename'].apply(lambda x: x.split('_')[0])
            process_metadata(lang, metadata, intermediate_map, collection)

            Graph.g.serialize(destination=f"{out_folder}/docs{i}.ttl")
            Graph.reset()

            tsv_data = pd.read_csv(frames, sep='\t', index_col=False).drop_duplicates().replace(np.nan, '', regex=True)

            # dividing in batches of 10K rows
            step = 10000
            for j in tqdm(np.arange(0, len(tsv_data) - 1, step), desc="Batches: "):
                process_annotation_sheet(tsv_data[i:i + step], lang='en', codename=codename)
                out = Graph.g.serialize(format='ttl')
                out = out.replace('"<<', '<<').replace('>>"', '>>')
                with open(f"{out_folder}/en{i}_{j}.ttl", 'w') as outfile:
                    outfile.write(out)
                Graph.reset()

        return


    else:
        lang_list = [lang]
        map_file = path.join(root, 'map.tsv')
        intermediate_map = None

        if path.isfile(map_file):
            intermediate_map = pd.read_csv(map_file, dtype=str, sep='\t', encoding='utf-8', names=['id', 'filename'])
            intermediate_map['real_id'] = intermediate_map['filename'].apply(
                lambda x: x.split('text_')[-1].replace('dlib-', ''))

        if metadata_format == 'tsv':
            docs_file = path.join(root, 'metadata.tsv')
            process_metadata(lang, docs_file, intermediate_map, collection)
        elif metadata_format == 'ris':
            for file in sorted(os.listdir(path.join(root, 'metadata'))):
                if file.endswith('.ris'):
                    process_metadata_ris(lang, path.join(root, 'metadata', file), intermediate_map, collection)
        else:
            raise RuntimeError('unrecognized metadata format')

    Graph.g.serialize(destination=f"{out_folder}/docs.ttl")
    Graph.reset()

    for lg in lang_list:
        em_tsv = path.join(root, f"{lg}-frame-elements-emotion.tsv")
        tsv_data = None

        if os.path.isfile(em_tsv):
            with open(em_tsv) as file:
                tsv_data = pd.read_csv(file, sep='\t', index_col=False).drop_duplicates()

        with open(path.join(root, f"{lg}-frame-elements.tsv")) as file:
            temp = pd.read_csv(file, sep='\t', index_col=False).drop_duplicates()
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
    parser.add_argument('--batch', action='store_true')
    parser.add_argument('--metadata', type=str, default='tsv')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run(args.input, args.output, args.lang, args.batch, args.metadata)