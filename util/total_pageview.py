from __future__ import print_function
import fileinput
import re
from tqdm import tqdm
import pickle
from pprint import pprint
all_vals = {}
all_types = []
print("starting...\n")
pbar = tqdm(total=25617311)
for line in fileinput.input():
    pbar.update(1)
    vals = re.sub(r'\s+', " ", line).split(" ")
    count = 0
    try:
        count = int(vals[3])
    except:
        continue
    if vals[0] not in all_vals:
        all_vals[vals[0]] = {'incoming': 0, 'link': 0, 'total': 0}
    if vals[1] not in all_vals:
        all_vals[vals[1]] = {'incoming':0, 'link': 0, 'total':0}
    if vals[2] not in all_types:
        all_types.append(vals[2])
    all_vals[vals[0]]['total'] += count
    all_vals[vals[1]]['total'] += count
    if 'link' in vals[2]:
        all_vals[vals[1]]['link'] += count
        all_vals[vals[0]]['link'] += count
        all_vals[vals[1]]['incoming'] += count

pbar.close()
print("all types:")
pprint(all_types)
print("writing file...\n")
with open('freqs.pickle', 'wb') as handle:
  pickle.dump(all_vals, handle)
