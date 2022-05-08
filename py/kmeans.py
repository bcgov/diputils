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
Example use:
   kmeans.py columns_ash_wanted.csv_csv_bin.csv_csv_onehot.csv 11

Note: this script implements:
   Lloyd's algorithm

Comments:
  #don't use:
  #depno_grouping
  #empl_stat_pssg_detail
  #famtype_group
'''
#------------------------------------------------------------#
# file: kmeans.py                                            #
#                                                            #
# description:                                               #
#   takes a CSV file and writes cluster labels to binary..   #
#                                                            #
# currently only floating-point values are supported         #
# usage:                                                     #
#       ./kmeans.py [inputFileName ] [k ]                    #
#------------------------------------------------------------#
import os
import sys
import math
import time
import numpy
import struct
import random
from misc import *
random.seed(time.clock()) # init random seed

if len(args) < 2:
    err("kmeans.py: usage:\n\t./kmeans [infile] [k]\n");

in_fn = args[1].strip();
if not os.path.exists(in_fn):
    err("Error: could not open input file :" + str(in_fn))

#------------------------------------------------------------#
#     data reading section.                                  #
#------------------------------------------------------------#

lines = open(in_fn).readlines()
field_names = lines[0].strip().split(',')
f_i = {field_names[i]: i for i in range(0, len(field_names))}
i_f = {i: field_names[i] for i in range(0, len(field_names))}

read_seeds = False
if 'cluster_label' in field_names:
    read_seeds = True
    if f_i['cluster_label'] != len(field_names) - 1:
        err('cluster_label field required to be at end of vector')

n_col = len(field_names)
n_fields = n_col - 1 if read_seeds else n_col #how many fields?
lines = lines[1:]  # data rows only no-header
nRecords = len(lines) # how many measurement vectors?


# DATA VARIABLE INIT
# init. a numpy format container for data
data = numpy.empty([nRecords, n_fields])  #numpy data format.
if( data.shape[0] != nRecords or data.shape[1] != n_fields):
    print('Error: data.shape != nRecords, n_fields')
    sys.exit(1)

#------------------------------------------------------------#
#     kmeans clustering section.. cluster variable setup..   #
#------------------------------------------------------------#
nClust = 5  # default number of clusters to initialize..
maxIter = 100  #number of iterations for cluster optimization..
try:
  nClust = int(args[2])
except:
  nClust = 5

currentLabel = [ ]  # current label (cluster index) for a point...
current_label_max = None

#------------------------------------------------------------#
#     check data integrity while populating the container..  #
#------------------------------------------------------------#

nNan = 0;
for i in range(0, len(lines)):

    row = lines[i].strip().split(',')
    if len(row) != n_col:
        err(str(row) + 'Error: row length ' + str(len(row)) + '!=' + str(n_col))
    my_label = None
    try:
        my_label = int(row[f_i['cluster_label']])
        current_label_max = my_label if (current_label_max is None) else (my_label if my_label > current_label_max else current_label_max)
    except:
        my_label = -1
    currentLabel.append(my_label)

    for j in range(0, n_fields):
        dataValue = row[j].strip()
        if dataValue == 'nan':
            Nan += 1
            data[i, j] = float('nan')

        # try to interpret field as numeric
        try:
            data[i, j] = float(dataValue)
        except:
            nNan += 1
            data[i, j] = float('nan')
            print('Warning: nan at row i=' + str(i + 1) + ' (1-indexed), col=' + str(j + 1))

if nNan > 0:
    print('Warning: ' + str(nNan) + ' instances-of-NaN detected')

print('There are ' + str(nRecords) + ' measurement vectors')
print "current_label_max", current_label_max

if not current_label_max is None:
    nClust = current_label_max + 1

# SET UP CURRENT LABELS AND N CLUST, BASED ON IF WE GOT SEEDS YET OR NOT
clusterCentres = [ ] # index of data record representative of a cluster
for i in range(0, nClust):
  clusterCentres.append(-1)

# (key,value)=(cluster index, list of members (pt. indices i))
clusterMembers = { }

#------------------------------------------------------------#
#     find the max and min of the individual features..      #
#------------------------------------------------------------#

dataMax, dataMin = numpy.zeros(n_fields), numpy.zeros(n_fields)

for j in range(0, n_fields):
    dataMax[j] = sys.float_info.min
    dataMin[j] = sys.float_info.max
    for i in range(0, nRecords):
        dij = data[i, j]
        if dij > dataMax[j]:
            dataMax[j] = dij
        if dij < dataMin[j]:
            dataMin[j] = dij

dataScale = numpy.zeros(n_fields)

for j in range(0, n_fields):
    print('var: ' + field_names[j] + ' min ' + str(dataMin[j]) + ' max ' + str(dataMax[j]))
    mM = dataMax[j] - dataMin[j]
    dataScale[j] = 1. / (mM)
    dataScale[j], dataMin[j] = 1., 0.

#------------------------------------------------------------#
#     find the 'most central' element of a cluster...        #
#------------------------------------------------------------#

def mostCentralElementForClusterJ(j):
    global data, clusterMembers
    nRecords, n_fields = data.shape
    nObs = 0.
    myMean = [0. for i in range(0, n_fields)]
    myMembers = clusterMembers[j]
    nMembers  = len(myMembers)
    if nMembers == 0:
        print('Warning: no members in class ' + str(j))
        return -1
    for i in range(0,nMembers):
        myMember = myMembers[i]
        for m in range(0, n_fields):
            myMean[m] += (data[myMember, m] - dataMin[m]) * (dataScale[m])
        nObs += 1.

    for m in range(0, n_fields):
        myMean[m] = myMean[m] / nObs

    #find the member closest to the mean..
    #feedback between elements, vs. representatives..
    assignI = 0
    minD = math.sqrt(math.sqrt(math.sqrt(sys.float_info.max)))
    minI = float('nan')
    for i in range(0, nMembers):
        d = 0.
        myMember = myMembers[i]
        for m in range(0, n_fields):
            d += math.pow(myMean[m] - ((data[myMember, m] - dataMin[m]) * dataScale[m]), 2.)
        d = math.sqrt(d)
        if(assignI == 0 or (d < minD and not(math.isnan(d)))):
            minD = d
            minI = myMember
            assignI += 1
    #assign the 'most central' element as the representative..
    if minI == float('nan'):
        print('Error: no centre rep for clusterJ: j=' + str(j))
        sys.exit(1)
    return(minI)

#------------------------------------------------------------#
#     function to find the nearest cluster centre, relative  #
#       to a given observation                               #
#------------------------------------------------------------#

def labelOfCentreNearestToAnObservationAtIndexI(i):
    global data, clusterCentres
    nRecords, n_fields = data.shape
    nClust = len(clusterCentres)
    minD = math.sqrt(math.sqrt( math.sqrt( sys.float_info.max)))
    minI = -1
    for j in range(0, nClust): #don't consider empty clusters..
        if(clusterCentres[j] == -1): continue;
        d = float(0.)
        centreI = clusterCentres[j]
        for k in range(0, n_fields):
            dd = (data[centreI, k]  - data[i, k]) * (dataScale[k])
            d += dd * dd;
        d = math.sqrt(d)
        if j == 0 or (d < minD and not(math.isnan(d))):
            minI = j
            minD = d
    if(minI == float('nan') or str(minI) == 'nan'):
        print('Error: no centre nearest to obs. i=' + str(i))
        sys.exit(1)
    return minI

#------------------------------------------------------------#
#     seed the clustering...                                 #
#------------------------------------------------------------#
if not read_seeds:
    #seed the simulation..
    for i in range(0, nRecords): #randomly label the points:
        currentLabel[i] =random.randint(0, nClust - 1)

'''
def writeLabels():
  global currentLabel
  f=open("./.label.bin","wb");
  for i in range(0, len(currentLabel)):
    d = float(currentLabel[i])
    s = struct.pack('f', d)
    f.write(s)
  f.close()
