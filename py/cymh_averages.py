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

def err(msg):
    print("Error: " + str(msg))
    sys.exit(1)

def run(cmd):
    a = os.system(cmd)
    if a != 0:
        err("command failed:\n\t" + cmd)

fields = ['sex',
          'cluster_id_from_hdb',
          'dad_visits_per_days_reg',
          'dad_ami_visits_per_days_reg',
          'msp_visits_per_days_reg',
          'msp_ami_visits_per_days_reg']

data_file = "merge_table_with_clusters_13September2019.csv"
if not os.path.exists("slice.csv"):
    run("csv_slice " + data_file + " " + " ".join(fields))
    run("mv -f " + data_file + "_slice.csv" + " " + "slice.csv")

select_fields =['sex', 'cluster_id_from_hdb']
run("csv_avg " + "slice.csv " + " ".join(select_fields))

average_fields = []
for f in fields:
    if f not in select_fields:
        average_fields.append(f)

ci = 0
results = []
for f in average_fields:
    for s in select_fields:
        run("csv_slice slice.csv " + s + " " + f)
        outf = "out" + str(ci) + ".csv"
        run("mv -f slice.csv_slice.csv " + outf)
        run("csv_avg " + outf + " " + s)
        results.append(outf + "_csv-avg.csv")
        ci += 1

o_f = open("results.csv", "wb")
for f in results:
    o_f.write((open(f).read() + "\n\n").encode())
o_f.close()
