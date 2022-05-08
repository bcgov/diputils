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
'''20190709 produce a concatenated csv file where the inputs have some col's in comon
Obviously headers are expected for the CSV files.

Note: equivalent col. names are expected to possibly differ with respect to a prefix:

    e.g. PC.STUDYID is considered equivalent to DE.STUDYID

Concatenated table will contain source table name as a new field?'''
import os
import sys
import time
from misc import *

ofn = "csv_cat_common_fields.csv"
if os.path.exists(ofn):
    err("output file already exists: " + ofn +
        "\n\t need to delete it if you want to run this")

args = sys.argv
if len(args) < 3:
    err("usage:\n\t" +
        "csv_cat_common_fields.py" +
        " [csv file 1]" +
        " [csv file 2]" +
        " .. [csv file n]")

files, hdr, f_i_i, i_f_i, i_sf_i = args[1:], [], {}, {}, {}
# check files exist and have .csv filename extension
for i in range(0, len(files)):
    fn = files[i]
    if not os.path.exists(fn):
        err("input file not found: " + fn)
    ext = fn.split(".")[-1]
    #if ext != "csv":
    #    err("input file required to be csv: " + fn)
    f = open(fn)
    hdr.append(f.readline().strip().split(","))
    line1 = f.readline().strip().split(",")

    # basic data consistency check
    if len(hdr[i]) != len(line1):
        err("consistency check failed for file: " + fn +
            "unexpected number of fields line 1")

    # map field names to positions (this file) and vice versa
    f_i, i_f, i_sf = {}, {}, {}
    for j in range(0, len(hdr[i])):
        fn_j = hdr[i][j]
        f_i[fn_j], i_f[j] = j, fn_j
    # print f_i
    # print i_f

    # assert field names have no more than one dot ".":
    for j in i_f:
        if len(i_f[j].split(".")) > 2:
            err("field name: " + i_f[j] + " included more than one period " +
                "for file: " + fn)

    # determine simplified field name to match on-- also appears in end product
    i_sf = {j: i_f[j].split(".")[-1].strip('*').lower() for j in i_f}
    # print i_sf

    # assert unique field-name-simplification result
    if len(i_sf) != len(i_f):
        err("field simplification produced non-unique result:\n" +
            "\tinput field name list:\n\t" + str(i_f) +
            "\n\tnew field name list:\n\t" + str(i_sf))

    f_i_i[i], i_f_i[i], i_sf_i[i] = f_i, i_f, i_sf

match_fields =[]
for i in range(1, len(files)):
    f_i, i_f, i_sf = f_i_i[i], i_f_i[i], i_sf_i[i]
    f_i_, i_f_, i_sf_ = f_i_i[i-1], i_f_i[i-1], i_sf_i[i-1]
    i_sf_v = i_sf_.values()
    if i == 1:
        # print i_f
        # print i_f_
        for j in range(0, len(i_f)):
            if i_sf[j] in i_sf_v:
                match_fields.append(i_sf[j])
        print len(match_fields), match_fields
    else:
        keep, i_sf_v = [], i_sf.values()
        for mf in match_fields:
            if mf in i_sf_v:
                keep.append(mf)
        print len(keep), keep
        match_fields = keep

if len(match_fields) < 1:
    err("failed to find any fields in common, among input files")

# do the concatenation
f = open(ofn, "wb")

# write the header
f.write((",").join(match_fields))

# total file size:
total_f_size = 0
for i in range(0, len(files)):
    total_f_size += os.stat(files[i]).st_size

cumulative_f_size, t_0 = 0, time.time()

# process input file-by-file and retain common cols only
for i in range(0, len(files)):
    # retrive
    fn, i_sf = files[i], i_sf_i[i]
    sf_i = {i_sf[j]: j for j in i_sf} # today's learn: in python a set is a dictionary without values
    # print i, fn, len(sf_i), sf_i

    f_size = os.stat(fn).st_size

    # field-positions to be written, this file
    i_use = []
    for j in range(0, len(match_fields)):
        mf = match_fields[j]
        i_use.append(sf_i[mf]) # list of indices to be selected

    # sanity check
    if len(i_use) != len(match_fields):
        err("len(i_use) != len(match_fields)")

    in_f = open(fn)
    if not in_f: err("failed to open input file: " + fn)

    line = in_f.readline() # header
    ci = 0
    ci_last, t_last, c_f_last = None, None, None

    # actual activity of program is below this line:

    while True:
        line = in_f.readline() # read a line of the file
        if not line: break # exit read loop if end-of-file
        words = line.strip().split(',')
        f.write('\n' + ','.join([words[j] for j in i_use]))

        # below this line is just the progress bar...
        if ci % 500000 == 0:
            t = time.time()
            c_f = in_f.tell() + cumulative_f_size
            if ci_last and t_last and c_f_last:
                ds = c_f - c_f_last # data increment (bytes)
                dt = t - t_last
                bytes_per_sec, bytes_rem = ds / dt, total_f_size - c_f
                eta = bytes_rem / bytes_per_sec
                minutes = round(eta / 60., 2) # hours = round(eta/(60. * 60), 2)
                print fn.split('.')[0], '%', round(100.* c_f / total_f_size, 2), " t(s): ", round(t - t_0, 2), ' eta: ', round(eta, 2), ' mins: ', minutes # , 'hours: ', hours
            ci_last, t_last, c_f_last = ci, t, c_f
        ci += 1
    in_f.close()

    cumulative_f_size += f_size
# close output file
f.close()
print "done"
