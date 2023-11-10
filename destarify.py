'''This code removes the RDF-star part'''
import os
import re
from tqdm import tqdm

source = './dump'
dest = './dump-flat'

for folder in tqdm(sorted(os.listdir(source))):
    if not os.path.isdir(os.path.join(source, folder)):
        continue
    for file in os.listdir(os.path.join(source, folder)):
        if not file.endswith('.ttl'):
            continue
        with open(os.path.join(source, folder, file)) as f:
            orig = f.read()

        final = re.sub(r'<< (.+) >> .+\.', r'\1 .', orig, flags=re.MULTILINE)
        os.makedirs(os.path.join(dest, folder), exist_ok=True)
        with open(os.path.join(dest, folder, file), 'w') as f:
            f.write(final)

for file in os.listdir(os.path.join(source, 'vocabularies', 'vocabularies')):
    if not file.endswith('.ttl'):
        continue
    with open(os.path.join(source, 'vocabularies', 'vocabularies', file)) as f:
        orig = f.read()

    final = re.sub(r'<< (.+) >> .+\.', r'\1 .', orig, flags=re.MULTILINE)
    os.makedirs(os.path.join(dest, 'vocabularies'), exist_ok=True)
    with open(os.path.join(dest, 'vocabularies', file), 'w') as f:
        f.write(final)