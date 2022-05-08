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

import csv
import sys
from misc import *
import time; t = time.time(); tt = time.time(); ttt = None;
infile = "2019-01-08_merged.csv_slice"

ci = 0
fields = None
csv.register_dialect('my',delimiter=",", quoting=csv.QUOTE_ALL,skipinitialspace=True)
f = open(infile)
line = f.readline().strip()
fields = line.split(",")

count = {} # mapping from the set of possible observations, to the integers..
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
    # update count

    # if I haven't recorded a count for that observation yet, start at 0..
    if w[-1] not in count:
        count[w[-1]] = 0
    # add one...
    count[w[-1]] += 1
    ci += 1
    if ci % 10000 == 0:
        ttt = tt
        tt = time.time()
        print ci/1000, "1/2 k, S/10 k: ", tt-ttt
# print "c", len(count)

count_count = {}
for id_ in count:
    if count[id_] not in count_count:
        count_count[count[id_]] = 0
    count_count[count[id_]] += 1
print "count of counts", count_count
print "for finished product ,want only count of 1 to occur"