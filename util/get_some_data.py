from __future__ import division
from __future__ import print_function
import psycopg2
from psycopg2.extras import DictCursor
import json

conn = None
dict_cur = None

try:
    conn = psycopg2.connect("dbname='REDACTED' user='REDACTED' host='localhost' password='REDACTED'")
except:
    raise SystemExit(0)
dict_cur = conn.cursor(cursor_factory=DictCursor)


dict_cur.execute("select * from smart_links where curr = 'Pizza' and type = 'link' order by value desc limit 25;")
bob = dict_cur.fetchall()
incoming = []
for row in bob:
    incoming.append({"name": row['prev'], "val": row['value'], "type": row['type'], "weight": float(row['rev_pct_in'])})

dict_cur.execute("select * from smart_links where prev = 'Pizza' and type = 'link' order by value desc limit 25;")
bob = dict_cur.fetchall()
outgoing = []
for row in bob:
    outgoing.append({"name": row['curr'], "val": row['value'], "type": row['type'], "weight": float(row['pct_in'])})

print('incoming')
print(json.dumps(incoming))
print('outgoing')
print(json.dumps(outgoing))
