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
'''2019-07-23 apply cohort file and mental-health drug list,
to concatenated  (integrated) pharmanet data
- product: various

example use:
$ pnet_druglist psy_studypop_dad_15July2019.csv_studyid csv_cat_common_fields.csv
(was used to generate an output of CYMH project)

*** NB don't forget to delete pnet_druglist.p if the cohort or data change!!!!'''
import os
import sys
import time
import pickle
import shutil
from misc import *

cohort_file, pnet_file = None, None
if len(sys.argv) == 2:
    cohort_file, pnet_file = sys.argv[1], 'pnet.csv' # _clean' #sys.argv[2]
else:
    err("druglist.py: search concatenated pharmanet file; apply mh-category drug list to determine mh-drug usage stats for study population\n" +
            "\tdruglist [study population 1-col csv labelled studyid]" +
            "\nNote: pharmanet concatenated data must be in pnet.csv")

if not exists('pnet.csv'):
    run('pnet_get ' + cohort_file)

print "cohort file: " + cohort_file
print "pnet file: " + pnet_file

fn_druglist = "NPDUIS_2019_002C_Drug_list_v1_00.xlsx"
if not os.path.exists(fn_druglist):
    err("required file: " + fn_druglist)

if not exists("dd"):
    run("dd_list")

hpf_file = "hlth_prod_final.dat_dd_sliceapply.csv"
if not os.path.exists(hpf_file):
    hpf_data_file = 'hlth_prod_final.dat'
    run('df_get ' + hpf_data_file)
    run('dd_sliceapply_all ' + hpf_data_file)


# reading the human-readable drug identifiers
def load_hlth_labels():
    lines = open("hlth_prod_final.dat_dd_sliceapply.csv").readlines()
    hdr = lines[0].strip() # header is the first line
    lines = lines[1:] # data comes after the header
    if hdr != "hp.din_pin,hp.drug_brand_nm,hp.gen_drug,hp.gcn_seq_num,hp.gen_drug_strgth_val,hp.gen_drug_strgth_unit,hp.gen_dsg_form_cd,hp.gen_dsg_form,hp.ahfs_3_cd,hp.tc5_cd":
        err("unexpected fields:\n\t" + hdr)
    hdr = hdr.strip().split(",") # split on comma produces a vector of the data elements for that row..

    # dog, cat, bat --> ['dog', 'cat', 'bat']

    # return two dictionaries: lookup for the two human-readable fields (map from integers to strings)
    hp_drug_brand_nm, hp_gen_drug = {}, {} # elements of the list are in the format DINPIN:drug_brand_nm (e.g., {1000:'MORPHINE SULPHATE POWDER'}

    # go through the vector of lines from the csv:
    for line in lines:
        w = line.strip().split(",") # split to get a vector of fields
        if len(w) != len(hdr):
            err("unexpected # of fields")
        hp_drug_brand_nm[w[0]] = w[1] # map the din onto the readable thing.. like {1000:'MORPHINE SULPHATE POWDER'}
        hp_gen_drug[w[0]] = w[2] # maps din onto second (similar) field
    return hp_drug_brand_nm, hp_gen_drug

# build a histogram
def count(x):
    c = {}
    for i in x:
        if i not in c:
            c[i] = 0
        c[i] += 1
    return c

# use this function to sort a histogram
def srt(x):
    y = [[x[i], i] for i in x]
    return sorted(y, key=lambda x: x[0], reverse=True)

'''
# e.g. testing the top3 concept:
x = [1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5]
print count(x)
srt(count(x))
print top3(x)
sys.exit(0)
'''

# top three concept (based on a histogram / counts)
def top3(x):
    s = srt(count(x))
    if len(s) >= 3:
        return [i[1] for i in s[0:3]]
    elif len(s) == 2:
        return [s[0][1], s[1][1], str(None)]
    elif len(s) == 1:
        return [s[0][1], str(None), str(None)]
    else:
        return [str(None), str(None), str(None)]

expected_fields = ["DIN_PDIN", "BRAND_NAME_E_DESC", "PDIN_FLAG*",
                       "ATC_LEVEL_4_CODE", "ATC_LEVEL_4_E_DESC",
                       "ATC_LEVEL_5_CODE", "ATC_LEVEL_5_E_DESC"]
# not all of these may be required at this point

