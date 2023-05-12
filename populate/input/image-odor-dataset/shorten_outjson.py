# short script to reduce the dimension of the annotation file
import re

with open('odeuropa_29k_nms_005.json') as f:
    data = f.read()

data = data.replace('/media/prathmeshmadhu/myhdd/odeuropa/annotations-nightly/mmodor_imgs/', '')
data = data.replace('"category_id"', '"cid"')
data = data.replace('"image_id"', '"iid"')
data = re.sub(r', "area": \d+}', '}', data)
with open('annotations_automatic.json', 'w') as f:
    f.write(data)