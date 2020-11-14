# this script not finished
# read csv data (use this one for small, possibly irregular files)
import os
import sys
import csv
args = sys.argv
from misc import err, wopen

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
print(args)

to_slice = args[2:]
if len(to_slice) == 1:
    to_slice = to_slice[0].strip('"').strip().split(',')
    to_slice = [x.strip() for x in to_slice]

for field in to_slice:
    if field not in hdr:
        err("field not found in header: " + field)

slice_i = [hdr.index(field) for field in to_slice]

f = wopen(args[1] + "_slice.csv")
f.write((','.join([hdr[i] for i in slice_i])).encode())
for i in range(len(lines)):
    f.write(('\n' + (','.join([lines[i][j] for j in slice_i]))).encode())
f.close()

