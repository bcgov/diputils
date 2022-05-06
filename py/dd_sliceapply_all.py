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
'''20190617 extract all fields from a fixed-width file, finding dd (data dictionary)
automagically!
'''
import os
import sys
from misc import *

msg = ("dd_sliceapply_all.py: extract all fields from a .dat file, choosing the data dictionary automatically.\n" +
       "usage:\n\tdd_sliceapply_all [dat file name]\nNote: dd/ directory expected in present working folder" +
       "usage:\n\tdd_sliceapply_all [dat file name] [cohort file (1-col csv with label studyid)]")

if len(args) >= 2:
    fn = sys.argv[1]
    ddn = fn + ".dd"

    if not exists("dd"):
        run("dd_list")

    if not os.path.exists(fn) or not os.path.isfile(fn):
        err("couldn't find input file: " + fn.strip())

    if not os.path.exists(ddn):
        run("dd_match_data_file " + fn)

    if not os.path.exists(ddn):
        err("data dictionary match not found")

    dd = open(ddn).read().strip()

    if not os.path.exists(dd):
        err("could not find dd file: " + dd.strip())

    fields = os.popen("dd_fields " + dd).read().strip().split("\n")[-1].split(" ")
    print "fields", fields

    if len(sys.argv) >= 3:
        cohort_file = sys.argv[2]
        if not os.path.exists(cohort_file):
            err("could not open cohort file: " + cohort_file)
        # this program builds .rc file:
        run("dd_slice_apply_cohort " + dd + " " + cohort_file + " " + fn.strip())
    else:
        run("dd_slice_apply " + dd + " " + fn.strip() + " " + (" ".join([f for f in fields if f.upper() != "LINEFEED"])))
    a = os.system("rm -f *exclude*") # remove this line
else:
    extract = []
    files = os.popen("ls -1 *.dat").read().strip().split()
    for f in files:
        f = f.strip()
        extract.append(f)

    f = open("./.dd_sliceapply_jobs.txt", "wb")
    for i in range(0, len(extract)):
        f.write("  dd_sliceapply_all " + extract[i] + "\n")
    f.close()

    run("cat ./.dd_sliceapply_jobs.txt")
    print(msg)
    raw_input("run the above jobs? press RETURN or ctrl-c to abort")

    run("multicore ./.dd_sliceapply_jobs.txt 4")
    # hardware limitation: memory channels
