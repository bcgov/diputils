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

from misc import * # using a module

if len(args) < 2:
    err("pnet_get [cohort file name, 1-col csv with header]")

cohort_file = args[1]

files = ['dsp_rpt.dat',
        'clm_rpt_1995_2000.dat',
        'clm_rpt_2001_2005.dat',
        'clm_rpt_2006_2010.dat',
        'clm_rpt_2011_2014.dat',
        'clm_rpt_2015_2018.dat']

run("dd_list") # find and clean all data dictionaries

h_file = 'hlth_prod_final.dat'
if not exists(h_file + '_dd_sliceapply.csv'):
    run('df_get ' + h_file)
    run('dd_sliceapply_all ' + h_file)

csv = []

for f in files:
    csv.append(f + '_dd_sliceapply_cohort.csv')

    if not exists(csv[-1]):
        run("df_get " + f)
        run("dd_sliceapply_all " + f + " " + cohort_file)

        # clean up files
        run("rm -f *.dat *.gz")

        # data cleaning
        run('pnet_check ' + csv[-1])

run("csv_cat_common_fields " + " ".join([cf + '_clean' for cf in csv]))
run("mv csv_cat_common_fields.csv pnet.csv")