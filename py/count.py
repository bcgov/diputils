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
'''20190311 accumulate observations in CSV file.. important for Q.A.!
'''
import os
import sys
import operator
from misc import *

# note: need to finish documenting this
if len(sys.argv) < 2:
    err("usage: count.py [csv input file]")

f = open(sys.argv[1])
f_count = open(sys.argv[1] + "_count.csv", "wb")
f_freq = open(sys.argv[1] + "_frequ.csv", "wb")

IGNORE_STUDYID = len(sys.argv) > 2

fields = f.readline().strip().split(",")
print("fields", fields)
occ = []

for i in range(0, len(fields)):
    occ.append({})

ci = 1
import time
f_size = os.stat(sys.argv[1]).st_size
ttt = tt = t_0 = time.time()

while True:
    line = f.readline()
    if not line: break
    word = line.strip().split(",")
    if len(word) != len(fields):
        print("warning: incorrect number of fields, line: ", ci)
    for i in range(0, len(word)):
        d = word[i].strip()
        if d not in occ[i]:
            occ[i][d] = 0.
        occ[i][d] += 1.
    ci += 1
    if ci % 100000 == 0:
        ttt = tt
        tt = time.time()
        print("file", " %: ", 100. * (float(f.tell()) / float(f_size)), " MB/s:", (float(f.tell()) / 1000000.) / (tt- t_0))#

counts = []
frequs = []
for i in range(0, len(fields)):
    if IGNORE_STUDYID and (fields[i] == "studyid"):
        continue
    print("sorting field ", fields[i], "..")
    if True: #len(occ[i]) < 100:
        n = 0  # number of observations
        #s = str(fields[i])
        occ_i = sorted(occ[i].items(), key=operator.itemgetter(0))
        for j in occ_i:
            n += j[1]
            counts.append(str(fields[i]) + "," + str(j[0]) + "," + str(j[1]))
        occ_i = sorted(occ[i].items(), key=operator.itemgetter(1), reverse=True)
        for k in range(0, len(occ_i)):
            j = occ_i[k]
            j = list(j)
            j[1] = j[1] * (1. / float(n))  # was 100. / float(n)
            j = tuple(j)
            frequs.append(str(fields[i]) + "," + str(j[0]) + "," + str(j[1]))

f_count.write("variable,value,count") #COUNTS\n".encode())
for c in counts:
    f_count.write(('\n' + str(c)).encode())

f_freq.write("variable,value,frequency") #FREQUENCIES\n".encode())
for f in frequs:
    f_freq.write(('\n' + str(f)).encode())
