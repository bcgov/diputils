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
'''20190108 this script excludes records not part of rob's cohort..
1) first special needs code
2) second special needs code..
3) moderate or severe?
4) mental health code ever??????????
5) year for mental health code???????? record from education data....
min, max, least common, most common.'''
import os
import sys
import time; t = time.time(); tt = time.time(); ttt = None;
in_fn = "2019-01-08_merged.csv_slice2.csv"
in_fn = "2019-01-09_merged2.csv_slice.csv"
in_fn = "merged5.csv_slice.csv"

f= open(in_fn)
g = open(in_fn + "_filter_psych.csv", "wb")

fields = f.readline().split(",")
print fields
g.write(",".join(fields)+"\n")

ci = 0
while True:
    line = f.readline()
    if not line:
        break
    w = line.strip().split(",")
    if len(w) != len(fields):
        print "error"
        sys.exit(1)
    if not w[0]=="":
        g.write(",".join(w)+"\n")
    ci += 1
    if ci % 10000 == 0:
        ttt = tt
        tt = time.time()
        print ci/1000, "1/2 k, S/10 k: ", tt-ttt

'''20180108 special needs flag:
    if they got a special needs designation,
        it's in there and it's flagged and that's the value

Also want a secondary search in a new col.:
  if they got more than one spec. needs. des, good to know
    what the other designation is?

Spec. needs code overrides non-special needs codes

1) first special needs code
2) second special needs code..
3) moderate or severe? '''
