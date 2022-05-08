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

'''20190315 take pharmanet dispensations:
look for earliest dispense date of drug type, as well as dispense frequency

Output has same data, with freq and min_srv_date added'''
import os
import sys
import time
from misc import*

def expected(f_name, lookup):
    if f_name not in lookup:
        err("expected field: " + str(f_name))

def freq_min(fn):
    f = open(fn)
    if f == None:
        err("failed to open file: " + str(fn))

    fields = f.readline().strip().split(",")
    print fields
    lookup = {}
    for i in range(0, len(fields)):
        lookup[fields[i].lower()] = i

    print "  ", lookup
    for i in ["studyid", "hp.din_pin"]:
        expected(i, lookup)


    #mindate, freq = f(studyid, hp.din_pin)
    dat = {}

    ci = 0
    f_size = os.stat(fn).st_size

    tt = ttt = t_0 = time.time()
    while True:
        words = None
        try:
            words = f.readline().strip().split(",")
        except:
            break
        if words == ['']:
            continue
        for i in range(0, len(words)):
            words[i] = words[i].strip().lower()

        if len(words) != len(fields):
            print words
            err("wrong number of fields, check csv file")

        key = words[lookup["studyid"]] + "," + words[lookup["hp.gen_drug"]]
        if key not in dat:
            # freq = 1, min(serv_date) = serve_date
            dat[key] = [1, words[lookup["srv_date"]]]
        else:
            freq, min_serv_date = dat[key]
            freq += 1
            date = words[lookup["srv_date"]]
            min_serv_date = min_serv_date if min_serv_date < date else date
            dat[key] = [freq, min_serv_date]

        ci += 1
        if ci % 100000 == 0:
            ttt = tt
            tt = time.time()
            print "file", " %: ", 100. * (float(f.tell()) / float(f_size)), " MB/s:", (float(f.tell()) / 1000000.) / (tt- t_0)#

    f.close()
    f = open(fn)

    if f is None:
        err("failed to open file: " + str(fn))

    print "  +r " + fn
    g_n = fn + "_freq-min.csv"
    print " +w " + g_n
    g = open(g_n, "wb")

    print "  +w " + g_n

    if g is None:
        err("failed to open file: " + str(g_n))

    fields.append("freq")
    fields.append("min_srv_date")
    g.write(",".join(fields))
    f.readline() # fields

    ci = 0
    while True:
        line, words = None, None
        try:
            line = f.readline().strip()
        except:
            break
        if line == "":
            continue
        words = line.split(",")

        for i in range(0, len(words)):
            words[i] = words[i].strip().lower()

        key = words[lookup["studyid"]] + "," + words[lookup["hp.gen_drug"]]
        if key not in dat:
            err("key should have been found")
        freq, min_serv_date = dat[key]
        g.write("\n" + line + "," + str(freq) + "," + str(min_serv_date))

        ci += 1
        if ci % 100000 == 0:
            ttt = tt
            tt = time.time()
            print "file", " %: ", 100. * (float(f.tell()) / float(f_size)), " MB/s:", (float(f.tell()) / 1000000.) / (tt- t_0)#
    f.close()
    g.close()

freq_min("dsp_rpt.dat_slice.csv_select-STUDY.csv_lookup.csv")
freq_min("dsp_rpt.dat_slice.csv_select-CONTROL.csv_lookup.csv")
