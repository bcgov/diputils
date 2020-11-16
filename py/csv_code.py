# apply numeric codes to each col of a csv
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
for i in range(0, len(d[list(fields)[0]])):
    row = [     d[list(fields)[j]][i] for j in range(len(fields))]
    row = [lookup[list(fields)[j]][row[j]] for j in range(len(fields))]
    row = [str(x) for x in row]
    f.write(('\n' + ','.join(row)).encode())


f.close()
