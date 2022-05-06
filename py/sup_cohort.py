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
'''attempt at full data integration or approaching it'''
import os
import sys
import pickle
from misc import *
debug = False
recent_datfile_names = {}

args = sys.argv
if len(args) < 2:
    print("warning: delete local intermediary files if cohort has changed")
    err("sup_cohort.py:\n\tusage [cohort file]")
cohort_file_name = args[1]

# make sure data dictionary files are listed
if not os.path.exists("dd"):
    run("dd_list")
else:
    print("data dictionaries already listed")

if not os.path.exists("recent_datfile_names.p"):
    run("df_list")
else:
    print("data files already listed")
[recent_datfile_names] = pickle.load(open("recent_datfile_names.p"))

dd_files = {}
row_counts = {}
fn_has_studyid = {}

def cleanup(fn):
    if os.path.exists(fn):
        run("rm -f " + fn)

for f in sorted(recent_datfile_names.keys()): #recent_datfile_names:
    fn = recent_datfile_names[f] #fn in datafiles:
    #fn = fn[1] # file name (fn[0] is file size)
    fn = os.path.abspath(fn).strip()
    file_name = fn.split(os.path.sep)[-1]
    dat_file_name = file_name[0:-3]
    dat_file_ext = dat_file_name.split(".")[-1]
    dd_file_name = dat_file_name + ".dd"
    rc_file = dat_file_name + ".rc"
    slice_file = dat_file_name + "_dd_sliceapply_cohort.csv"
    select_file = dat_file_name + "_select-" + cohort_file_name + ".csv"

    print dat_file_name
    print "\tgz file", fn
    print "\tgzfile short", file_name
    print "\tdatfile short", dat_file_name
    print "\tdatfile ext", dat_file_ext
    print "\tddfile fn", dd_file_name
    print "\trecordcount file", rc_file
    print "\tslice file", slice_file
    print "\tselect file", select_file

    #raw_input("press any key to continue..")

    if os.path.exists(dat_file_name + "_no-studyid"):
        print "\tno studyid col this file. skipping.."
        continue

    no_records_for_cohort_this_data_file = False
    if os.path.exists(rc_file):
        # find out how many rows were sliced out for cohort, this file..
        rc = open(rc_file).read().strip().split("\n")[1].split(",")[0]
        if int(rc) < 2:
            no_records_for_cohort_this_data_file = True
        else:
            row_counts[fn] = rc
            print "\talready sliced. skipping.."
            continue

    if os.path.exists(select_file):
        print "\talready sliced. skipping.."
        continue

    if no_records_for_cohort_this_data_file:
        print "\tno records this file. skipping.."
        cleanup(dat_file_name)
        continue

    if os.path.exists(dd_file_name):
        if open(dd_file_name).read().strip() == "":
            print "\tno dd found this file. skipping.."
            cleanup(dat_file_name)
            continue

    # make a local copy of the file if it doesn't exist
    if not os.path.exists(file_name):
        run("cp " + fn + " " + file_name)

    # unzip the file
    if not os.path.exists(dat_file_name):
        run("unzp " + file_name)

    # need to check datfile_name counts!

    if not os.path.exists(dat_file_name):
        err("couldn't find dat file after unzipping")

    if os.path.exists(file_name):
        run("rm -f " + file_name)

    if dat_file_name[-4:] == ".csv": # data provided as CSV:
        if os.path.exists(slice_file):
            print "slice file already exists. skipping.."
            cleanup(dat_file_name)
            continue

        total_record_count = int(os.popen("lc " + dat_file_name).read().strip()) - 1

        fields = os.popen("fields " + dat_file_name).read().strip().split("\n")[1].strip().split(" ")
        fields = [x.lower() for x in fields]
        fields = [x.split('.')[-1] for x in fields]
        print "fields", fields

        if not (('studyid' in fields) or ('studyid1' in fields) or ('studyid2' in fields) or ('study-id' in fields)):
            print "\tno studyid record found this file. skipping.."
            fn_has_studyid[fn] = False
            open(dat_file_name + "_no-studyid", "wb").write(" ")
            cleanup(dat_file_name)
            continue

        studyid_field = None
        for my_f in fields:
            if my_f == 'studyid' or my_f =='studyid1' or my_f =='studyid2' or my_f == 'study-id':
                studyid_field = my_f

        select_file = dat_file_name + "_select-" + cohort_file_name + ".csv"
        cohort_data = open(cohort_file_name).read().strip().split("\n")
        cohort_size = len(cohort_data) - 1

        if cohort_size > 1:
            # multi-pattern grep
            run("csv_select_noexclude " + cohort_file_name + " " + studyid_field + " " + dat_file_name)
        else:
            # do a fast grep for single pattern
            my_id = cohort_data[1].strip()
            run("csv_grep " + my_id + " " + dat_file_name)
            tmpf = dat_file_name + "_grep_" + my_id + ".csv"
            run("mv -v " + tmpf + " " + select_file)

        if not os.path.exists(select_file):
            err("couldn't find output from csv_select")
        records_selected = int(os.popen("lc " + select_file).read().strip()) - 1
        open(rc_file, "wb").write("n_records_sliced,n_records_total\n" + str(records_selected) + "," + str(total_record_count))
        if records_selected > 0:
            pass
        else:
            run("rm -f " + select_file)
    else:
        # match data dictionary
        if not os.path.exists(dd_file_name):
            run("dd_match_data_file " + dat_file_name)

        if not os.path.exists(dd_file_name):
            err("could not find dd filename file: " + dd_file_name)

        fields = os.popen("dd_fields " + open(dd_file_name).read().strip()).read().strip().split("\n")[-1].split(" ")
        fields = [x.lower() for x in fields]
        fields = [x.split('.')[-1] for x in fields]

        if not (('studyid' in fields) or ('studyid1' in fields) or ('studyid2' in fields) or ('study-id' in fields)):
            print "\tno studyid record found this file. skipping.."
            fn_has_studyid[fn] = False
            open(dat_file_name + "_no-studyid", "wb").write(" ")

        else:
            fn_has_studyid[fn] = True
            # this produces the .rc variable
            run("dd_sliceapply_all " + dat_file_name + " " + cohort_file_name)

    if os.path.exists(rc_file):
        rc = int(open(rc_file).read().strip().split("\n")[1].split(",")[0])
        if rc == 0:
            no_records_for_cohort_this_data_file = True

    if no_records_for_cohort_this_data_file:
        run("rm -f " + slice_file)

    # datfile work happens before here..

    if os.path.exists(dat_file_name):
        run("rm -f " + dat_file_name)
