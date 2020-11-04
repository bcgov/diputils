# 2019/01/07 slice csv with header. nested commas tolerated!
import os
import sys
import csv
from misc import *
import time; t = time.time(); print(t)
csv.register_dialect('my',
                     delimiter=",",
                     quoting=csv.QUOTE_ALL,
                     skipinitialspace=True)

#infile = "CB_STULVLCB_FT_SCHLSTUD_VWD_LK.csv"
#if infile == "CB_STULVLCB_FT_SCHLSTUD_VWD_LK.csv":
#    keep = ['GENDER',
#            'SPECIAL_NEED_THIS_COLL',
#            'studyid']

infile = sys.argv[1]
keep = sys.argv[2:]

keep_i = []
outfile = infile+"_slice.csv"; of = open(outfile, "wb")
f, ci, f_names, n_f, fields = open(infile), 0, None, 0, None
tt = time.time()
ttt = None
while True:
    line = f.readline()
    if not line:
        break
    line = line.strip()
    if ci == 0:
        f_names = line.split(","); print(f_names)
        n_f, fields = len(f_names), ",".join(f_names)
        for i in range(0, len(f_names)):
            if f_names[i] in keep:
                keep_i.append(i)
        # write out sliced header
        for i in range(0, len(keep_i)):
            if i>0:
                of.write(",")
            of.write(f_names[keep_i[i]])
        of.write("\n")
    else:
        w = line.split(",")
        if len(w) != n_f:
            tmp_fn = "ts.csv"
            g=open(tmp_fn,"wb"); g.write(fields+"\n"+line); g.close()
            reader = csv.reader(open(tmp_fn), dialect='my')
            hdr, lin = reader
            w = lin
        if len(w) != n_f:
            err("")
        # write out sliced line
        outl = []
        for i in range(0, len(keep_i)):
            outl.append(w[keep_i[i]])
        outs = ",".join(outl)
        #print w
        #print(outs)
        of.write(outs+"\n")
    ci += 1
    if ci % 1000 == 0:
        ttt = tt
        tt = time.time()
        print( ci/1000, "k, S/k: ", tt-ttt)
print("done")
print("  ", int((ci / (time.time() - t))/1000.), "K lines per sec")
f.close(); of.close()
