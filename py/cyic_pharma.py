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
20190601 filter pharmanet for cyic and control/demographic pops

Run this script in a directory with 1TB free, write privileges,
    good read/write speed (local SSD) and the following files:

pharmanet data:
    5 x clm_rpt_xxxx_xxxx.dat
    dsp_rpt.dat

study group files (csv, one col with header: pc.studyid)
    demography_lt19.csv_studyid
    studyid_incare_popn_201712.csv_unnest.csv_STUDYID

health product file (hlth_prod.csv, preview below:)
    $ head hlth_prod.csv
    pc.hlth_prod_label,hp.drug_brand_nm
    1000,MORPHINE SULFATE POWDER
    10014,LERITINE TABLETS 25MG
    1007,MYDRIACYL
    10073,VIMICON TAB 4MG (D/C)

druglist.csv (preview below):
    $ head druglist.csv
    DIN_PDIN , BRAND_NAME_E_DESC , PDIN_FLAG* , ATC_LEVEL_4_CODE , ATC_LEVEL_4_E_DESC , ATC_LEVEL_5_CODE , ATC_LEVEL_5_E_DESC
    02248732,APO CLONIDINE 0.025mg tab,N,C02AC,Imidazoline receptor agonists,C02AC01,CLONIDINE
    00259527,CATAPRES 0.1mg tab,N,C02AC,Imidazoline receptor agonists,C02AC01,CLONIDINE
    00291889,CATAPRES 0.2mg tab,N,C02AC,Imidazoline receptor agonists,C02AC01,CLONIDINE
    02361299,CLONIDINE 0.025mg tab,N,C02AC,Imidazoline receptor agonists,C02AC01,CLONIDINE
    22123089,CLONIDINE CAPS 0.1MG COMPOUNDED,Y,C02AC,Imidazoline receptor agonists,C02AC01,CLONIDINE

categories.csv (preview below):
    $ head categories.csv
    N07B,ADDICTIVE DISORDER DRUGS
    N06C,PSYCHOLEPTICS AND PSYCHOANALEPTICS
    N06B,STIMULANTS
    N06A,ANTIDEPRESSANTS
    N05B,ANXIOLYTICS
    N05A,ANTIPSYCHOTICS
