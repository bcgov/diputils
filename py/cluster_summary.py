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
'''cluster_summary.py:
    this code goes with kmeans.py! '''
import math
from misc import *
import numpy as np

if len(args) < 2:
    err("produce cluster summaries" +
        "\n\tcluster_summary [input file.csv]" +
        "\n\t- within cluster sum of squares" +
        "\n\t- data by class: separate files")

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

f_i = {fields[i]: i for i in range(0, len(fields))}
i_f = {i: fields[i] for i in range(0, len(fields))}

# group data by class
rows_by_class = {}
for i in range(0, n_rows):
    data_row = []
    w = lines[i].strip().split(',')
    if len(w) != n_fields:
        err("unexpected number of fields")
    for j in range(0, n_fields):
        d = float(w[j])
        data_row.append(d)
    ci =  int(data_row[f_i['cluster_label']])
    if ci not in rows_by_class:
        rows_by_class[ci] = []
    rows_by_class[ci].append(data_row)


# calculate cluster centres and normalized wcss (within cluster sum of squares)
# cluster centres

cluster_centres = {}
for k in rows_by_class:
    cluster_centres[k] = np.zeros(n_fields) # init to zero

    for row in rows_by_class[k]:
        cluster_centres[k] += np.array(row)

for k in rows_by_class:
    cluster_centres[k] /= float(len(rows_by_class[k]))

centres_fn = in_f + "_kmeans_centres.csv"
c_f = open(centres_fn, "wb")
if not c_f:
    err("failed to open output file: " + c_f)

c_f.write(','.join(fields))
for k in rows_by_class:
    c_f.write("\n" + str(cluster_centres[k][0]))
    for i in range(1, n_fields):
        c_f.write("," + str(cluster_centres[k][i]))
c_f.write("\n")


for i in range(0, n_fields -1):
    d = []
    for k in rows_by_class:
        d.append(cluster_centres[k][i])

    c_f.write(str(np.std(np.array(d))) + ",")
c_f.write("stdv")
c_f.close()

run("transpose " + centres_fn)

# sort by standard deviation
run("csv_sort " + centres_fn + "_transpose.csv stdv kmeans_centres.csv_transpose.csv_sort.csv")
run("csv_to_html " + "kmeans_centres.csv_transpose.csv_sort.csv")

wcss_total, wcssn_total = 0., 0.
# wcss
wcss = {}
for k in rows_by_class:
    ss = 0.
    for i in range(0, len(rows_by_class[k])):
        d = [float(rows_by_class[k][i][j]) for j in range(0, n_fields - 1) ] # data includes cluster id..
        ss += math.pow(np.linalg.norm(cluster_centres[k][0:-1] - d, 2.), 2.) # 0:-1 since have to get rid of the part of the mean that is the cluster index

    # ss /= float(len(rows_by_class[k]))
    wcss[j] = ss
    wcss_total += ss
    wcssn_total +=  ss / float(len(rows_by_class[k]))
    print "k", k, "wcss", ss, "wcss/n", ss / float(len(rows_by_class[k])), "n", len(rows_by_class[k])

print "total_wcss", wcss_total
print "avg wcss/n", wcssn_total / float(len(rows_by_class.keys()))


# output data by class, separate files, and generate frequency tables
jobs = []
freq_files = []
for k in rows_by_class:
    print k, len(rows_by_class[k])
    ofn = in_f + "_class" + str(k) +".csv"
    o_f = open(ofn, 'wb')
    o_f.write(','.join(fields))

    for row in rows_by_class[k]:
        df = [str(row[i]) for i in range(0, len(row))]
        o_f.write('\n' + (','.join(df)))
    o_f.close()
    freq_file =  ofn + "_frequ.csv"
    jobs.append("count " + ofn + "; csv_sort " + freq_file + " frequency")
    freq_files.append(freq_file)

open("cluster_summary_jobfile.txt", "wb").write('\n'.join(jobs))

run("multicore cluster_summary_jobfile.txt")

o_f = open("cluster_summary_jft.csv", "wb")
if not o_f:
    err("failed to open output file")

jft = {}
classis = []
var_val_last = None
for f in freq_files:
    print "freq_file:", f
    f_f = open(f)
    if not f_f:
        err("failed to open file: " + str(f))

    classi = f.split(".csv_")[-2][5:]
    print "classi", classi
    if classi not in classis:
        classis.append(classi)

    hdr = f_f.readline().strip()
    if hdr != "variable,value,frequency":
        err("unexpected header")

    while True:
        line = f_f.readline()
        if not line:
            break
        w = line.strip().split(',')
        var_val = w[0] + ',' + w[1]
        freq = w[2]

        if var_val not in jft:
            jft[var_val] = {}
        jft[var_val][classi] = freq

        var_val_last = var_val
    f_f.close()

o_f.write("variable,value")

for var_val in jft:
    if var_val.split(",")[0] != "cluster_label":
        if len(jft[var_val].keys()) != len(freq_files):
            print var_val, jft[var_val]


for classi in classis:
    o_f.write(",freq" + classi)

o_f.write(",stdv")

for var_val in jft:
    if var_val.split(",")[0] != "cluster_label":
        freqs = []
        o_f.write("\n" + var_val)
        for classi in classis:
            if classi not in jft[var_val]:
                o_f.write(",0.0")
                freqs.append(float(0.0))
            else:
                d = jft[var_val][classi]
                o_f.write("," + d)
                freqs.append(float(d))
        o_f.write("," + str(np.std(np.array(freqs))))
        '''
        f_sum = 0
        for f in freqs:
            f_sum += f

        p = {f/f_sum for f in freqs}

        H = 0
        for p_i in p:
            if p_i > 0.:
                H += p_i * math.log(p_i)

        o_f.write("," + str(H))
        '''
o_f.close()

run("csv_sort cluster_summary_jft.csv stdv")
run("csv_to_html cluster_summary_jft.csv_sort.csv")
print "done"
print "still need wcss-- elbow"
print "agglom"
