import os
from os.path import join
import shutil
from tqdm import tqdm

PREP = 'batch-'
root = './'
for batch in tqdm(sorted(os.listdir(root))):
    try:
        os.rename(join(root, batch, 'extracted.txt'),
                  join(root, batch, 'sl-frame-elements.tsv'))
        os.rename(join(root, batch, 'converted-meta.tsv'),
                  join(root, batch, 'map.tsv'))
        shutil.rmtree(join(root, batch, 'bertout'))
        shutil.rmtree(join(root, batch, 'converted'))
        shutil.rmtree(join(root, batch, 'txt'))
    except:
        pass
