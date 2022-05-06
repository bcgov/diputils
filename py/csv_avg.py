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
'''20190917 average everything else, on different possibilities for selected col's
 assumption: the selected col's are categorical in nature (not verified)
'''
from misc import *

if len(args) < 3:
    err("csv_avg.py [input csv file] [select field 1] ...")

in_f = args[1]
out_f = in_f + "_csv-avg.csv"

f = ropen(in_f)
hdr = f.readline().strip().split(",")
f_i = {hdr[i]: i for i in range(0, len(hdr))}
i_f = {i: hdr[i] for i in range(0, len(hdr))}

select_fields = []
for i in range(2, len(args)):
    select_fields.append(args[i])

print "select_fields", select_fields
# sanity check
for i in select_fields:
    if i not in hdr:
        err("select field provided not found in header")

total, count = {}, {}

while True:
    line =  f.readline()
    if not line: break
    w = line.strip().split(",")
    w = [w[i].strip() for i in range(0, len(w))]

    idx, tot = [], 0.
    for i in range(0, len(w)):
        if hdr[i] in select_fields:
            idx.append(w[i])
    idx = ",".join(idx)

    for i in range(0, len(w)):
        if hdr[i] not in select_fields: # averaged field
            if hdr[i] not in total:
                total[hdr[i]] = {}
            if idx not in total[hdr[i]]:
                total[hdr[i]][idx] = 0.
            if hdr[i] not in count:
                count[hdr[i]] = {}
            if idx not in count[hdr[i]]:
                count[hdr[i]][idx] = 0.
            try:
                total[hdr[i]][idx] += float(w[i]) if w[i] != '' else float(0.)
            except:
                if w[i] == '':
                    pass
                else:
                    print("Error: str(hdr):" + str(hdr))
                    err(str(w))
            count[hdr[i]][idx] += 1.

o_f = wopen(out_f)
s =  "field_averaged," + ",".join(select_fields) + ",average"
o_f.write(s)

for field in total:
    for idx in total[field]:
        s = str(field) + ',' + str(idx) + ','
        s += str(round(total[field][idx] / count[field][idx], 9))
        o_f.write("\n" + s)
o_f.close()
