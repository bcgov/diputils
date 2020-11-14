# Falliable method for cleaning up CSV data: this script not finished
# read csv data (use this one for small, possibly irregular files)
import os
import sys
import csv
args = sys.argv

if len(args) < 2:
    print("csv_clean.py [input csv file]")
    sys.exit(1)

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

if len(count.keys()) > 1:
    print("Error: ragged array or messy data?"); sys.exit(1)

hdr = lines[0]
lines = lines[1:]

for i in range(0, len(lines)):
    for j in range(0, len(lines[i])):
        lines[i][j] = lines[i][j].replace(',', ';')

for j in range(0, len(hdr)):
    hdr[j] = hdr[j].replace(',', ';')

f = open(args[1] + "_clean.csv", "wb")
f.write((','.join(hdr)).encode())

for line in lines:
    f.write(('\n' + ','.join(line)).encode())

print("+w " + args[1] + "_clean.csv")
f.close()
