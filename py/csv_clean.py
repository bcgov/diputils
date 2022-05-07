'''Not-invincible method for cleaning up CSV data: script needs some revision.

It can read csv data (definitely can use this one for small,
                      possibly irregular files, no problem!!!) 

20220506 NOTE:
Can use this script for replacing comma with ;,
so that some dumber (but faster) C/C++ programs will be able to
use/read the result

i.e. it's faster to parse CSV where:
    (*) the contents aren't closed in quotation marks
    (*) the only comma that appear, are the delimiters. So replacing
    every non-delimiting ',' with ';' or some other character, can be a 
    performance enhancing option. 

Example usage:

    python3 ~/GitHub/diputils/py/csv_clean.py  Feb-16th-2022-03-35PM-Flight-Airdata.csv
    ~/GitHub/diputils/cpp/csv_select.exe select_file isphoto Feb-16th-2022-03-35PM-Flight-Airdata.csv_clean.csv

where contents of file isphoto is 'isPhoto\n1'

(In this example, selected fields from drone telemetry data sheet (csv),
    where the flag indicated a photo was taken)'''
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
