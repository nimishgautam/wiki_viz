from __future__ import print_function
from __future__ import division
import fileinput
import re
from tqdm import tqdm
import pickle
from pprint import pprint
import psycopg2
from psycopg2.extras import DictCursor

conn = None
dict_cur = None

def populate_nodes():
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
        node = {
            "incoming_name": vals[0],
            "outgoing_name": vals[1],
            "type": vals[2],
            "value": count
        }
        insert_str = ""
        vals_str = ""
        for val in node:
            insert_str += (val +",")
            vals_str += ("%("+val+")s,")
        vals_str = vals_str[:-1]
        insert_str = insert_str[:-1]
        insert_q = "insert into links (" + insert_str+ ") values ("+ vals_str+")"
        dict_cur.execute(insert_q, node)
        conn.commit()
    pbar.close()

def populate_wts():
    all_vals = pickle.load(open( "freqs.pickle", "rb" ))
    pbar = tqdm(total=len(all_vals) + 1)
    for val in all_vals:
        pbar.update(1)
        node = {
                "node_name": val,
                "node_a": val,
                "node_b": val,
                "a_to_b": 0,
                "b_to_a": 0,
                "node_weight": all_vals[val],
                "is_top_level": True
        }
        insert_str = ""
        vals_str = ""
        for val in node:
            insert_str += (val +",")
            vals_str += ("%("+val+")s,")
        vals_str = vals_str[:-1]
        insert_str = insert_str[:-1]
        insert_q = "insert into nodes (" + insert_str+ ") values ("+ vals_str+")"
        dict_cur.execute(insert_q, node)
        conn.commit()
    pbar.close()


def populate_smart_links():
    print("loading...")
    all_vals = pickle.load(open( "freqs.pickle", "rb" ))
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
        pct_in = 0
        rev_pct_in = 0
        pct_link = 0
        if 'link' in vals[2]:
            try:
                pct_in = count / all_vals[vals[1]]['incoming']
            except:
                pass
            try:
                rev_pct_in = count / all_vals[vals[0]]['incoming']
            except:
                pass
            try:
                pct_link = count / all_vals[vals[1]]['link']
            except:
                pass

        node = {
            "prev": vals[0],
            "curr": vals[1],
            "type": vals[2],
            "value": count,
            "pct_in": pct_in,
            "rev_pct_in": rev_pct_in,
            "pct_link": pct_link,
        }
        insert_str = ""
        vals_str = ""
        for val in node:
            insert_str += (val +",")
            vals_str += ("%("+val+")s,")
        vals_str = vals_str[:-1]
        insert_str = insert_str[:-1]
        insert_q = "insert into smart_links (" + insert_str+ ") values ("+ vals_str+")"
        dict_cur.execute(insert_q, node)
        conn.commit()
    pbar.close()

if __name__ == '__main__':
    try:
        conn = psycopg2.connect("dbname='REDACTED' user='REDACTED' host='localhost' password='REDACTED'")
    except:

        raise SystemExit(0)
    dict_cur = conn.cursor(cursor_factory=DictCursor)
    #populate_wts()
    #populate_nodes()
    populate_smart_links()