# write R script to use readxl library to open the XLS file
open("dd_unpack.R", "wb").write('''# convert Excel files to CSV: one CSV per sheet in Excel file 20190213
# usage: Rscript dd_unpack.R [name of Excel file to unpack]
library(readxl)

fn<-""
args = commandArgs(trailingOnly=TRUE)

if(length(args)>=1) fn<-args[1]
if(length(args)==0) stop("Error: usage: Rscript dd_unpack.R [data dictionary file.xls/xlsx]")

for(s in excel_sheets(fn)){
  out_fn<-paste(paste(fn, s, sep="_"), ".csv", sep="");
  write.csv(read_excel(fn, sheet=s, skip=1), out_fn);
  }''') # python:  out_fn = fn + "_" + s + ".csv"

if not exists('druglist.csv'):  # convert EXCEL format to CSV
    a = os.system("rscript dd_unpack.R " + fn_druglist)
    a = os.system("rm -f dd_unpack.R") # clean up
    druglist = "NPDUIS\_2019\_002C\_Drug_list\_v1\_00.xlsx\_DIN\ list.csv"

    for root, dirs, files in os.walk("."): # goes through all the files in the present directory
        for f in files:
            if len(f.split("DIN")) > 1:  # looks for files that have DIN in them (should only be one..)
                if os.path.exists(f):
                    # copy that file to druglist.csv
                    shutil.copyfile(f, "druglist.csv") # sheet that maps dins to a category
                else:
                    err("problem copying file!")

    # correct the drugslist csv to remove quotation marks, and remove leading zeros
    lines, DIN_PDIN = open("druglist.csv").readlines(), -1
    for i in range(0, len(lines)):
        w = lines[i].strip().split(",") # vector of data (instead of comma separated)
        for j in range(0, len(w)):
            w[j] = w[j].strip('"') # strip the quotation marks off of things..
        # remove leading zeros from dinpin col

        # find out what col. the dinpin is in..
        if i == 0: # on the first line:
            for j in range(0, len(w)):
                if w[j] == "DIN_PDIN": # take the j-th data value on the first line..
                    DIN_PDIN = j # store j if the value matches "DIN_PDIN"
        else: # if you're past the header, strip leading zeros
            w[DIN_PDIN] = w[DIN_PDIN].lstrip('0')
        lines[i] = ",".join(w)
    open("druglist.csv", "wb").write("\n".join(lines)) # cleaned file

lines = open("druglist.csv").readlines() # open cleaned file
hdr, data = lines[0], lines[1:]
fields = hdr.strip().split(",")
fields = [f.strip('"') for f in fields]
f_i = {fields[i] : i for i in range(0, len(fields))} # map from field name to index of that field..

# checking that all the expected fields are there..
for f in expected_fields:
    if f not in fields:
        err("expected field: " + f + " not found in druglist.csv")

# codes to search for in the CSV (based on ATC_LEVEL_4_CODE)-- for 'N07B':'ADDICTIVE DISORDER DRUGS', we search for N07B (second element of tuple is a readable label)..
atc_codes = {'N07B':'ADDICTIVE DISORDER DRUGS',
             'N06C':'PSYCHOLEPTICS AND PSYCHOANALEPTICS',
             'N06B':'STIMULANTS',
             'N06A':'ANTIDEPRESSANTS',
             'N05B':'ANXIOLYTICS',
             'N05A':'ANTIPSYCHOTICS'} # map 4-character atc code stem, to a readable description

ci, di = f_i['ATC_LEVEL_4_CODE'], f_i['DIN_PDIN'] # get indices for ATC and DIN fields..

# create categorized dinpin lists, that match 4-character ATC code stem, to dinpin
dinpin_lists = {} # match 4-character ATC code stem, to dinpin list (list of dinpin within that category)
reverse_lookup = {} # match dinpin bck to 4-character ATC code stem
for d in data: # drug list data..
    words = d.strip().split(",") # get a vector of the fields for a line..
    atc4 = words[ci].strip().strip('"') # pull out the atc code.. (should have already been cleaned for ")
    dinpin = words[di].strip().strip('"').lstrip('0') # pull out din pin (should have already been cleaned for leading 0s)..
    if len(atc4) >= 4:
        atc44 = atc4[0: 4] #for the record from the drug list, look at the first 4 digits only (match on the first 4 digits)
        if atc44 in atc_codes: # check if the first 4 digits of the code, were in our list..(atc_codes)..

            # if we don't have a vector for that 4-digit code, add an empty vector..
            if atc44 not in dinpin_lists: dinpin_lists[atc44] = []

            # vector of dinpins, for each 4-digit code.. list of vectors (R-speak): apply the index: dinpin_lists[atc44] you get a vector
            # append adds something to the back of a vector
            dinpin_lists[atc44].append(dinpin) # create a list of dinpin for a given category (python list is vector in R, python map/dictionary is list in R)

            # want a map from dinpin, to 4-digit code..
            reverse_lookup[dinpin] = atc44 # be able to go backwards, too

