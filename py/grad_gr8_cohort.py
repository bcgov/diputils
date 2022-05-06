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
'''
grad_gr8_cohort.py
This script follows a gr8 cohort to graduation (20190430 version)

# run by opening C:/cygwin64/Cygwin.bat

# before running, type:
#    cd /cygdrive/r/working/bin/
#    source bash_profile
# then, type:
#    cd /cygdrive/r/working/education/

# grad_gr8_cohort youth_cohort.csv 4
#  youth_cohort.csv has studyid, dob (yyyy-mm)'''
import os, sys, math, pickle, datetime
from misc import load_fields, assert_exists, err, run

if not os.path.exists("dd") or not os.path.isdir("dd"):
    # find, extract and clean data dictionary files
    run("dd_list")
    run("dd_clean")

# data dictionary file
dd_reg = "dd/2019-01-09_data_dictionary_consolidation-file-january-1-1986-onwards.xlsx_registry.C.csv2"
dd_schlstud, dd_studcrd = "dd/2019-01-24_data_dictionary_education.xlsx_schlstud.csv2", "dd/2019-01-24_data_dictionary_education.xlsx_studcrd.csv2"
for f in [dd_reg, dd_schlstud, dd_studcrd]:
    assert_exists(f)

if len(sys.argv) < 3:
    print "Important: delete the *.p files before running, if you change the cohort file!!!"
    err("Usage: grad_gr8_cohort [cohort_file.csv] [number of years=6?]")

cohort_file = sys.argv[1] #'youth_cohort.csv' # delete *.p files and other intermediary files if cohort changes
number_of_years = None
try:
    number_of_years = int(sys.argv[2])
except:
    err("failed to parse second parameter, year interval e.g. 4, 6, or 8")

schlstud_file = 'idomed1991-2017.ft_schlstud.A.dat_dd_sliceapply.csv'
studcrd_file = 'idomed1991-2017.ft_studcrd.A.dat_dd_sliceapply.csv'
registry_file = 'registry1991-2016_dd_sliceapply.csv_cat.csv'
files = [cohort_file, schlstud_file, studcrd_file, registry_file]

# prepare school student file, if not yet
if not os.path.exists(schlstud_file):
    schlstud_datfile = "dat/idomed1991-2017.ft_schlstud.A.dat"; assert_exists(schlstud_datfile)
    slice_fields = "birthdate_yymm school_year age_group_jun_30 age_in_years_jun_30 age_group_dec_31 age_in_years_dec_31 school_postal_code grade_this_enrol studyid"
    run("dd_slice_apply " + dd_schlstud + " " + schlstud_datfile + " "  + slice_fields)
    assert_exists(schlstud_datfile + "_dd_sliceapply.csv")
    run("mv " + schlstud_datfile + "_dd_sliceapply.csv" + " " + schlstud_file)

# prepare student credit data, if not yet
if not os.path.exists(studcrd_file):
    studcrd_datfile = "dat/idomed1991-2017.ft_studcrd.A.dat"; assert_exists(studcrd_datfile)
    slice_fields = "credential_cnt trax_school_year sp_need_perf_grp_lst_knwn_coll sp_need_code_lst_knwn_coll credential_name studyid"
    run("dd_slice_apply " + dd_studcrd + " " + studcrd_datfile + " " + slice_fields)
    assert_exists(studcrd_datfile + "_dd_sliceapply.csv")
    run("mv " + studcrd_datfile + "_dd_sliceapply.csv" + " " + studcrd_file)

# prepare registry data, if not yet (combine into one csv file)
if not os.path.exists(registry_file):
    registry_files = os.popen('find ./dat/registry/ -name "*.dat"').read().strip().split("\n")
    if registry_files == ['']:
        zip_files = os.popen('find ./dat/registry -name "*.gz"').read().strip().split("\n")
        for f in zip_files:
            run("unzp " + f.strip()) # the c-wrapped version is visible in system() but not in python's os.system!

    registry_files = os.popen('find ./dat/registry/ -name "*.dat"').read().strip().split("\n")
    if registry_files == ['']:
        err("failed to find registry files")

    slice_fields = "startday daysreg year studyid"
    for f in registry_files: # registry datfile
        f = f.strip()
        if f == "": continue
        run("dd_slice_apply " + dd_reg + " " + f + " " + slice_fields)
        assert_exists(f + "_dd_sliceapply.csv")
    slice_files = os.popen('find ./dat/registry/ -name "*.dat_dd_sliceapply.csv').read().strip().split("\n")
    run("csv_cat " + (" ".join(slice_files)))
    assert_exists("csv_cat.csv")
    run("mv csv_cat.csv " + registry_file)

