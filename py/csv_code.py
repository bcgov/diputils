import os
import sys
from misc import *

d = load_fields(args[1])

names = []
lookup = {}
fields = d.keys()
for f in fields:
    codes = list(set(d[f]))
    print(codes)
    my_lookup = {}
    for i in range(len(codes)):
        my_lookup[codes[i]] = i
    lookup[f] = my_lookup

    names.append(';'.join([str(codes[i]) + "->" + str(i) for i in range(len(codes))]))

f = wopen(args[1] + "_code.csv")
f.write((','.join(names)).encode())
for i in range(0, len(d[fields[0]])):
    f.write(('\n' + ','.join([d[fields[j] for j in range(len(fields))]])).encode())
f.close()
