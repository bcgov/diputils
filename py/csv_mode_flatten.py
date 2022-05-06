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
'''
2019/01/07 mode flattening operation
2090729 revised to refuse comma inside of field, and detect studyid col automatically
20190729 added optional parameter to specify reverse sorting (for antimode)
'''
import operator
from misc import *
import time; t = time.time(); tt = time.time(); ttt = None;
if len(args) < 2:
    err("csv_mode_flatten [input file.csv] [optional parameter that reverses the sorting (antimode)]")

infile = args[1] # "CB_STULVLCB..*" # insert file name here
print "input file", infile
reverse_mode = False # reverse_mode = True for "least frequent thing"

reverse_mode = len(args) > 2

mod = "" if reverse_mode == False else "_revmod"
of = open(infile + mod + "_flatten.csv", "wb")
in_f = open(infile)
if not in_f: err("failed to open input file")

line = in_f.readline().strip()
fields = line.split(","); n_f = len(fields)
fields = [f.strip().lower() for f in fields]
if not 'studyid' in fields:
    err("study id field expected")
s_f_i = -1 #
for i in range(0, len(fields)):
    if fields[i] == 'studyid':
        s_f_i = i
d = {}
ci = 0

f_size = os.stat(infile).st_size
# index the data by studyid
while True:
    line = in_f.readline()
    if not line: break
    line = line.strip()
    w = line.split(",")
    if len(w) != n_f:
        err("input csv should have been extracted with commas inside fields replaced with semicolon, etc")
    if w[s_f_i] not in d:
        d[w[s_f_i]] = []
    d[w[s_f_i]].append(w[0:len(w) - 1])
    ci += 1
    if ci % 100000 == 0:
        ttt = tt
        tt = time.time()
        print "read data %", 100. * float(in_f.tell()) / float(f_size) # , ci/1000, "1/2 k, S/10 k: ", tt-ttt
#if reverse_mode:
#    fields = ['2' + f for f in fields]

# now go through the data
of.write(",".join(fields) + "\n")
ci = 0
for k in d:
    if len(d[k]) > 1000:
        # scrap studyid with unreasonably many entries
        continue
    else:
        dd = d[k]
        out = dd[0]
        #print "dd", dd
        for j in range(0, len(dd[0])):
            # for each field:
            c = {}
            for i in range(0, len(dd)):
                di = dd[i][j]
                if di not in c:
                    c[di] = 0
                c[di] += 1 #  print c
            if reverse_mode:
                sorted_c = sorted(c.items(), key=operator.itemgetter(1), reverse=False)
            else:
                sorted_c = sorted(c.items(), key=operator.itemgetter(1), reverse=True)
            out[j] = sorted_c[0][0]
            #if len(d[k]) > 1:
            #    print "  cc", sorted_c
            #    print "   -> ", out[j] #print "s[0]", s[0], "c[s[0]]", c[s[0]]
        out.append(k) # dont forget studyid
        #print "* out", out
        if len(out) != len(fields):
            err("")
        of.write(",".join(out) + "\n")
    ci += 1
    if ci % 1000 == 0:
        ttt = tt
        tt = time.time()
        print "processing %", 100. * float(ci + 1) / len(d) # ci/1000, "2/2 k, S/10k: ", tt-ttt

in_f.close(); of.close()
print "done"
print "  ", int((ci / (time.time() - t))/1000.), "K lines per sec"
