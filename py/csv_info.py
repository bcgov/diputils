# guess data types of cols of csv. Ignore data with no info (one outcome only)
import os
import sys
from misc import load_fields
args = sys.argv
dat = load_fields("../test/merge.csv" if len(args) < 2 else args[1])

types = {}
for k in dat.keys():
    d, is_float = dat[k], True # extract col
    for i in range(0, len(d)):
        try:
            f = float(d[i])
        except Exception:
            is_float = False
    
    t = "float" if is_float else "str"
    lsd = len(set(d))
    if lsd > 1:
        print(t, k, lsd if lsd > 12 else set(d))
        if not t in types:
            types[t] = []
        types[t].append(k)

sys.exit(0)

if len(args) < 3:
    print(types)
else:
    if args[2] in ['str', 'float']:
        print(','.join(types[args[2]]))