'''

#------------------------------------------------------------#
#   run the (unsupervised) algorithm...                      #
#------------------------------------------------------------#

lastClusterCentres = str(clusterCentres);

#for a number of iterations:
for k in range(0, maxIter):
    print('-----------------------------------------------------------------')
    print "iter", k
    #calculate class membership lists:
    clusterMembers={}
    for i in range(0, nClust):
        clusterMembers[i] = []
    for i in range(0, nRecords):
        myLabel = currentLabel[i]
        clusterMembers[myLabel].append(i);
    # print('1) clusterMembers: ' + str(clusterMembers))

    #for each class, find the 'most central' element..
    for j in range(0, nClust):
        clusterCentres[j] = mostCentralElementForClusterJ(j);
        if(clusterCentres[j] =='nan' or clusterCentres[j] == float('nan')):
            print('Error: current label is nan for clusterCentre.');
            sys.exit(1)
    print('2) cluster representatives (element indices):' + str(clusterCentres))
    if(str(clusterCentres) == lastClusterCentres):
        print('cluster centres stationary after ' + str(k + 1) + ' updates. done.')
        # writeLabels()
        break
    lastClusterCentres = str(clusterCentres)
    for i in range(0, nClust):
        print "\t|cluster_" + str(i) + "|=" + str(len(clusterMembers[i]))

    print "relabel.."
    #label a point in terms of the nearest 'cluster centre':
    for i in range(0, nRecords):
        newLabel = labelOfCentreNearestToAnObservationAtIndexI(i)
        if(str(newLabel) == 'nan' or newLabel == float('nan')):
            print('Error: current label is nan: ' + str(i))
            sys.exit(1)
        currentLabel[i] = newLabel
    #print('1) currentLabels:' + str(currentLabel))
    for i in range(0, nClust):
        print "\t|cluster_" + str(i) + "|=" + str(len(clusterMembers[i]))

    # output results at each iteration

    ofn = in_fn + "_kmeans_iter" + str(k) + ".csv"
    o_f = open(ofn, 'wb')
    print "+w", ofn
    if not o_f:
        err('failed to open output file')

    if k==0:
        field_names.append("cluster_label")
    o_f.write(','.join(field_names))

    for i in range(0, nRecords):
        datarow = []
        for k in range(0, n_fields):
            d = data[i, k]
            datarow.append(str(d))
        lab = str(currentLabel[i])
        datarow.append(lab)
        o_f.write('\n' + (','.join(datarow)))
    o_f.close()

    print "nan_warnings" + str(nNan)
    print histo(currentLabel)

print "still need to output cluster centres"
print "need to calcluate wccs / n"
