from __future__ import division
from __future__ import print_function
import psycopg2
from tqdm import tqdm
from psycopg2.extras import DictCursor
import fileinput

# *MUST* BE GREATER THAN .51 TO BE MEANINGFUL!!!
THRESSHOLD = .51
USE_OUTPUT = True

NODE_NAME_BASE_STR = "NODE_"
NODE_NAME_BASE_VAL = 0

conn = None
dict_cur = None
regular_cur = None

def get_top_level_nodes():
    top_q = "select node_name from nodes where is_top_level = true and node_weight > 3000"
    regular_cur.execute(top_q)
    return regular_cur.fetchall()

def check_for_pair(node_name):
    wt_q = "select * from nodes where node_name = %s"
    link_q = "select * from links where incoming_name = %s and value >= %s and type = 'link' "
    find_q = "select * from links where incoming_name = %s and outgoing_name = %s"
    # value for thresshold
    dict_cur.execute(wt_q, (node_name,))
    node_info = dict_cur.fetchone()
    max_check = node_info['node_weight'] * THRESSHOLD
    dict_cur.execute(link_q, (node_name, max_check))
    rows = dict_cur.fetchall()
    # if any incoming links match
    for possible_pair in rows:
        #This node is providing a majority of incoming connections... check the other way around
        possible_pair_name =  possible_pair['incoming_name']
        dict_cur.execute(wt_q, (possible_pair_name,))
        pair_check = dict_cur.fetchone()
        max_for_pair = pair_check['node_weight'] * THRESSHOLD
        dict_cur.execute(find_q, (node_name, possible_pair_name))
        pair_checking = dict_cur.fetchall()
        for pair_to_check in pair_checking:
            if pair_to_check['value'] >= max_for_pair:
            # this node also provides a > thresshold amount of incoming connections to candidate
            # .: pair found
                return {"pair_name": possible_pair_name,
                        "a_to_b": possible_pair['value'],
                        "b_to_a": pair_checking['value']}

    # nothing found
    return None


def examine_nodes():
    nodes_created = 0
    to_process = get_top_level_nodes()
    pbar = None
    if(USE_OUTPUT):
        print( unicode(len(to_process)) + " nodes" )
        pbar = tqdm(total=len(to_process)+1)
    for node in to_process:
        if(USE_OUTPUT):
            pbar.update(1)
        node_pair = check_for_pair(node[0])
        if(node_pair):
            new_node_name = NODE_NAME_BASE_STR + unicode(NODE_NAME_BASE_VAL)
            new_node = merge_nodes(node[0], node_pair, new_node_name)
            try:
                del_index = to_process.index((node_pair['pair_name'],))
                del to_process[del_index]
            except ValueError:
                pass
            nodes_created += 1
            NODE_NAME_BASE_VAL += 1
    if(USE_OUTPUT):
        pbar.close()
    return nodes_created

def merge_nodes(nodeA_name, node_pair, new_node_name):
    wt_q = "select * from nodes where node_name = %s"
    dict_cur.execute(wt_q, (nodeA_name,))
    nodeA = dict_cur.fetchone()
    dict_cur.execute(wt_q, (node_pair['pair_name'],))
    nodeB = dict_cur.fetchone()
    cann_name = nodeA['cann_name']
    if (nodeB['node_weight'] > nodeA['node_weight']):
        cann_name = nodeB['cann_name']
    new_node = {'node_name' : new_node_name,
                'node_weight': nodeA['node_weight'] + nodeB['node_weight'],
                'is_top_level':True,
                'node_a': nodeA["node_name"],
                'node_b': nodeB["node_name"],
                'a_to_b': node_pair['a_to_b'],
                'b_to_a': node_pair['b_to_a'],
                'cann_name': cann_name
                }
    replace_nodes("incoming", nodeA["node_name"], nodeB["node_name"], new_node_name)
    replace_nodes("outgoing", nodeA["node_name"], nodeB["node_name"], new_node_name)
    insert_str = ""
    vals_str = ""
    for val in new_node:
        insert_str += (val +",")
        vals_str += ("%("+val+")s,")
    vals_str = vals_str[:-1]
    insert_str = insert_str[:-1]
    insert_q = "insert into nodes ("+ insert_str +") values(" + vals_str + ")";
    dict_cur.execute(insert_q, new_node)
    conn.commit()


def replace_nodes(direction, nodeA_name, nodeB_name, new_node_name):
    opposite = "outgoing"
    if direction == "outgoing":
        opposite = "incoming"

    link_q = "select * from links where " + direction + "_name = %s and type = 'link' "

    dict_cur.execute(link_q, (nodeA_name,))
    results_node_A = dict_cur.fetchall()
    dict_cur.execute(link_q, (nodeB_name,))
    results_node_B = dict_cur.fetchall()

    for result in results_node_A:
        node_B_val = 0
        for pairing in results_node_B:
            if pairing[opposite+"_name"] == result[opposite+"_name"]:
                node_B_val += pairing["value"]
                dict_cur.execute("delete from links where id = " + result['id'])
                conn.commit()
                del results_node_B[results_node_B.index(pairing)]
                break
        dict_cur.execute("update links set "+direction+"_name = %s, value = %s where id = %s", (new_node_name, result['value'] + node_B_val, result['id']))
        conn.commit()

    for result in results_node_B:
        dict_cur.execute("update links set "+direction+"_name = %s where id = %s", (new_node_name, result['id']))
        conn.commit()


if __name__ == '__main__':
    try:
        conn = psycopg2.connect("dbname='REDACTED' user='REDACTeD' host='localhost' password='REDACTED'")
    except:
        raise SystemExit(0)
    dict_cur = conn.cursor(cursor_factory=DictCursor)
    regular_cur = conn.cursor()
    nodes_created = examine_nodes()
    if(USE_OUTPUT):
        print("Nodes Created:")
        print(nodes_created)
    while(nodes_created > 0):
        nodes_created = examine_nodes()
        if(USE_OUTPUT):
            print("Nodes Created:")
            print(nodes_created)
