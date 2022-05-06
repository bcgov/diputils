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
import os, sys, math, pickle, datetime
from misc import load_fields, assert_exists, err, run
'''grad.py: this script implements a graduation metric concept
20190416 version; grad concept: > grad 1 psy_pssg_cohort_20190423.csv_unnest.csv

# run by opening C:/cygwin64/Cygwin.bat

# before running, type:
#    cd /cygdrive/r/working/bin/
#    source bash_profile
# then, type:
#    cd /cygdrive/r/working/education/
#    grad
'''

# this script will use this flag to call itself for the second version
v_2 = False
try:
    v_2 = True if sys.argv[1] == "2" else False
    if not v_2:
        if sys.argv[1] != "1":
            err("argument must be 1 or 2")
except:
    pass

if len(sys.argv) < 3:
    print "Important: delete the *.p files before running, if you change the cohort file!!!"
    err("usage:\n\tgrad [version 1 or 2: start with 1] [cohort file.csv]\nhuman should enter 1 for first parameter.")

if not os.path.exists("dd") or not os.path.isdir("dd"):
    # find, extract and clean data dictionary files
    run("dd_list")
    run("dd_clean")

# data dictionary file for registry:
dd_reg = "dd/2018-09-27_data_dictionary_consolidation-file-january-1-1986-onwards.xlsx_registry.C.csv2"; assert_exists(dd_reg)
dd_schlstud = "dd/2019-01-24_data_dictionary_education.xlsx_schlstud.csv2"; assert_exists(dd_schlstud)
dd_studcrd = "dd/2019-01-24_data_dictionary_education.xlsx_studcrd.csv2"; assert_exists(dd_studcrd)

cohort_file = sys.argv[2]; #'youth_cohort.csv' # delete *.p files and other intermediary files if cohort changes
schlstud_file = 'idomed1991-2017.ft_schlstud.A.dat_dd_sliceapply.csv'
studcrd_file = 'idomed1991-2017.ft_studcrd.A.dat_dd_sliceapply.csv'
registry_file = 'registry1991-2016_dd_sliceapply.csv_cat.csv'
files = [cohort_file, schlstud_file, studcrd_file, registry_file]

# prepare school student file, if not yet
if not os.path.exists(schlstud_file):
    print "School student file not found. Extracting.."
    schlstud_datfile = "dat/idomed1991-2017.ft_schlstud.A.dat"; assert_exists(schlstud_datfile)
    slice_fields = "birthdate_yymm school_year age_group_jun_30 age_in_years_jun_30 age_group_dec_31 age_in_years_dec_31 school_postal_code grade_this_enrol studyid"
    a = os.system("dd_slice_apply " + dd_schlstud + " " + schlstud_datfile + " "  + slice_fields)
    assert_exists(schlstud_datfile + "_dd_sliceapply.csv")
    a = os.system("mv " + schlstud_datfile + "_dd_sliceapply.csv" + " " + schlstud_file)

# prepare student credit data, if not yet
if not os.path.exists(studcrd_file):
    print "Student credit file not found. Extracting.."
    studcrd_datfile = "dat/idomed1991-2017.ft_studcrd.A.dat"; assert_exists(studcrd_datfile)
    slice_fields = "credential_cnt trax_school_year sp_need_perf_grp_lst_knwn_coll sp_need_code_lst_knwn_coll credential_name studyid"
    a = os.system("dd_slice_apply " + dd_studcrd + " " + studcrd_datfile + " " + slice_fields)
    assert_exists(studcrd_datfile + "_dd_sliceapply.csv")
    a = os.system("mv " + studcrd_datfile + "_dd_sliceapply.csv" + " " + studcrd_file)

