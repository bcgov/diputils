#  Copyright 2019 Province of British Columbia
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

''' Script for merging tables. This operation is basically a "no RAM"
implementation of a type of join. Hence resilient to large data

20190108 test on small files.. modified 20190311'''
import os
import sys
import csv
from misc import *
import time; t = time.time(); tt = time.time(); ttt = None;
in_fn, infiles = [], []
t_0 = t # start time
if len(sys.argv) < 3:
    err("merge [input file 1] [input file 2] .. [input file n]")

infiles = sys.argv[1:]
for i in range(0, len(infiles)):
    infiles[i] = infiles[i].strip()
    print("input file: ", infiles[i])
    in_fn.append(infiles[i])
    if not os.path.exists(infiles[i]):
        err("file does not exist: " + str(infiles[i]))

n_files = len(in_fn)
out_fn = ("merged.csv") #out_fn = ("merged.csv")

outfile = open(out_fn, "wb")
csv.register_dialect('my',delimiter=",", quoting=csv.QUOTE_ALL,skipinitialspace=True)

d = {} # merged data
newfields = []
newfields_head = []

fi = 0
fstart = []
for i in range(0, n_files):
    fstart.append(fi)
    ci = 0
    print("pass 1: open file:", in_fn[i])
    f = open(in_fn[i])
    line = f.readline().strip()
    fields = line.split(",")
    for j in range(0, len(fields)):
        fields[j] = fields[j].strip('"')
    # last field should appear only once
    if i == n_files-1:
        newfields.extend(fields)
        fi += len(fields)
        for k in range(0, len(fields)):
            newfields_head.append(in_fn[i])
    else:
        newfields.extend(fields[:len(fields)-1])
        fi += len(fields)-1
        for k in range(0, len(fields) -1):
            newfields_head.append(in_fn[i])

for i in range(0, n_files):
    f_size = os.stat(in_fn[i]).st_size
    ci = 0
    print("pass 2: open file:", in_fn[i])
    f = open(in_fn[i])
    line = f.readline().strip()
    fields = line.split(",")

    if not (fields[-1] == "STUDYID" or fields[-1] == "studyid"):
        err("last field req'd to be STUDYID for file" + str(in_fn[i]))
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()
        w = line.split(",")
        if len(w) != len(fields):
            g=open("tmp.csv","wb"); g.write(fields+"\n"+line); g.close()
            reader = csv.reader(open("tmp.csv"), dialect='my')
            hdr, lin = reader
            w = lin
        if len(w) != len(fields):
            err("")
        for j in range(0, len(w)):
            w[j] = w[j].strip('"')
        id_ = w[-1]

        if id_ not in d:
            d[id_] = []
            for j in range(0, len(newfields)):
                d[id_].append('')

        if i == n_files - 1:
            for j in range(0, len(w)):
                d[id_][fstart[i] + j] = w[j]
            #d[id_].extend(w)
        else:
            for j in range(0, len(w)-1):
                d[id_][fstart[i] + j] = w[j]
            #d[id_].extend(w[:len(w)-1])

        ci += 1
        if ci % 100000 == 0:
            ttt = tt
            tt = time.time()
            print("file", i+1,"/", n_files, " %: ", 100. * (float(f.tell()) / float(f_size)), " MB/s:", (float(f.tell()) / 1000000.) / (tt- t_0))# , " t ", tt - t_0

outfile.write((",".join(newfields_head) + "\n").encode())
outfile.write((",".join(newfields) + "\n").encode())
ci = 0
ld = len(d)

print("\nmerging..")
for k in d:
    dk = d[k]
    dk[-1] = k # write out studyid, in case it's not in a specific file
    outfile.write((",".join(dk)+"\n").encode())
    ci += 1
    if ci % 100000 == 0:
        ttt = tt
        tt = time.time()
        print("  %", 100. * float(ci) / float(ld))
outfile.close()
