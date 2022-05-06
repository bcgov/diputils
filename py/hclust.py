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
'''hierarchical agglomerative clustering (csv format input expected)'''
import math
from misc import *

if len(args) < 3:
    err("hclust [csv input file] [n clusters desired]")

classes = [] # list of indices belonging to each class
n_clusters = int(args[2]) # desired number of clusters
in_fn = args[1] # input file
lines = open(in_fn).readlines() # the data
fields, lines = lines[0].strip().split(","), lines[1:]
n_records, n_fields = len(lines), len(fields)
data = [] # data converted to float format

# initializing each datum to own class
for i in range(0, len(lines)):
    w =  lines[i].strip().split(",")
    d = [float(w[j]) for j in range(0, len(w))]
    data.append(d)
    classes.append([i])

# write out data with cluster label added
def write_output():
    global in_fn, classes, it, fields, data
    ofn = in_fn + "_hclust_iter" + str(it) + ".csv"
    o_f = wopen(ofn, 'wb')
    if it == 0:
        fields.append("cluster_label")
    o_f.write(','.join(fields))
    for ci in range(0, len(classes)):
        for di in classes[ci]:
            out_lin = ','.join([str(d) for d in data[di]]) + ',' + str(ci)
            o_f.write(out_lin)
    o_f.close()

# euclidean distance function "complete linkage"
def dist(x, y):
    global data
    # calculate distance function between two sets (of vectors)
    d = 0.
    for xi in x: # iter over first set
        dx = data[xi]
        for yi in y: # iter over second set
            dy = data[yi]
            for i in range(0, len(dx)): # iter along vec 1
                dxi = dx[i]
                for j in range(0, len(dy)): # iter along vec 2
                    dd = dxi - dy[j]
                    d += (dd * dd)
    return d # should we normalize for size?

it = 0
while True:
    # keep merging until we reach the desired # of clusters
    if len(classes) <= n_clusters: break

    print "iter", it, "nclass", len(classes)
    d_min, i_min, j_min = None, None, None

    for i in range(0, len(classes)):
        print "iter", it, "i", i + 1, "of", len(classes)
        for j in range(i + 1, len(classes)):
            if j == i:
                continue # d == 0.
            d = dist(classes[i], classes[j])
            if d_min is None or d < d_min:
                d_min, i_min, j_min = d, i, j
    print "* d_min", d, "i_min", i, "j_min", j

    # merge
    for k in range(0, len(classes[j_min])):
        classes[i_min].append(classes[j_min][k])
    del classes[j_min]

    write_output()
    it += 1
print "n_classes", len(classes)
print "done"