print("loading..")
for f in files: assert_exists(f) # check for files

# extract studyid
cohort_id_file = cohort_file + "_studyid"
run("csv_split " + cohort_file) if not os.path.exists(cohort_id_file) else None
assert_exists(cohort_id_file) # make sure we got the result

# load filtered student credit table
dat_cohort, datf_cohort = None, None
if not os.path.exists('dat_cohort.p'):
    dat_cohort, datf_cohort = load_fields([cohort_file, 'dob'])
    pickle.dump([dat_cohort, datf_cohort], open('dat_cohort.p', 'wb'))
else:
    dat_cohort, datf_cohort = pickle.load(open('dat_cohort.p', 'rb'))
studyid, dob = list(dat_cohort.keys()), {}
fdat_cohort = {datf_cohort[i] : i for i in range(0, len(datf_cohort))}

# express dob as a function of studyid
for i in studyid:
    dob[i] = dat_cohort[i][fdat_cohort['dob']][0]

def filter_table_for_cohort(cohort_id_file, table_file):
    select_file = table_file + "_select.csv"
    if not os.path.exists(select_file):
        run("csv_select " + cohort_id_file + " studyid " + table_file)
    assert_exists(select_file)
    return select_file

# filter tables for cohort
registry_select_file = filter_table_for_cohort(cohort_id_file, registry_file)
schlstud_select_file = filter_table_for_cohort(cohort_id_file, schlstud_file)
studcrd_select_file =  filter_table_for_cohort(cohort_id_file, studcrd_file)

# load filtered school student table
dat_schlstud, datf_schlstud = None, None
if not os.path.exists('dat_schlstud.p'):
    print("schlstud_select_file", schlstud_select_file)
    dat_schlstud, datf_schlstud = load_fields([schlstud_select_file, 'school_year', 'age_group_jun_30', 'birthdate_yymm', 'age_in_years_jun_30', 'grade_this_enrol'])
    pickle.dump([dat_schlstud, datf_schlstud], open('dat_schlstud.p', 'wb'))
else:
    dat_schlstud, datf_schlstud = pickle.load(open('dat_schlstud.p', 'rb'))

# load filtered student credit table
dat_studcrd, datf_studcrd = None, None
if not os.path.exists('dat_studcrd.p'):
    dat_studcrd, datf_studcrd = load_fields([studcrd_select_file, 'credential_cnt', 'trax_school_year', 'credential_name'])
    pickle.dump([dat_studcrd, datf_studcrd], open('dat_studcrd.p', 'wb'))
else:
    dat_studcrd, datf_studcrd = pickle.load(open('dat_studcrd.p', 'rb'))

# load filtered msp registry table
dat_registry, datf_registry = None, None
if not os.path.exists('dat_registry.p'):
    dat_registry, datf_registry = load_fields([registry_select_file, 'startday', 'daysreg', 'year' ])
    pickle.dump([dat_registry, datf_registry], open('dat_registry.p', 'wb'))
else:
    dat_registry, datf_registry = pickle.load(open('dat_registry.p', 'rb'))

if True:
    print("calculating some stats..")
    def p_avg(dat, name):
        avg = 0.
        for i in dat: avg += float(len(dat[i]))
        print(str(avg / float(len(dat))) + " " + name + " records per id, that table")

    p_avg(dat_schlstud, "schlstud")
    p_avg(dat_studcrd, "studcrd")

    def had(dat, studyid, name):
        had = 0.
        for i in studyid:
            if i in dat: had += 1.
        print(str(100. * had / float(len(studyid))) + " % of cohort, had " + name)

    had(dat_schlstud, studyid, "schlstud")
    had(dat_studcrd, studyid, "studcrd")
    had(dat_registry, studyid, "registry")

fdat_studcrd = {datf_studcrd[i] : i for i in range(0, len(datf_studcrd))}
fdat_schlstud = {datf_schlstud[i] : i for i in range(0, len(datf_schlstud))}
fdat_registry = {datf_registry[i] : i for i in range(0, len(datf_registry))}
print("studcrd", fdat_studcrd)
print("schlstud", fdat_schlstud)
print("registry", fdat_registry)