# prepare registry data, if not yet (combine into one csv file)
if not os.path.exists(registry_file):
    print "Registry file not found. Extracting.."
    registry_files = os.popen('find ./dat/registry/ -name "*.dat"').read().strip().split("\n")
    slice_fields = "startday daysreg year studyid"
    for f in registry_files: # registry datfile
        a = os.system("dd_slice_apply " + dd_reg + " " + f + " " + slice_fields)
        assert_exists(f + "_dd_sliceapply.csv")
    slice_files = os.popen('find ./dat/registry/ -name "*.dat_dd_sliceapply.csv').read().strip().split("\n")
    a = os.system("csv_cat " + (" ".join(slice_files)))
    assert_exists("csv_cat.csv")
    a = os.system("mv csv_cat.csv " + registry_file)

print("loading..")

for f in files: assert_exists(f) # check for files

# extract studyid
cohort_id_file = cohort_file + "_studyid"
a = os.system("csv_split " + cohort_file) if not os.path.exists(cohort_id_file) else None
assert_exists(cohort_id_file) # make sure we got the result

# load filtered student credit table
dat_cohort, datf_cohort = None, None
if not os.path.exists('dat_cohort.p'):
    print "dat_cohort.p not found. Creating.."
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
        a = os.system("csv_select " + cohort_id_file + " studyid " + table_file)
    assert_exists(select_file)
    return select_file

# filter tables for cohort
schlstud_select_file, studcrd_select_file, registry_select_file = [filter_table_for_cohort(cohort_id_file, schlstud_file),
                                                                   filter_table_for_cohort(cohort_id_file, studcrd_file),
                                                                   filter_table_for_cohort(cohort_id_file, registry_file)]
# load filtered school student table
dat_schlstud, datf_schlstud = None, None
if not os.path.exists('dat_schlstud.p'):
    print "dat_schlstud.p not found. Creating.."
    dat_schlstud, datf_schlstud = load_fields([schlstud_select_file, 'school_year', 'age_group_jun_30', 'birthdate_yymm', 'age_in_years_jun_30'])
    pickle.dump([dat_schlstud, datf_schlstud], open('dat_schlstud.p', 'wb'))
else:
    dat_schlstud, datf_schlstud = pickle.load(open('dat_schlstud.p', 'rb'))

# load filtered student credit table
dat_studcrd, datf_studcrd = None, None
if not os.path.exists('dat_studcrd.p'):
    print "dat_studcrd.p not found. Creating.."
    dat_studcrd, datf_studcrd = load_fields([studcrd_select_file, 'credential_cnt', 'trax_school_year', 'credential_name'])
    pickle.dump([dat_studcrd, datf_studcrd], open('dat_studcrd.p', 'wb'))
else:
    dat_studcrd, datf_studcrd = pickle.load(open('dat_studcrd.p', 'rb'))

# load filtered msp registry table
dat_registry, datf_registry = None, None
if not os.path.exists('dat_registry.p'):
    print "dat_registry.p not found. Creating.."
    dat_registry, datf_registry = load_fields([registry_select_file, 'startday', 'daysreg', 'year' ])
    pickle.dump([dat_registry, datf_registry], open('dat_registry.p', 'wb'))
else:
    dat_registry, datf_registry = pickle.load(open('dat_registry.p', 'rb'))

if not v_2:
    print("calculating some stats..")
    def p_avg(dat, name):
        avg = 0.
        for i in dat: avg += float(len(dat[i]))
        print(str(avg / float(len(dat))) + " " + name + " records per id, that table")

    p_avg(dat_schlstud, "schlstud")
    p_avg(dat_studcrd, "studcrd")
    p_avg(dat_registry, "registry")

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

