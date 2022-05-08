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
'''20190617 find an acceptable data dictionary (dd):
        for a given data file
'''
import os
import sys
from misc import *
from ansicolor import *
from filename_fuzzy_match import *
debug = False

if len(sys.argv) < 2:
    err("dd_match_data_file.py: find data dictionary for data file.\n" +
        "\tusage: dd_match_data_file [data file.dat]\n" +
        "Note: data dictionaries expected in folder dd/, produced by dd_list.py")

if not os.path.exists("dd") or not os.path.isdir("dd"):
    err("dd/ expected. Please run dd_list")

f = sys.argv[1]
if not os.path.exists(f) or not os.path.isfile(f):
    err("could not find input file: " + str(f))

fn = os.popen("cygpath -d " + f.strip()).read().strip()
print "data file: ", f
files = {}
dd_files = os.popen('find ./dd').readlines()
for d in dd_files:
    d = d.strip()
    if d[-4:] == "csv2":
        files[d] = True

datfiles = [f] #[fn]
matches = []

def chars_per_line(fn, datfiles):
    # use data dictionary file to predict number of characters per line, in a data file
    global matches
    if debug:
        print fn
    csv_l = open(fn).read().strip().split('\n')
    fields = csv_l[0].split(",")
    if fields[0].lower() != "start":
        if debug:
            print(fn + ", expected first field name: start: found: " + fields[0].lower())
        return -1
    if fields[1].lower() != "stop":
        if debug:
            print(fn + ", expected second field name: stop: found: " + fields[1].lower())
        return -1

    # for l in csv_l: print l.strip()
    #csv_l = csv_l[1:] # remove header and process
    if debug:
        print fn
        print "start, stop, length, total_len"
    total_len = 0
    for i in range(1, len(csv_l)):
        w = csv_l[i].strip().split(",")
        start = int(w[0])
        stop = int(w[1])
        length = stop - start + 1
        length2 = int(w[2])
        if length2 != length:
            err("field name: " + w[3].strip() + " length from dd: " + str(length2) + " vs stop - start + 1: " + str(length))
        total_len += length
        if debug:
            print "\t", start, stop, length, total_len

    print "dd=",fn, " nchars=", total_len, " flen: ", len(open(datfiles[0]).readline())
    had_match = False
    for i in range(0, len(datfiles)):
        line = open(datfiles[i]).readline()
        if len(line) == total_len:
            if len(matches) <= 1000: # <= 10
                print "\tmatch", datfiles[i]
                had_match = True
            matches.append([fn, len(line), total_len])
    if len(matches) != 1 and had_match:
        print "****** Warning: nonunique match", len(line), total_len

for d in files:
    chars_per_line(d, datfiles)

print "\n\n******* MATCHES: [file, len(line), len(line) predicted by file]"
for i in range(0, len(matches)):
    m = matches[i]
    print("\t(" + str(i+1) + ") " + str(m))

if len(matches) > 1:
    try:
        match_files = []
        for i in range(0, len(matches)):
            match_files.append(matches[i][0])
        m, mi = fuzzy_filename_match_i(os.path.abspath(f), match_files)
        match_i = matches[m]
        matches = [match_i]
    except:
        pass

    print "after fuzzy matching:"
    for i in range(0, len(matches)):
        m = matches[i]
        print("\t(" + str(i+1) + ") " + str(m))

# find a match!
match_use = None
if len(matches) == 1:
    match_use = 0
elif len(matches) == 0:
    print("error: failed to find data dictionary for: " + f) # open(f + ".dd", "wb").write("ERROR: failed to find data dictionary for: " + f)
else:
    while True:
        try:
            answer = input("please select one of the above matches for " + f + ": ")
            match_use = int(answer) - 1
            if match_use >=0 and match_use < len(matches):
                break
        except:
            print("please enter a number from 1 to however many matches there are")
    # err("unique dd match not found")
try:
    open(f + ".dd", "wb").write(matches[match_use][0])
except:
    open(f + ".dd", "wb").write("")
