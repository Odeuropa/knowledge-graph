import os
import pandas as pd
import requests
from tqdm import tqdm

if not os.path.isdir('images'):
    os.makedirs('images')

df = pd.read_csv('metadata.csv', encoding='latin-1')
df = df[['File Name', 'Image URL']]

for fname,url in tqdm(list(df.values)):
    pth = f'images/{fname}'
    r = requests.get(url)
    if r.status_code != 200: 
        print(f'failed to download {url}')
        continue
    open(pth, 'wb').write(r.content)

