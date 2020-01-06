'''
python3 make_fakedata.py
'''
import os
import sys
import csv
# next: iterate metadata, classify field types: nominal, ordinal, date?

intersect, union = None, None
files = os.popen('ls -1 metadata/')
for f in files:
    f = f.strip()

    fn = 'metadata/' + f
    with open(fn, encoding="utf8", errors='ignore') as csvfile:
        n_fields = 0
        csvreader, is_header = csv.reader(csvfile, delimiter=','), True
        for row in csvreader:
            row = [r.strip() for r in row]
            if is_header:
                n_fields = len(row)
                print(n_fields, row, fn)
                if intersect is None:
                    intersect, union = set(row), set(row)
                else:
                    intersect = intersect.intersection(set(row))
                    union = union.union(set(row))
            else:
                if len(row) != n_fields:
                    err("expected: " + str(n_fields) + " got: " + str(len(row)))
            is_header = False # already visited header

# if 'Code Table' in hdr:

print("intersection", intersect)
print("union",union)
print("good news: all metadata files had same # of fields, within a table!")
print("done")

