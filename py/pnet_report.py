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

import os
import sys
from misc import *
start_year, end_year = 1980, 2025
run_jobs = True

unique_record_files = {}
unique_record_files_lc = {}
unique_studyid_count_files = {}
status_files = {}
bad_data_files = {}
reversal_counts = {}
total_counts = {}
veterinary_counts = {}

#================================================================
f = open("jobs.txt", "wb") # produce nonduplicate records
for i in range(start_year, end_year):
    fn = "pnet_" + str(i) + ".csv"
    if os.path.exists(fn):
        cmd = "unique " + fn
        of = fn + "_unique-_.csv"
        unique_record_files[i] = of
        if not os.path.exists(of):
            f.write(cmd + "\n")
            print cmd

f.close()
if run_jobs and open("jobs.txt").read().strip() != "":
    run("multicore jobs.txt 4") # use only four processors, to avoid RAM use

#================================================================
f = open("jobs.txt", "wb")
for fi in unique_record_files:
    fn = unique_record_files[fi]
    of = fn + "_lc"
    unique_record_files_lc[fi] = of
    if os.path.exists(fn):
        cmd = "lc " + fn + " > " + of
        if not os.path.exists(of):
            f.write(cmd + "\n")
            print cmd

f.close();
if run_jobs and open("jobs.txt").read().strip() != "":
    run("multicore jobs.txt")

#================================================================
f = open("jobs.txt", "wb")
# count studyid
for i in range(start_year, end_year):
    fn = "pnet_" + str(i) + ".csv"
    if os.path.exists(fn):
        cmd = "csv_count_unique_studyid " + fn
        of = fn + "_count_unique_studyid"
        unique_studyid_count_files[i] = of
        if not os.path.exists(of):
            f.write(cmd + "\n")
            print cmd

f.close()
if run_jobs and open("jobs.txt").read().strip() != "":
    run("multicore jobs.txt") # not same ram issue

#================================================================
# check for bad data
f = open("jobs.txt", "wb")
# count studyid
for i in range(start_year, end_year):
    fn = "pnet_" + str(i) + ".csv"
    if os.path.exists(fn):
        cmd = "pnet_check " + fn
        of1 = fn + "_status"
        of2 = fn + "_bad-data"
        status_files[i] = of1
        bad_data_files[i] = of2
        if not os.path.exists(of1) or not os.path.exists(of2):
            f.write(cmd + "\n")
            print cmd

f.close()
if run_jobs and open("jobs.txt").read().strip() != "":
    run("multicore jobs.txt") # not same ram issue

reversal_count, veterinary_count, total_count = {}, {}, {}
def exe(c):
    c = c.strip()
    exec("global total_count, veterinary_count, reversal_count; " + c)

for i in status_files:
    lines = open(status_files[i]).read().strip().split("\n")
    rev, vet, tot = lines[len(lines) - 3], lines[len(lines) - 2], lines[len(lines) - 1]
    if rev.split("=")[0].strip() == 'reversal_count' and len(rev.split(";")) == 1:
        exe(rev)
    if vet.split("=")[0].strip() == 'veterinary_count' and len(vet.split(";")) == 1:
        exe(vet)
    if tot.split("=")[0].strip() == 'total_count' and len(tot.split(";")) == 1:
        exe(tot)

    for j in reversal_count:
        if str(j.strip().strip('"')) != str(i):
            err("unexpected data")
        if i not in reversal_counts:
            reversal_counts[i] = 0
        reversal_counts[i] += reversal_count[str(i)]

    for j in veterinary_count:
        if str(j.strip().strip('"')) != str(i):
            err("unexpected data")
        if i not in veterinary_counts:
            veterinary_counts[i] = 0
        veterinary_counts[i] += veterinary_count[str(i)]

    for j in total_count:
        if str(j.strip().strip('"')) != str(i):
            err("unexpected data")
        if i not in total_counts:
            total_counts[i] = 0
        total_counts[i] += total_count[str(i)]

'''
print total_counts
print reversal_counts
print veterinary_counts
unique_record_files = {}
unique_record_files_lc = {}
unique_studyid_count_files = {}
'''
print "year,distinct studyid,total records,reversal records,reversals %,vet records, vet records %,distinct records,duplicate records,duplicates %"
for i in unique_record_files_lc:
    if i > 1980:
        n_unique_records = open(unique_record_files_lc[i]).read().strip()
        n_unique_studyid = open(unique_studyid_count_files[i]).read().strip()
        print ",".join([str(i),# year
                        n_unique_studyid, # distinct studyid
                        str(total_counts[i]) if i in total_counts else "", # total records
                        str(reversal_counts[i]) if i in reversal_counts else "", # reversal records
                        str(100. * float(reversal_counts[i]) / float(total_counts[i])) if i in reversal_counts else "",
                        str(veterinary_counts[i]) if i in veterinary_counts else "", # vet records
                        str(100. * float(veterinary_counts[i]) / float(total_counts[i])) if i in veterinary_counts else "",
                        n_unique_records,
                        str(total_counts[i] - int(n_unique_records)),
                        str(    100.* float(total_counts[i] - int(n_unique_records)) / float(total_counts[i]))
                        ])

print "done"