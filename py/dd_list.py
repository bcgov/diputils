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
'''dd_list.py: this script finds, converts and cleans all (known at the time of development)
data dictionaries into the format used by education and health

 It extracts data dictionaries stored in excel format,
 and is able to remediate an error caused by having multi-line cells

(*) internal procedure to extract excel files:
      
      python rscript.py dd_unpack.R data_dictionary_education.xlsx
      rscript dd_unpack.R data_dictionary_education.xlsx

1) dd_list.py: list data dictionaries and make copy in local folder, extracting to csv. Calls dd_clean..
3) dd_examine.py: loop through the results to check if the cleaned outputs are good
4) dd_extract.py:
5) dd_match.py
'''
import os
import sys
import csv
import time
from misc import *

# write R script to use readxl library to open the XLS file
open("dd_unpack.R", "wb").write('''# convert Excel files to CSV: one CSV per sheet in Excel file 20190213
# usage: Rscript dd_unpack.R [name of Excel file to unpack]
library(readxl)

fn<-""
args = commandArgs(trailingOnly=TRUE)

if(length(args)>=1) fn<-args[1]
if(length(args)==0) stop("Error: usage: Rscript dd_unpack.R [data dictionary file.xls/xlsx]")

for(s in excel_sheets(fn)){ out_fn<-paste(paste(fn, s, sep="_"), ".csv", sep=""); write.csv(read_excel(fn, sheet=s, skip=1), out_fn); }''')

# a = os.system("rscript dd_unpack.R " + fn_druglist)

if exists('./dd'):
    err("data dictionary folder already initialized")

csv.register_dialect('my', delimiter=",", quoting=csv.QUOTE_ALL, skipinitialspace=True)
whoami = os.popen("whoami").read().strip()
os.system("mkdir dd")

excel = []
xls = os.popen('find R:/DATA/ -name "data_dictionary*.xls"').read().strip().split("\n")
for xlf in xls:
    excel.append(xlf.strip())

xlsx = os.popen('find R:/DATA/ -name "data_dictionary*.xlsx"').read().strip().split("\n")
for xlf in xlsx:
    excel.append(xlf.strip())
    print xlf.split("/")

print "copying excel files into dd/ folder.."
for xlf in excel:
    if os.path.exists(xlf):
        date_str = xlf.split('/')[2].strip().replace(" ", "_")
        run("cp " + xlf + " dd/" + date_str + "_" + xlf.split('/')[-1])

print "extracting data dictionaries"

excel = os.popen("ls -1 dd/").read().strip().split("\n")
for xlf in excel:
    localf = "./dd/" + xlf
    localfp = localf.replace('\ ','_')
    localfp = localfp.replace(' ','_')
    run("mv " + localf + " " + localfp)
    localf = localfp.strip("\'")
    print "\t" + "./dd/" + localf

    # need to update this line:
    dd_unpack = os.path.abspath("R:/" + whoami + "/bin/R/dd_unpack.R").replace('\\','/')
    a = os.system("rscript dd_unpack.R " + localf)
    # run("rscript " + dd_unpack + " " + localf)

run("dd_clean") # only need to clean data dictionaries we didn't make ourselves

pssg = os.popen('find R:/DATA/ -name "pssg_linked*.txt"').readlines()
for fn in pssg:
    fn = fn.strip()
    if not os.path.exists(fn):
        continue
    t = time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(fn)))
    new_fn = 'dd/' + t + '_' + fn.split('/')[-1]
    run('cp ' + fn + ' ' + new_fn)
    run('dd_convert_pssg_summary_to_csv2 ' + new_fn)

nflt = os.popen('find R:/DATA/ -name "*nflt"').read().strip().split("\n")
for fn in nflt:
    if not os.path.exists(fn):
        continue
    fn = fn.strip()
    date_str = fn.split('/')[2].strip().replace(" ", "_")
    new_fn = "dd/" + date_str + "_" + fn.split('/')[-1]
    run("cp " + fn + " " + new_fn)
    run("dd_convert_nflt_to_csv2 " + new_fn)
