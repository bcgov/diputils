from misc import *
#20201113: revised from 2019 01 09: paste two tables together left-right: assert last col. matches
import time; t = time.time(); tt = time.time(); ttt = None;
if len(args) < 3:
    err("simple_join [input file 1] [input file 2] [optional param to skip checking]" +
        "# paste two tables together left-right: assert last col matches?")
fn1 = args[1] # "CB_STULVLCB_FT_SCHLSTUD_VWD_LK.csv_slice.csv_flatten.csv"
fn2 = args[2] # "CB_STULVLCB_FT_SCHLSTUD_VWD_LK.csv_slice.csv_revmod_flatten.csv"
ofn = fn1 + "_join.csv"; of = open(ofn, "wb")
s_f_i = -1


check = len(args) > 3 # enable mysterious special function for catting (left right) together stuff with same header!
f1 = open(fn1); line1 = f1.readline().strip().lower()
fields1 = line1.split(","); n_f1 = len(fields1)

f2 = open(fn2); line2 = f2.readline().strip().lower()
fields2 = line2.split(","); n_f2 = len(fields2)

if check and line1 != line2:
    err("input headers don't match")


if check:
    for i in range(0, len(fields2)):
        fields2[i] = "2"+fields2[i]
        if fields2[i] == 'studyid':
            s_f_i = i

of.write(",".join(fields1)); of.write(",")
of.write(",".join(fields2)); of.write("\n"); ci = 0
while True:
    line1 = f1.readline();  line2 = f2.readline()
    if not line2: break
    if not line2: break
    line1 = line1.rstrip(); line2 = line2.rstrip()
    w1 = line1.split(","); w2 = line2.split(",")
    if check and w1[s_f_i] != w2[s_f_i]:
        err("mismatch")

    if len(w1) != n_f1:
        err("")

    of.write(",".join(w1)); of.write(",")
    of.write(",".join(w2)); of.write("\n")

    ci += 1
    if ci % 10000 == 0:
        ttt = tt
        tt = time.time()
        print ci/1000, "1/2 k, S/10 k: ", tt-ttt
of.close()
f1.close()
f2.close()
