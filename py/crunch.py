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
'''20190304 filter a data set with multiple records, aggregating records with same studyid
'''
import os
import sys
import operator
from misc import *

if len(sys.argv) < 2:
    err( "usage: crunch.py [input file]")

fn = sys.argv[1].strip()
if not os.path.exists(fn):
    err("file not found: " + fn)

print "loading data.."
words = open(fn).read().strip().split("\n")
fields = words[0].strip().split(",")
for i in range(0, len(fields)):
    fields[i] = fields[i].strip()

print fields
if(fields[-1] != "studyid"):
    err("last field must be studyid")

print "cleaning data.."
words = words[1:]
for i in range(0, len(words)):
    words[i] = words[i].strip().split(",")
    for j in range(0, len(words[i])):
        words[i][j] = words[i][j].strip()

print "accumulating data.."
dat = {}
for i in range(0, len(words)):
    s_i = words[i][-1]
    if s_i not in dat:
        dat[s_i] = []
    dat[s_i].append(words[i][:-1])
print "free some mem.."
words = None

print "crunching.."
fields = fields[:-1]
print "fields:", fields
outf = open(fn + "_crunch.csv", "wb")

stuff = ["most_frequent", "first", "last", "n_observ", "n_outcome"]
line = "studyid"
for j in range(0, len(fields)):
    for i in range(0, len(stuff)):
        line += "," + fields[j] + "_" + stuff[i]
outf.write(line + "\n")
print line

for s_i in dat: # for each studyid
    line = str(s_i)
    obs = dat[s_i]
    # for each obs, calc first, last, mode for each field
    d = []
    #  print s_i,":"
    for j in range(0, len(fields)):
        # print "field:", fields[j]
        d_j = []
        for i in range(0, len(obs)):
            d_j.append(obs[i][j])
        # first, last mode;
        #print "\t",d_j
        d_j.sort()
        #print "\t",d_j
        first, last = d_j[0], d_j[-1]
        n = len(obs)
        count = {}
        for d_ji in d_j:
            if d_ji not in count:
                count[d_ji] = 0
            count[d_ji] +=1
        count = sorted(count.items(), key=operator.itemgetter(1), reverse=True)
        #print "\t",count
        #print count[0][0], first, last, n, len(count)
        line += "," + (",".join([count[0][0], first, last, str(n), str(len(count))]))
    outf.write(line + "\n")
#for i in range(0, len(words)):
