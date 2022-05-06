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
# alterate approach to csv_bin:
# convert categorical variables to continuous (instead of the other way around)
# objective: data all same type!
'''
import math
import operator
from misc import *
if len(args) < 2:
    err("for numeric-only col.s of a csv, bin those quantities into modes (if applicable)" +
        "\n\tcsv_bin [input file.csv]")
in_f = args[1]

if not exists(in_f):
    err("could not find input file")

# input data:
lines = open(in_f).readlines() # number of lines in input csv
hdr = lines[0] # header row-- field names-- from csv
fields = hdr.strip().lower().split(',') # array of field names
n_fields = len(fields) # number of fields
lines = lines[1:] # non-header data lines from csv
n_rows = len(lines) # number of data lines from csv

# intermediate data
data = {i: [] for i in range(0, len(fields))} # "data frame" indexed by field index
is_numeric = {i: True for i in range(0, len(fields))} # numeric variable indicator
hist = {i: {} for i in range(0, len(fields))} # histogram indexed by field index


print "building histograms and converting to columnar format.."
# for each line
for i in range(0, len(lines)):
    w = lines[i].strip().lower().split(',')
    if len(w) != n_fields:
        print fields
        print w
        err("failed to parse csv. could be commas in fields.")

    # for each field
    for j in range(0, n_fields):
        d = w[j].strip()

        # for this field, incr. the count for this observation AKA value
        if d not in hist[j]:
            hist[j][d] = 0
        hist[j][d] += 1

        # take the value and tack it on to our so-called collumnar representation
        data[j].append(d) # n.b. this variable indexed by field-index


for i in range(0, n_fields):
    print i, "nv", len(hist[i])


print "preparing new data frame.."

#new_data = {}
new_fields = []
nvn_i, i_nvn = {}, {}
# map from new variable name, to new field index and vice versa
ci = 0
for j in range(0, n_fields):
    print "\tfield_i:", j + 1, "of", n_fields
    for k in hist[j].keys():
        nvn = fields[j] + "=" + k
        nvn_i[nvn] = ci # map new variable name onto new col. index
        i_nvn[ci] = nvn # map new col. index onto new variable name
        #new_data[nvn] = []
        #for i in range(0, n_rows):
        #    new_data[nvn].append(None)
        ci += 1
        new_fields.append(nvn)

print "producing output.."

# maps in hand, recode the data!
ofn = in_f + "_csv_onehot.csv"
o_f = open(ofn, "wb")
if not o_f:
    err("failed to open output file: " + ofn)

o_f.write(",".join(new_fields))

for i in range(0, n_rows):
    if i % 10 == 0:
        print "row ", i+1, "of", n_rows
    ci = 0
    datarow = []
    for j in range(0, n_fields):
        for k in hist[j].keys():
            nvn = fields[j] + "=" + k

            one_hot = '1.' if data[j][i] == k else '0.'
            datarow.append(one_hot)

            nvni = nvn_i[nvn]
            if nvni != ci:
                err("index mismatch") # just assure ourselves that keys() is repeatable
            ci += 1

    o_f.write("\n" + (",".join(datarow)))
o_f.close()
