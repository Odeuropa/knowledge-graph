# author: menini@fbk.eu
# extract plain text from gutenberg zip-based archive and create a metadata output file

import json
import os
import urllib.request
import zipfile
from urllib.parse import urlparse
from tqdm import tqdm
import requests
from time import sleep

root = '/data/odeuropa/FR/gutenberg/'
out = '/data/odeuropa/FR/gutenberg_clean/'
metadata_out = './gutenberg_metadata.tsv'

os.makedirs(out, exist_ok=True)


def check_date(myquery):
    q_safe = urllib.parse.quote_plus(myquery)
    sleep(0.5)
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=' + q_safe)
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        exit(1)
    data = json.loads(response.text)
    year = 9999

    if int(data['totalItems']) == 0:
        return year

    for i in data['items']:
        if 'publishedDate' in i['volumeInfo']:
            publicationYear = i['volumeInfo']['publishedDate'][:4]
            if publicationYear.isdecimal():
                if int(publicationYear) < int(year):
                    year = publicationYear
    return year


def find_metadata(book):
    with z.open(book, 'r') as f:
        my_author = ""
        my_title = ""
        my_book_id = ""

        checkAut = False
        checkTit = False
        checkID = False
        for line in f:
            line = line.decode("iso-8859-1")
            line = line.strip()
            if line.startswith("Author") and not checkAut:
                my_author = line.replace("Author:", "").strip()
                checkAut = True
            if line.startswith("Title") and not checkTit:
                my_title = line.replace("Title:", "").strip()
                checkTit = True
            if "EBook #" in line and not checkID:
                my_book_id = line.split("#")[len(line.split("#")) - 1].replace("]", "").strip()
                checkID = True
        if checkAut == True and checkTit == True:
            query_word = my_title + " " + my_author
            return query_word, my_author, my_title, my_book_id

    f.close()


metaFile = open("metadata.txt", 'w')
metaFile.write('\t'.join(('id', 'year', 'author', 'title', 'link')))
metaFile.write('\n')

bookCount = 0

file_list = []
for root, dirs, files in os.walk(root):
    for name in files:
        if name.endswith("-8.zip"):
            file_list.append(os.path.join(root, name))

for zfile in tqdm(file_list):
    with zipfile.ZipFile(zfile) as z:
        for book in z.namelist():
            bookCount = bookCount + 1
            # print(bookCount)
            try:
                stringForQuery, myAuthor, myTitle, myBookID = find_metadata(book)
            # print(myTitle)
            except:
                continue

            if len(stringForQuery) < 1:
                # print("SKIP", bookCount, book, stringForQuery)
                continue

            publicationYear = check_date(stringForQuery)

            if int(publicationYear) < 1600 or int(publicationYear) > 1930:
                # print("SKIP", bookCount, book, stringForQuery, publicationYear)
                continue
            # print("OK", bookCount, book, publicationYear, myAuthor, myTitle)

            with z.open(book, 'r') as f:
                textDict = dict()

                newOutName = str(publicationYear) + "__" + str(myAuthor) + "__" + str(myTitle)
                newOutName = newOutName[:200].replace('/', '_')

                outFile = open(os.path.join(out, newOutName + ".txt"), 'w')

                for line in f:
                    line = line.decode("iso-8859-1")
                    outFile.write(line)

                outFile.close()

            metaFile.write('\t'.join((
                newOutName,
                str(publicationYear),
                myAuthor,
                myTitle,
                "https://www.gutenberg.org/ebooks/" + myBookID
            )))
            metaFile.write('\n')