start_of_last_observed_school_year = 1900
print("calculating last observed school year (starting year)..")
# find the last school year present in the data (for "too young to graduate" class)
for i in studyid:
    if i in dat_schlstud:
        for dataline in dat_schlstud[i]:
            school_year = dataline[fdat_schlstud['school_year']]
            school_year = int(school_year.split('/')[0])
            if school_year > start_of_last_observed_school_year:
                start_of_last_observed_school_year = school_year
print("last observed start of school year", start_of_last_observed_school_year)
print("classifying student population..")
code = {}
my_gr8_year = {}
for i in studyid: # for every studyid (call it "i")

    gr8_year, grad_year = None, None

    if i in dat_studcrd:
        # a student in this table did graduate: has credential
        for dataline in dat_studcrd[i]:
            credential_cnt = dataline[fdat_studcrd['credential_cnt']]
            trax_school_year = dataline[fdat_studcrd['trax_school_year']]
            credential_name = dataline[fdat_studcrd['credential_name']]
            # print credential_cnt, trax_school_year, credential_name
            if credential_cnt != '1':
                err('credential_cnt != 1')
            trax_school_year = int(trax_school_year.split('/')[0])
            # take the first grad year
            if grad_year is None:
                grad_year = trax_school_year
            else:
                if trax_school_year < grad_year:
                    grad_year = trax_school_year

    if i in dat_schlstud:
        for dataline in dat_schlstud[i]:
            school_year = dataline[fdat_schlstud['school_year']]
            school_year = int(school_year.split('/')[0])
            grade_this_enrol = dataline[fdat_schlstud['grade_this_enrol']]
            try:
                grade_this_enrol = int(grade_this_enrol)
            except:
                pass
            #print school_year, grade_this_enrol
            if grade_this_enrol == 8:
                gr8_year = school_year
    my_gr8_year[i] = gr8_year

    code[i] = "" #N/A_4-unknown"
    if gr8_year is None:
        code[i] = "N/A_4-no-gr8"
        continue
    else:

        if not(grad_year is None): # graduated sometime
            if grad_year - gr8_year <= number_of_years:
                code[i] = "YES_1-gradwindow"; continue  # graduated within n_year window! Woohoo
            else:
                code[i] = "YES_2_grad_after_window"; continue # graduated outside of the window
        else:
            code[i] += "NO_2-nevergradded" # didn't graduate yet

        code[i] = "N/A_0-not-in-registry" if i not in dat_registry else code[i]
        if i not in dat_registry: continue
        code[i] = "N/A_1-not-in-schlstud" if i not in dat_schlstud else code[i]
        if i not in dat_schlstud: continue

        # too young to graduate? e.g., start gr8 sep 2015; 2015 + 4 = 2019 -> bigger than start of last observed school year
        if gr8_year + 4 > start_of_last_observed_school_year:
            code[i] = "N/A_2-too-young-to-grad" # too young to graduate
            continue

        # MSP: check if ever left bc between gr8 and when they should have bn. in grade 12.
        left_province = False # left province or died?
        if i not in dat_registry:
            code[i] += "N/A_0-not-in-registry"; continue
        reg_yrs = [int(dataline[fdat_registry['year']]) for dataline in dat_registry[i]]
        for year in range(gr8_year + 3, gr8_year + 4): # end bracket zero indexed (need +1) subtract one for year interval mismatch
            if year not in reg_yrs:
                left_province = True
        if left_province:
            code[i] = "N/A_3-left-province"; continue

count = {}
lines = ["studyid,grad_output_n" + str(number_of_years) + "_short, grad_output_n" + str(number_of_years)]
for i in studyid:
	w = code[i].split("_")
	code_short = code[i] if len(w) ==1 else w[0]
	lines.append(str(i) + "," + code_short + "," + str(code[i]))
        if code[i] not in count:
            count[code[i]] = 1
        count[code[i]] += 1
        #if code[i] == 'YES-gradNO_2-left-province':
        #    print i, code[i], "my_gr8_year", my_gr8_year[i]
print count

# print "GRADUATION RATE %", 100. * count['YES'] / (count['YES'] + count['NO_0'] + count['NO_1'])
# print "too young to graduate %(total)", 100.*count['N/A_1'] / (count['N/A_0'] + count['N/A_1'] + count['YES'] + count['NO_0'] + count['NO_1'])

out_fn = "graduation_output_n" + str(number_of_years) + ".csv"
open(out_fn, "wb").write(('\n'.join(lines)).encode())

# generate frequency table
run("count " + out_fn + " SUPPRESS_STUDYID=True")
# run("cat " + out_fn + "_frequ")