'''

import os, sys

# system call
def run(cmd):
    print("[" + cmd + "]")
    a = os.system(cmd)
    if a != 0:
        print("Error: command failed: " + str(cmd))

'''
extract pharmanet
'''
# pharmanet claims files
clm_files = ['clm_rpt_1995_2000.dat',
             'clm_rpt_2001_2005.dat',
             'clm_rpt_2006_2010.dat',
             'clm_rpt_2011_2014.dat',
             'clm_rpt_2015_2018.dat']

# extract pharmanet claims files
for f in clm_files:
    if os.path.exists(f) and not os.path.exists(f+"_dd_sliceapply.csv"):
        run("dd_slice_apply dd/2019-04-24_data_dictionary_pharmanet-january-1-1996-onwards.xlsx_clm_rpt.A.csv2 " + f + " PC.STUDYID PC.HLTH_PROD_LABEL")

# extract pharmanet dispensation file
if os.path.exists("dsp_rpt.dat") and not os.path.exists("dsp_rpt.dat_dd_sliceapply.csv"):
    run("dd_slice_apply dd/2019-04-24_data_dictionary_pharmanet-january-1-1996-onwards.xlsx_dsp_rpt.A.csv2 " + f + " PC.STUDYID PC.HLTH_PROD_LABEL")

# since the records extracted are the same, we can merge the files
if not os.path.exists("pharmanet_1995-2018.csv"):
    run("csv_cat " + " ".join(clm_files) + " dsp_rpt.dat_dd_sliceapply.csv")
    run("mv -v csv_cat.csv pharmanet_1995-2018.csv")

# build lists of dinpins from drug categories
''' take categories.csv:

    N07B,ADDICTIVE DISORDER DRUGS
    N06C,PSYCHOLEPTICS AND PSYCHOANALEPTICS
    N06B,STIMULANTS
    N06A,ANTIDEPRESSANTS
    N05B,ANXIOLYTICS
    N05A,ANTIPSYCHOTICS

 and use that to filter druglist.csv (cleaned csv version of drug list from Dan's sheet NPDUIS_2019_002C_Drug_list_v1_00.xlsx)
 to extract (for each category) the appropriate list of dinpins

*** output*** : a list of dinpins for each category
'''

print("building drug list for each category..")

drug_categories = []
drug_category_labels = {}

for line in open("categories.csv").read().strip().split("\n"):
    words = line.strip().split(",")
    drug_categories.append(words[0].strip())
    drug_category_labels[words[0].strip()] = words[1].strip()
    print("* " + str(words))

if not os.path.exists("druglist_ascii.csv"):
    run("iconv -t ASCII//TRANSLIT//IGNORE  druglist.csv > druglist_ascii.csv")

fn = "druglist_ascii.csv_unnest.csv"
if not os.path.exists(fn):
    run("unnest druglist_ascii.csv")

# DIN_PDIN , BRAND_NAME_E_DESC , PDIN_FLAG* , ATC_LEVEL_4_CODE
if not os.path.exists(fn + "_slice.csv"):
    run("csv_slice " + fn + " DIN_PDIN ATC_LEVEL_4_CODE")

fn = "druglist_ascii.csv_unnest.csv_slice.csv"
f = open(fn)

category_lists = {}
for c in drug_categories:
    category_lists[c] = []

line = f.readline().strip() # skip the header
if line != "din_pdin,atc_level_4_code":
    print("Expected header: din_pdin,atc_level_4_code")
    sys.exit(1)
while True:
    line = f.readline()
    if not line: break
    line = line.strip()
    words = line.split(",")
    if len(words) != 2:
        print("Error: expected line of length 2")
        sys.exit(1)
    my_pin, my_category = words[0], words[1]

    my_pin = my_pin.lstrip('0')
    #print(drug_categories)
    for c in drug_categories:
        if c == my_category[0:len(c)]:
            category_lists[c].append(my_pin)

fn_i = {}
for i in range(0, len(drug_categories)):
    n_d = 0
    fni = "dinpin-list_" + str(i)+ drug_category_labels[drug_categories[i]].replace(" ","-") + ".csv"
    f = open(fni, "wb")
    f.write("pc.hlth_prod_label".encode());
    for dinpin in category_lists[drug_categories[i]]:
        f.write(("\n" + dinpin.strip()).encode())
        n_d += 1
    f.close()
    fn_i[i] = fni
    print(drug_category_labels[drug_categories[i]].replace(" ","-") + " ndrugs=" + str(n_d))

# now bring in the control and study pops
study_file = "studyid_incare_popn_201712.csv_unnest.csv_STUDYID"
contr_file = "demography_lt19.csv_studyid"

# assert they have only unique studyids
if not os.path.exists(study_file + "_unique-studyid.csv"):
    run("unique_studyid " + study_file)

if not os.path.exists(contr_file + "_unique-studyid.csv"):
    run("unique_studyid " + contr_file)

def grab(cmd):
    return os.popen(cmd).read()

def nlin(fn):
    return int(grab("lc " + fn)) - 1

if nlin(study_file) != nlin(study_file + "_unique-studyid.csv"):
    print("Error: nonunique studyid in study group file")
    sys.exit(1)

if nlin(contr_file) != nlin(contr_file + "_unique-studyid.csv"):
    print("Error: nonunique studyid in control group file")
    sys.exit(1)

print("\nunique studyid for control group [CHECK]")
print("unique studyid for study group [CHECK]")


'''
 restrict pharmanet data to groups of interest
'''

# now, filter the pharmanet data for the groups. filtered files will be:
pharma_contr = "pharmanet_1995-2018.csv_select-demography_lt19.csv_studyid.csv"
pharma_study = "pharmanet_1995-2018.csv_select-studyid_incare_popn_201712.csv_unnest.csv_STUDYID.csv"

# the file to filter:
pharma_file = "pharmanet_1995-2018.csv"

# build a "jobs" file to run "multicore.py" on:
f, runme = open("jobs.txt", "wb"), False
#  csv_select [file to filter by] [field name] [first file to filter] .. [last file to filter]
if not os.path.exists(pharma_contr):
    f.write(("csv_select " + contr_file + " pc.studyid " + pharma_file + "\n").encode())
    print("extracting pharmacare records for control/demography group..")
    runme = True
if not os.path.exists(pharma_study):
    f.write(("csv_select " + study_file + " pc.studyid " + pharma_file + "\n").encode())
    print("extracting pharmacare records for study group..")
    runme = True
f.close()

if runme:
    run("multicore jobs.txt") # spawn to multiple processors

''' before filtering data for the drug groups, add the readable-identifier to the data cf:
$ head hlth_prod.csv
pc.hlth_prod_label,hp.drug_brand_nm
1000,MORPHINE SULFATE POWDER
10014,LERITINE TABLETS 25MG
1007,MYDRIACYL
10073,VIMICON TAB 4MG (D/C)
10081,642 TAB
10154,PAPAVERINE HCL TAB 100MG
10189,DANILONE TAB 50MG (D/C)
10197,COLISONE TAB 5MG (D/C)
10200,PROPYL-THYRACIL
'''

pharma_contr_lookup = pharma_contr + "_lookup.csv"
pharma_study_lookup = pharma_study + "_lookup.csv"

if not os.path.exists(pharma_contr_lookup):
    run("csv_lookup hlth_prod.csv " + pharma_contr)
if not os.path.exists(pharma_study_lookup):
    run("csv_lookup hlth_prod.csv " + pharma_study)

# now filter the data for the drug groups!
#pharmanet_1995-2018.csv_select-studyid_incare_popn_201712.csv_unnest.csv_STUDYID.csv
#pharmanet_1995-2018.csv_select-demography_lt19.csv_studyid.csv

# filter study and control group data, for each drug category
runme = False
f = open("jobs.txt", "wb")
for i in range(0, len(drug_categories)):
    fni = "dinpin-list_" + str(i)+ drug_category_labels[drug_categories[i]].replace(" ","-") + ".csv"
    outfile = pharma_study_lookup + "_select-" + fni + ".csv"
    if not os.path.exists(outfile):
        cmd = "csv_select " + fni + " pc.hlth_prod_label " + pharma_study_lookup
        f.write((cmd + "\n").encode())
        print("\t\t"+ cmd)
        runme = True
    outfile = pharma_contr_lookup + "_select-" + fni + ".csv"
    if not os.path.exists(outfile):
        cmd = "csv_select " + fni + " pc.hlth_prod_label " + pharma_contr_lookup
        f.write((cmd + "\n").encode())
        print("\t\t" + cmd)
        runme = True
f.close()
if runme:
    run("multicore jobs.txt 1") # spawn a thread right away per job (no queue)


# filter results of above, for unique studyid (want one record per category per studyid)
runme = False
# filter for unique studyids:
f = open("jobs.txt", "wb")
for i in range(0, len(drug_categories)):
    fni = "dinpin-list_" + str(i)+ drug_category_labels[drug_categories[i]].replace(" ","-") + ".csv"
    outfile = pharma_study_lookup + "_select-" + fni + ".csv"
    if not os.path.exists(outfile + "_unique-studyid.csv"):
        cmd = "unique_studyid " + outfile
        f.write((cmd + "\n").encode())
        runme = True
    outfile = pharma_contr_lookup + "_select-" + fni + ".csv"
    if not os.path.exists(outfile + "_unique-studyid.csv"):
        cmd = "unique_studyid " + outfile
        f.write((cmd + "\n").encode())
        runme = True
f.close()
if runme:
    run("multicore jobs.txt 1") # spawn a thread right away per job (no queue)


# create output table
for i in range(0, len(drug_categories)):
    print("category index," +
          "drug category," +
          "number of records (multiple records possible for a given dinpin or a given studyid)," +
          "number of records (just one record for a given studyid)," +
          "study/control pop, avg. number of prescriptions ever this category this group per person," +
          "popsize" +
          "est. percentage of people this group ever prescribed this drug category," +
          "ratio: fraction of people in study group known to be ever prescribed this drug category vs. fraction of people in control group known to be ever prescribed this drug category: hint: larger than 1")

    fni = "dinpin-list_" + str(i)+ drug_category_labels[drug_categories[i]].replace(" ","-") + ".csv"
    outfile = pharma_study_lookup + "_select-" + fni + ".csv"
    study_n_i = nlin(outfile)
    outfile = outfile + "_unique-studyid.csv"
    study_n_i_us = nlin(outfile)
    ratio = "n/a" if study_n_i * study_n_i_us == 0 else str(float(study_n_i) / float(study_n_i_us)) # number of prescriptions this category / number of people ever prescribed this category: average number of prescriptions ever recorded this category, per person
    popsize = nlin(study_file)
    ratio2 = 100. * study_n_i_us / popsize # number of people ever prescribed in this category (regardless of drug type quantity or frequency) / pop size = percentage of people this group, ever prescribed this drug category
    str1 = (str(i) + "," + drug_category_labels[drug_categories[i]] + "," + str(study_n_i) + "," + str(study_n_i_us) + ",study," + ratio + "," + str(popsize) + "," + str(ratio2))
    outfile = pharma_contr_lookup + "_select-" + fni + ".csv"
    study_n_i = nlin(outfile)
    outfile = outfile + "_unique-studyid.csv"
    study_n_i_us = nlin(outfile)
    ratio = "n/a" if study_n_i * study_n_i_us == 0 else str(float(study_n_i) / float(study_n_i_us)) # number of prescriptions this category / number of people ever prescribed this category: average number of prescriptions ever recorded this category, per person
    popsize = nlin(contr_file)
    ratio2a = ratio2 # keep the ratio for the first group for comparing that to the second group
    ratio2 = study_n_i_us / popsize # number of people ever prescribed in this category (regardless of drug type quantity or frequency) / pop size = percentage of people this group, ever prescribed this drug category

    str2 = (str(i) + "," + drug_category_labels[drug_categories[i]] + "," + str(study_n_i) + "," + str(study_n_i_us) + ",demog," + ratio + "," + str(popsize) + "," + str(ratio2))
    try:
        print(str1 + "," + str(100. * ratio2a / ratio2))
    except:
        print(str1 + ",n/a")
    try:
        print(str2 + "," + str(100. * ratio2a / ratio2))
    except:
        print(str2 + ",n/a")