print "\n**************************************" # simple stats about codes..(how many dinpin for each 4-letter code)
print "  ATC Code, Drug Category Name, Count"
for c in dinpin_lists:
    print "  " +str(c) + "," + str(atc_codes[c]) + "," + str(len(dinpin_lists[c])) # len() is length of vector
print "************************************"

# read studyid, discard header (not a studyid)
# [1:] removes the header row
studyid = open(cohort_file).read().strip().split("\n")[1:]  # every line (except header) of cohort file is a studyid

# make sure no whitespace
studyid = [i.strip() for i in studyid] # clean off whitespace..

print "study population size (assuming unique):", len(studyid)

# get pnet file size and open it
pnet_file_size, f = os.stat(pnet_file).st_size, open(pnet_file)

# check for required fields in pharmanet file
hdr = f.readline().strip().split(",")
hdr_fi = {hdr[i] : i for i in range(0, len(hdr))}

# use the field-index "list" (python or algebra map) to find out where the fields are located..
si = hdr_fi['studyid'] if 'studyid' in hdr_fi else -1
di = hdr_fi['hlth_prod_label'] if 'hlth_prod_label' in hdr_fi else -1
sdi = hdr_fi['srv_date'] if 'srv_date' in hdr_fi else -1

# crash if we couldn't get an index for the required fields
if si == -1 or di == -1 or sdi == -1:
    err("required field not found in pnet file. studyid, hlth_prod_label, or srv_date")

# where --> is "map" (apply dictionary)

# R-list that maps studyid to a list of pins for that person
pins = {} # studyid --> list of pins (count top3) (single nested dictionary)

# R-list (python map) that maps studyid to a list of drug-categories (by 4-letter code)
first = {} # studyid --> category --> earliest prescribe date, given category (double nested dictionary)
# R: list of lists!!! Nested list..

l_i, line, n_inc = 0, None, 100000

# don't regenerate things if we don't have to (try to restore the end result..)
if os.path.exists("pnet_druglist.p"):
    print "load previously generated data.."
    [pins, first] = pickle.load(open("pnet_druglist.p"))
else:
    # calculate the end result

    # for each line of the pharmanet data file
    while(True):
        line = f.readline()
        if not line: # get out if no more data
            break
        w = line.strip().split(",") # split the line by comma (get a vector)
        if len(w) != len(hdr): # sanity check: number of fields
            if w != ['']:
                print line
                print w
                print l_i
                err("unexpected # of fields")
            else:
                continue

        # extract required fields this line (clean dinpin for leading zeros if they're there)
        dinpin, my_id, srv_date = w[di].lstrip('0'), w[si].strip(), w[sdi].strip() # my_id is studyid

        # atc44 = reverse_lookup[dinpin]

        if srv_date[4] != '-' or srv_date[7] != '-': # check date formatting yyyy-mm-dd
            err('unknown date fmt.: ' + srv_date + " (not yyyy-mm-dd)")

        # for this record, check if the studyid is associated with the study population
        if my_id in studyid: # individual is in study pop

            # start a list of dinpins for this person, if we don't have one already
            if not my_id in pins:
                pins[my_id] = []

            # go through the lists of dinpin, by mh drug category (here c is a 4letter code N07A etc..)
            for c in dinpin_lists:
                # if the dinpin for this pharmanet record is in one of the drug din lists, got a match!
                if dinpin in dinpin_lists[c]: # mh drug use: positive
                    #c = reverse_lookup[dinpin]

                    # add that dinpin to the individual's din list..
                    pins[my_id].append(dinpin)
                    if not my_id in first:
                        first[my_id] = {}

                    # record the earliest date for that mh drug category (by 4 letter code);
                    # initialize a first date for the category (for this pnet record) if there isn't one for that category
                    if not c in first[my_id]:
                        first[my_id][c] = srv_date

                    # if the date is earlier than the one on file, replace it.. (hence you get an earliest date)..
                    if srv_date < first[my_id][c]:
                        first[my_id][c] = srv_date # store serv date if smaller
        else:
            pass # drop a record that isn't for the study population

        # progress bar
        if l_i > n_inc and l_i % n_inc == 0:
            print "%", 100. * (float(f.tell()) / float(pnet_file_size))
        l_i += 1 # next line
    pickle.dump([pins, first], open("pnet_druglist.p", "wb"))

