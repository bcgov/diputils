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
'''20190311 supposing a csv file, with header, count the number of rows
'''
import os
import sys
from misc import *

if len(sys.argv) < 2:
    err("usage: csv_nrecords [ csv file name ]")
fn = sys.argv[1]
f = open(fn)

l_1 = f.readline().strip().split(",")
l_2 = f.readline().strip().split(",")

if len(l_1) != len(l_2):
    err("probably not a csv file")
nrec = os.popen("wc -l " + fn).read().strip().split()[0]

try:
    nrec = int(nrec)
except:
    err("could not parse number: " + string(nrec))

print "number of records: ", str(nrec)
