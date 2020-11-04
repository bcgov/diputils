import os
import sys
import csv
args = sys.argv

csv_file = open(args[1]) 

reader = csv.reader(csv_file, delimiter=',')
for row in reader:
    print(row)