def jun30(year):
    jan1, jun30 = datetime.datetime(year, 1, 1), datetime.datetime(year, 6, 30)
    return int(str(datetime.timedelta(1) + jun30 - jan1).split(',')[0].split()[0])

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
def in_bc_when_gr12_age(i):
    global dob, dat_registry, fdat_registry, code
    in_bc = False # guilty until proven innocent
    yyyy, mm, dd = dob[i].split('-') # dob: 'yyyy-mm-dd'
    yyyy, mm, dd = int(yyyy), int(mm), int(dd)
    school_yr_17 = yyyy + 17 if mm <= 6 else yyyy + 18 # year they're 17 at june
    school_yr_18 = yyyy + 18 if mm <= 6 else yyyy + 19 # year they're 18 at june
    jun30_yr17, jun30_yr18 = jun30(school_yr_17), jun30(school_yr_18)

    if i not in dat_registry: return in_bc
    for dataline in dat_registry[i]:
        reg_year = int(dataline[fdat_registry['year']])
        daysreg = int(dataline[fdat_registry['daysreg']])
        start_day = int(dataline[fdat_registry['startday']])
        end_day = start_day + daysreg - 1
        # case for 17 and 18
        if reg_year == school_yr_17 and start_day <= jun30_yr17 and jun30_yr17 <= end_day:
            in_bc = True
        if reg_year == school_yr_18 and start_day <= jun30_yr18 and jun30_yr18 <= end_day:
            in_bc = True
    return in_bc

for i in studyid: # for every studyid (call it "i")
    code[i] = None
    if i in dat_studcrd:
        code[i] = "YES_0-graduated" # graduated!
        for dataline in dat_studcrd[i]: # sanity check to make sure the credential count is always 1
            if dataline[fdat_studcrd["credential_cnt"]] != "1":
                print("i:" + str(i)) # crash if there is not a 1 code
                err("found unexpected credential_cnt: " + str(dat_studcrd[i][fdat_studcrd["credential_cnt"]]))
        continue
    else: # didn't graduate

        code[i] = "N/A_0-not-in-registry" if i not in dat_registry else code[i]
        if i not in dat_registry: continue
        code[i] = "N/A_1-not-in-schlstud" if i not in dat_schlstud else code[i]
        if i not in dat_schlstud: continue

        yyyy, mm, dd = dob[i].split('-')
        yyyy, mm, dd = int(yyyy), int(mm), int(dd)
        max_age = None
        for dataline in dat_schlstud[i]:
            age = int(dataline[fdat_schlstud['age_in_years_jun_30']])
            max_age = age if max_age is None else max_age
            max_age = age if age > max_age else max_age
        if max_age < 17:
            code[i] = "N/A_2-too-young"; continue

        ever_adult_student = False # innocent until proven guilty
        # fields in datarow: datf_schlstud
        if i in dat_schlstud:
            for dataline in dat_schlstud[i]:
                if dataline[fdat_schlstud['age_group_jun_30']][0:5] == 'ADULT': ever_adult_student = True
        if not v_2:
            #if ever_adult_student:
            #    code[i] = "NO_0-adult-student"; continue
            if in_bc_when_gr12_age(i):
                code[i] = "NO_1-in-bc"; continue
            else:
                code[i] = "N/A_3-left-province"; continue
        else:
            if in_bc_when_gr12_age(i):
                code[i] = "NO_1-in-bc";
                #if ever_adult_student:
                #    code[i] = "NO_0-adult-student"; continue
            else:
                code[i] = "N/A_3-left-province"; continue

lines = ["studyid,grad_concept3,grad_concept7" + ("_v2" if v_2 else "")]
for i in studyid:
	w = code[i].split("_")
	code_short = code[i] if len(w) ==1 else w[0]
	lines.append(str(i) + "," + code_short + "," + str(code[i]))

out_fn = "graduation_output" + ("_v2" if v_2 else "") + ".csv"
open(out_fn, "wb").write(('\n'.join(lines)).encode())

# generate frequency table
a = os.system("count " + out_fn + " IGNORE_STUDYID=True")
a = os.system("cat " + out_fn + "_frequ")

# call the second version of the code:
#if not v_2:
#    a = os.system("grad 2 " + sys.argv[2]) # call this script and invoke second version
