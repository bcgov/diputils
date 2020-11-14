# this script not finished
# read csv data (use this one for small, possibly irregular files)
import os
import sys
import csv
args = sys.argv
from misc import err

if len(args) < 2:
    print("csv_slice.py [input csv file] [variable to slice] .. [variable to slice]"); sys.exit(1)

lines = []
csv_file = open(args[1]) 
reader = csv.reader(csv_file, delimiter=',')


count = {}
for row in reader:
    N = len(row)
    if N not in count:
        count[N] = 0
    count[N] += 1
    lines.append(row)
print(count)

hdr = lines[0]
lines = lines[1:]

to_slice = args[1:]
for field in to_slice:
    if field not in hdr:
        err("field not found in header: " + field)

slice_i = [hdr.index(field) for field in to_slice]

f = open(args[1] + "_slice.csv", "wb")
f.write((','.join([hdr[i] for i in slice_i])).encode())
for i in range(len(lines)):
    f.write('\n' + (','.join([lines[i][j] for f in slice_i])).encode())
f.close()

