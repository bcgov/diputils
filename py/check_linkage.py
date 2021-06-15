''' 2019/01/20 this file was for a counting analysis of education data'''
import os
import sys
import csv
from misc import *
import time; t = time.time(); print t
csv.register_dialect('my',
                     delimiter=",",
                     quoting=csv.QUOTE_ALL,
                     skipinitialspace=True)

infile = "CB_STULVLCB..*" # insert real file name here

f, ci, f_names, n_f, fields = open(infile), 0, None, 0, None
tt = time.time()
ttt = None

special = {}
gender = {}
ids = []

while True:
    line = f.readline()
    if not line: break
    line = line.strip()
    if ci == 0:
        f_names = line.split(",")
        print f_names
        n_f, fields = len(f_names), ",".join(f_names)
        # write out header
        #of.write(",".join(f_names) + "\n")
    else:
        w = line.split(",")
        if len(w) != n_f:
            err(str(len(w)) + " " + str(n_f))
        # write out line
        if w[-1]!=NULL_STUDY_ID:
            if (w[0][0:3]).lower() != 'non':
                special[w[-1]] = w[0]
            gender[w[-1]] = w[1]
            if not w[-1] in ids:
                ids.append(w[-1])
    ci += 1
    if ci % 10000 == 0:
        ttt = tt
        tt = time.time()
        print ci/1000, "k, S/k: ", tt-ttt
print "done"
print "  ", int((ci / (time.time() - t))/1000.), "K lines per sec"


gender_count = {}
special_count = {}
special_count_m = {}
special_count_f = {}
mcount, fcount, scount, scountm, scountf = 0,0,0,0,0
for i in ids:
    mygender = gender[i]
    if i in special:
        scount += 1
        specialcode = special[i]
        if not specialcode in special_count:
            special_count[specialcode] =0
        special_count[specialcode] += 1
        if mygender=='M':
            mcount += 1
            if not specialcode in special_count_m:
                special_count_m[specialcode] =0
            special_count_m[specialcode] += 1
            scountm += 1
        if mygender=='F':
            fcount += 1
            if not specialcode in special_count_f:
                special_count_f[specialcode] =0
            special_count_f[specialcode] += 1
            scountf +=1
    if not mygender in gender_count:
        gender_count[mygender] =0
    gender_count[mygender] += 1


print "mcount", mcount
print "fcount", fcount
print "scount", scount
print "scountm", scountm
print "scountf", scountf
print "gender_count", gender_count
print "special_count", special_count
print "special_count_m", special_count_m
print "special_count_f", special_count_f
