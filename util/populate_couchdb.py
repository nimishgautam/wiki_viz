from __future__ import print_function
from __future__ import division
import fileinput
import json
import re
from tqdm import tqdm
import pickle
import sys
import couchdb

reload(sys)
sys.setdefaultencoding('utf8')

#pbar_val = 25617311
pbar_val = 2316032
couchdb_server = None
dbase = None
delim = "<<>>"
fhandle = None

def get_totals():
    print("starting...\n")
    all_vals = {}
    pbar = tqdm(total=pbar_val)
    for line in fileinput.input():
        pbar.update(1)
        vals = re.sub(r'\s+', " ", line).split(" ")
        count = 0
        try:
            count = int(vals[3])
        except:
            continue
        prev = vals[0]
        curr = vals[1]
        link_type = vals[2]
        if 'link' not in link_type:
            continue
        if prev not in all_vals:
            all_vals[prev] = 0
        if curr not in all_vals:
            all_vals[curr] = 0
        all_vals[prev] += count
        all_vals[curr] += count
    pbar.close()
    print("saving...")
    with open('freqs.pickle', 'wb') as handle:
      pickle.dump(all_vals, handle)

def populate_values():
    print("loading...")
    all_weights = pickle.load(open( "freqs.pickle", "rb" ))
    print("loaded weights")
    pbar = tqdm(total=pbar_val)
    for line in fileinput.input():
        pbar.update(1)
        vals = re.sub(r'\s+', " ", line).split(" ")
        count = 0
        try:
            count = int(vals[3])
        except:
            continue
        prev = vals[0]
        curr = vals[1]
        link_type = vals[2]

        if 'link' not in link_type:
            continue

        format_output("incoming",curr,{
        "name":prev,
        "type":"link",
        "weight":all_weights[prev],
        "val": count
        })

        format_output("outgoing", prev,{
        "name":curr,
        "type":"link",
        "weight":all_weights[curr],
        "val": count
        })
    pbar.close()
    fhandle.close()


def format_output(direction, node_name, value_dict):
    fhandle.write(node_name + delim + direction + delim + json.dumps(value_dict) + delim + "\n")


def add_to_couch():
    current_node = ""
    current_direction = ""
    current_node_struct = None
    pbar = tqdm(total=pbar_val)
    for line in fileinput.input():
        parsed = line.split(delim)
        node_name = parsed[0]
        direction = parsed[1]
        value_dict = json.loads(parsed[2])
        if node_name != current_node:
            if current_node:
                add_node_to_couch(current_node_struct)
                pbar.update(1)
            current_node = node_name
            current_node_struct = {'_id': node_name, 'title': node_name, 'incoming':[], 'outgoing':[]}
        current_node_struct[direction].append(value_dict)
    pbar.close()

def add_node_to_couch(node_struct):
    try:
        dbase.save(node_struct)
    except couchdb.http.ResourceConflict as e:
        old = dbase[node_struct['_id']]
        old['incoming'] += node_struct['incoming']
        old['outgoing'] += node_struct['outgoing']
        dbase.save(old)


def add_to(direction, node_name, value_dict):
    document = None
    try:
        document = dbase[node_name]
    except:
        document = {'_id': node_name, 'title': node_name, 'incoming':[], 'outgoing':[]}
        dbase.save(document)
        document = dbase[node_name]

    document[direction].append(value_dict)
    dbase.save(document)

if __name__ == '__main__':
    try:
        pbar_val = int(sys.argv[1])
    except:
        pass
    couchdb_server = couchdb.Server()
    dbase = couchdb_server['wiki_stream']

    fhandle = open('unsorted.tsv', 'wb')

    #populate_values()
    #get_totals()
    add_to_couch()
