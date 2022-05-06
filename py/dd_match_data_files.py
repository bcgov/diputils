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
'''20190214 dd_match.py:
    given a data dictionary (csv2),
        determine (e.g. hospital etc) data files:
            that match or could match'''
import os
import sys
import pickle
from misc import *

datfiles = None
data_files_list_file = "data_files_list.p"
try:
    print "attempting to restore data files list.."
    datfiles = pickle.load(open(data_files_list_file, "rb"))
except:
    print "finding data files.."
    data_dir = 'R:\\working\\extract'
    cmd = "find " + data_dir + ' -name "*.dat" -type f'
    datfiles = os.popen(cmd).read().strip().split('\n')
    for i in range(0, len(datfiles)):
        datfiles[i] = os.path.abspath(datfiles[i]).strip()
    datfiles = set(datfiles)
    datfiles = list(datfiles)
    pickle.dump(datfiles, open(data_files_list_file, 'wb'))

if not os.path.exists("dd_match_fields_selected_dd.txt"):
    err("please run dd_match_fields.py first")

lines = open("dd_match_fields_selected_dd.txt").read().strip().split("\n")

for f in lines:
    fn = os.popen("cygpath -d " + f.strip()).read().strip()
    print f, fn
    csv_l = open(fn).read().strip().split('\n')
    fields = csv_l[0].split(",")
    if fields[0].lower() != "start":
        err("csv2 file expected first field name: start")
    if fields[1].lower() != "stop":
        err("csv2 file expected second field name: stop")

    # for l in csv_l: print l.strip()
    csv_l = csv_l[1:] # remove header and process

    total_len = 0
    for i in range(0, len(csv_l)):
        w = csv_l[i].strip().split(",")
        start = int(w[0])
        stop = int(w[1])
        length = stop - start + 1
        total_len += length

    print "\tdata record length (chars)", total_len

    matches = []
    for i in range(0, len(datfiles)):
        line = open(datfiles[i]).readline()
        if len(line) == total_len:
            if len(matches) <= 1000: # <= 10
                print "\tmatch", datfiles[i]
            matches.append(datfiles[i])
    if len(matches) != 1:
        print "****** Warning: nonunique match"
