# this script not finished
# read csv data (use this one for small, possibly irregular files)
import os
import sys
import csv
args = sys.argv

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

print("to_slice", args[1:])
