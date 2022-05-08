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

import math
import pickle
import pandas
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

        # convert blank, n, no to 0.
        d = '0' if (d == 'no' or d == 'n' or d =='') else d

        # convert yes and y to 1.
        d = '1' if (d == 'yes' or d =='y') else d

        # try float conversion
        try:
            d = float(d)
        except:
            # record that this field is not numeric
            is_numeric[j] = False

        # for this field, incr. the count for this observation AKA value
        if d not in hist[j]:
            hist[j][d] = 0
        hist[j][d] += 1

        # take the value and tack it on to our so-called collumnar representation
        data[j].append(d) # n.b. this variable indexed by field-index


print ",".join(fields) # print out the field names
d_qcut = {}

# clean up the field names
fields = [fields[i].replace('/', '_') for i in range(0, n_fields)]

# for each field
for i in range(0, n_fields):
    n_values = len(hist[i].keys()) # number of distinct values observed, this field
    keys = hist[i].keys() # the distinct values that were observed

    # print out some debug info
    print ("****", i+1, "of", n_fields, fields[i], "n_values", str(n_values),
            (str(keys) if n_values < 25 else ""), "min", min(keys), "max", max(keys))

    '''
    #print str(fields[i]) + str(",") + str(len(hist[i])) + str(",") + str(is_numeric[i])
    shist = [[j, hist[i][j]] for j in hist[i]]
    shist = sorted(shist, key=operator.itemgetter(0), reverse=False)
    '''
    nc =  5 # target number of bins
    if not is_numeric[i] or n_values <= nc:
        # don't bin the data.
        print hist[i].keys()
    else:
        qcut_pfn = '.qcut_' + str(i) +'.p'
        if exists(qcut_pfn):
            d_qcut[i] = pickle.load(open(qcut_pfn))
        else:
            qcut_n = nc
            d_qcut[i] = pandas.qcut(data[i], qcut_n, duplicates='drop')
            qcut_values = {d_qcut[i][j] for j in range(0, len(d_qcut[i]))}
            while len(qcut_values) < nc-1:
                qcut_n += 1
                print "\tqcut_n", qcut_n
                d_qcut[i] = pandas.qcut(data[i], qcut_n, duplicates='drop')
                qcut_values = {d_qcut[i][j] for j in range(0, len(d_qcut[i]))}
            #d = [str(d_qcut[i][j]).replace(',','->') for j in range(0, len(d_qcut[i]))]
            d = [str(j).replace(',','->') for j in qcut_values] #qcut_values[j]) for j in range(0, len(qcut_values))]
            print "\t" + (",".join(d))
            pickle.dump(d_qcut[i], open(qcut_pfn,'wb'))

        # check that the array of binned values has the same length as the input

        if len(d_qcut[i]) != n_rows:
            print "len(d_qcut)", len(d_qcut[i]), "n_rows", n_rows
            print "d_qcut", d_qcut[i]
            err("len(d_qcut) != n_rows")

        data[i] = [str(j).replace(',','->') for j in d_qcut[i]]

        if len(data[i]) != n_rows:
            err("problem must be right above this line")


ofn = in_f + "_csv_bin.csv"
o_f = open(ofn, "wb")
if not o_f:
    error("failed to open output file: " + ofn)

o_f.write(",".join(fields))

# check that the columnar variable has appropriate dimensions
if len(data) != n_fields:
    print "len(data)", len(data), "n_fields", n_fields
    err("columnar representation length should be: n_fields")

# check that the columnar variable isn't ragged
for j in range(0, n_fields):
    if len(data[j]) != n_rows:
        print "\n\tj", j, "len(data[j])", len(data[j]), "n_rows", n_rows
        err("len(data[j]) != n_rows")

# for each row
for j in range(0, n_rows):
    # NEED TO FIX THIS:

    datarow = [ str(data[0][j]) ]
    for i in range(1, n_fields):
        datarow.append(str(data[i][j]))
    o_f.write("\n" + ",".join(datarow))
o_f.close()