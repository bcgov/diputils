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
''' 2019-02 extract data for edu project
        make local copies of metadata files and data input files
        delete local files and copy the results to network storage'''
import os
import sys
from misc import *
dry = False

use_local = True
output_directory = "R:\\working\\out\\"

log_n = 0
log_f = open("gather_log.txt","wb")
files = open("gather.txt").read().strip().split('\n')

s = 0L
dat_f, dat_f_tmp, dd_f, dd_f_tmp = None, None, None, None
for f in files:
    f = f.strip()
    if f != '':
        sz = os.stat(f).st_size
        s += sz
        f = os.path.abspath(f)
        # print f
        if len(f.split()) > 1:
            err("filename with space in it")
        # got something from the file
        if f[-4:] == "csv2":
            dd_f = f
        if f[-3:] == "dat":
            dat_f = f

print s / 1000000000., "Gb"
print "---------------------------------------------------"

def run(s):
    global log_n, log_f
    if log_n > 0:
        log_f.write("\n")
    s = s.strip()
    # print "cmd: ", s
    if dry:
        log_f.write("SKIP\t" +s)
        log_n += 1
        return
    a = os.system(s)
    if a != 0:
        log_f.close()
        err("command failed: \n\t" + s)

    log_f.write(s)
    log_f.flush()
    log_n += 1

select = {}
select['data_dictionary_education.xlsx_schlstud.csv2'] = ['studyid', 'special_need_code_this_coll']

select['data_dictionary_discharge-abstracts-database-hospital-separations-april-1-1985-onwards.xlsx_hospital.N.csv2']=['studyid', 'addate', 'diagx1', 'dsc']
select['data_dictionary_discharge-abstracts-database-hospital-separations-april-1-1985-onwards.xlsx_hospital.H.csv2']=['studyid', 'addate', 'diagx1', 'dsc']
select['data_dictionary_discharge-abstracts-database-hospital-separations-april-1-1985-onwards.xlsx_hospital.G.csv2']=['studyid', 'addate', 'diagx1', 'dsc']
select['data_dictionary_medical-services-plan-payment-information-file-april-1-1985-onwards.xlsx_msp.C.csv2'] =  ['spec', 'icd9', 'icd9_1', 'icd9_2', 'icd9_3', 'icd9_4', 'icd9_5', 'servcode', 'servdate', 'pracnum*', 'studyid']
select['data_dictionary_pharmanet-january-1-1996-onwards.xlsx_dsp_rpt.A.csv2'] =  ['de.studyid', 'de.hlth_prod_label', 'de.dspd_qty', 'de.srv_date']
select['data_dictionary_pharmanet-january-1-1996-onwards.xlsx_hlth_rpt.A.csv2'] =  ['hp.din_pin', 'hp.gen_drug']

dat_f, dat_f_tmp, dd_f, dd_f_tmp = None, None, None, None
for f in files:
    f = f.strip()
    print "f", f
    if f != '':
        f = os.path.abspath(f)
        if len(f.split()) > 1:
            err("filename with space in it")
        fn = f.split("\\")[-1]
        #print "\t", fn
        # got something from the file
        if f[-4:] == "csv2":
            print f
            if dd_f != None:
                pass # this was for not iterating past the first dd: # sys.exit(1)
            dd_f = f
            dd_f_tmp = fn
            run("cp -v " + dd_f + " " + dd_f_tmp)

        if f[-3:] == "dat":
            if dd_f_tmp == None:
                err("data dictionary not selected")
            dat_f = f
            dat_f_tmp = fn
            csv_f = dat_f_tmp + "_dd_apply.csv"
            slc_f = csv_f.strip() + "_slice.csv"
            if os.path.exists(slc_f):
                # don't process this dataset if the output is already there
                continue
            print "\t" + f
            if use_local:
                run("cp -v " + dat_f + " " + dat_f_tmp)
            bindir = "C:/cygwin64/home/" + os.popen("whoami").read().strip() + "/bin/"
            run(bindir + "dd_apply.exe " + dd_f_tmp + " " + (dat_f_tmp if use_local else dat_f))
            # remove intermediary file
            if use_local:
                run("rm -f " + dat_f_tmp)

            run(bindir + "csv_slice.exe " + csv_f + " " + (" ".join(select[dd_f_tmp])))
            # remove intermediary files
            run("rm -f " + csv_f)
                        # for csv_slice, e.g. of input type prefixing the executable name..

            run("mv -v " + slc_f + " " + output_directory + "/" + fn + "_slice.csv")
log_f.close()