print "\nstudyid, {first mh-drug category : prescribe date}"
for p in first:
    if p in first: print str(p) + "," + str(first[p])

# top 3 MH-related dinpin
# ever prescribed MH drug (any category)
# first prescribe date each category

categories = dinpin_lists.keys()
output_file_name = cohort_file  + "_mh_drugs.csv"
f = open(output_file_name, "wb")
f.write("studyid," + # anonymized identifier
        "mh_top3_1_din,mh_top3_2_din,mh_top3_3_din," + # top 3 mh-related dinpin
        "mh_top3_1_atc,mh_top3_2_atc,mh_top3_3_atc," + # atc for the above
        "mh_top3_1_str,mh_top3_2_str,mh_top3_3_str," + # readable string for the atc code
        (",".join([(c + "_ever") for c in categories])) + "," + # ever prescribed in given category
        (",".join([c + "_firstdate" for c in categories])) + "," + # first date prescr. in category
        "mh_drug_ever," + # ever prescribed from mh drug list

        # readable brand descriptors for top3 dins
        "hp.drug_brand_nm_top3_1,hp.drug_brand_nm_top3_2,hp.drug_brand_nm_top3_3," +
        "hp.gen_drug_top3_1,hp.gen_drug_top3_2,hp.gen_drug_top3_3," +

        # top-3 when we count on categories, not dinpins-- hence a category can't appear >1 time
        "mh_cat_1,mh_cat_2,mh_cat_3\n")

a, b = load_hlth_labels()

for p in pins:
    s, t3, mh_ever = str(p), top3(pins[p]), False
    for i in range(0, 3):
        s += "," + (t3[i] if t3[i] != "None" else "NA")

    for i in range(0, 3):
        s += "," + (reverse_lookup[t3[i]] if (t3[i] != "None" and t3[i] in reverse_lookup) else "NA")

    for i in range(0, 3):
        s += "," + (atc_codes[reverse_lookup[t3[i]]] if (t3[i]!="None" and t3[i] in reverse_lookup and reverse_lookup[t3[i]] in atc_codes) else "NA")
    '''
    s += "," + (t3[0] if t3[0]!="None" else "NA")
    s += "," + (t3[1] if t3[1]!="None" else "NA")
    s += "," + (t3[2] if t3[2]!="None" else "NA")
    '''
    for c in categories: # need to document this a bit more..
        x = ""
        if p not in first: # no first date, haven't had it
            x = "NO"
        else:
            if c not in first[p]:
                x = "NO"
            else:
                x = "YES"
                mh_ever = True
        s += ("," + x)

    for c in categories:
        x = ""
        if p not in first:
            x = "NA"
        else:
            if c not in first[p]:
                x = "NA"
            else:
                x = str(first[p][c])
        s += "," + x
    s += "," + ("YES" if mh_ever else "NO")

    # finally write out some human-readable drug labels (For the "top 3")
    for i in range(0, 3):
        s += "," + (a[t3[i]] if (t3[i] in a) else "NA")

    for i in range(0, 3):
        s += "," + (b[t3[i]] if (t3[i] in b) else "NA")

    # reverse_lookup: match dinpin back to 4-character ATC code (stem)

    # calculate a top-3 so that the dinpin is mapped onto a category before it's counted..
    t3 = top3([reverse_lookup[pp] for pp in pins[p]])

    for i in range(0, 3):
        s += "," + (t3[i] if t3[i]!="None" else "NA")
    #.. this gives a top3 where the entries can't repeat

    '''
    s += "," + a[t3[0]]
    s += "," + a[t3[1]]
    s += "," + a[t3[2]]
    s += "," + b[t3[0]]
    s += "," + b[t3[1]]
    s += "," + b[t3[2]]
    '''
    f.write(s + "\n")
f.close()
print "number of studyid:", len(pins.keys())
print "output file name:", output_file_name
# add last date for category
# add birth date for individual..
