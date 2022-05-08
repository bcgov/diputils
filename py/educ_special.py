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

'''20190814 this file previously called educ_special_needs_v2.py
# end-to-end process to generate CYMH subtable (education special needs)

# these are the mental health flags:
# H - severe behavioral
# M - moderate behavioural
# R - moderate behaviour support
# N - behaviour disorder rehab
'''
from misc import *

if len(args) < 2:
    err('generate special needs cols from data\n' +
        '\teduc_special_needs [cohort file]')

cohort_file = args[1]


# get data dictionaries for everything so we can unpack the data we need..
if not exists('./dd/'):
    run('dd_list')

# fetch and unzip data file (locally for performance)..
data_file = 'idomed1991-2017.ft_schlstud.A.dat'

if not exists(data_file):
    run('df_get ' + data_file)

# selected a few more things than are actually used..
fields = ['spec_need_perf_grp_this_coll',
          'special_need_group_this_coll',
          'special_need_code_this_coll',
          'special_need_this_coll',
          'graduation_course_count',
          'other_course_count',
          'french_imm_this_coll_flag',
          'french_imm_in_year_flag',
          'esl_this_coll_flag',
          'esl_in_year_flag',
          'gender',
          'studyid']

# result from conversion to csv
csv_file = data_file + '_dd_sliceapply_cohort.csv'

# convert to csv retaining cohort data only, but all fields (dd_sliceapply_all is the program for that)
if not exists(csv_file):
    run('dd_sliceapply_all ' + data_file + ' ' + cohort_file)

# next step is slicing out desired variables (csv_slice is the program for that)
sliced_csv = csv_file + '_slice.csv'

# slice out the desired fields
if not exists(sliced_csv):
    run('csv_slice ' + csv_file + ' ' + ' '.join(fields))

'''The mental health related special needs codes:
    field:
      special_need_code_this_coll
    codes:
      R,M,N,H'''

# if the sliced file for the cohort doesn't exist, make it..
if not exists("idomed1991-2017.ft_schlstud.A.dat_dd_sliceapply_cohort.csv_slice.csv"):
    run("csv_slice idomed1991-2017.ft_schlstud.A.dat_dd_sliceapply_cohort.csv spec_need_perf_grp_this_coll special_need_group_this_coll special_need_code_this_coll special_need_this_coll studyid")

# slice out the relevant fields (could have done this in previous step)

# give the file a shorter name..
if not exists("slice.csv"):
    run("mv idomed1991-2017.ft_schlstud.A.dat_dd_sliceapply_cohort.csv_slice.csv slice.csv")

# open file
f = open("slice.csv")

# readlines() gets all the lines. readline() just gets one..
hdr = f.readline().strip().lower().split(",") # read line, strip whitespace, convert to lower case, split on comma..

# now we have field names
print "fields", hdr

# set builder notation: "{" shape brackets means we're building a dictionary (list in R):
# the list has ordered pairs of the form (hdr[i], i) where i is an integer from 0 to the number of fields..
# a map from the field name to the index of the field
f_i = {hdr[i]: i for i in range(0, len(hdr))}

print f_i
# for the five cols of interest, get the indices.. (resilient to fields moving around)
# 'spec_need_perf_grp_this_coll,special_need_group_this_coll,special_need_code_this_coll,special_need_this_coll'
c0 = f_i['spec_need_perf_grp_this_coll'] # notation for evaluating the map (R- list) is square brackets.. Q: does R use square for list?
c1 = f_i['special_need_group_this_coll']
c2 = f_i['special_need_code_this_coll']
c3 = f_i['special_need_this_coll']

studyid_i = f_i['studyid'] # col index of studyid

''' r - moderate behaviour support / mental illness
    h - intensive behaviour intervention / serious mental illness
    m - behaviour disorder: moderate
    n - behaviour disorder: rehabilitation '''
special_codes = ['r', 'm', 'n', 'h'] # "[" brackets: "python" list: "python" list is a map from [0, len(list)] to whatever is in your list (in C or Java this is an "array": like 1-d matrix or a vector, except it's untyped...)

# outputs: "{" means variables are "dictionary"  (list in R) format..
special_needs_flag_ever = {} # map from studyid to boolean variable
mental_health_flag_ever = {} # map from studyid to boolean variable
gifted_flag_ever = {} # map from studyid to boolean variables

# calculating modes (map from the studyid to a histogram: a map from items to counts) for each col. prefixed with 'spec' (4 cols)
col0_counts = {}
col1_counts = {}
col2_counts = {}
col3_counts = {}

# read all the data row by row
while True:
    # read a row from the file
    line = f.readline()
    if not line: break # if we're out of rows, exit (get out of the loop)

    # strip the line, convert to lower case, split on comma..the various fields in the record in an R-vector (py-list)
    w = line.strip().lower().split(',')

    # try to extract the studyid (we calculated the index for that before)..
    try:
        studyid = w[studyid_i]
    except:
        # if we can't (we can) output an error for debugging..
        print "line", line
        print w
        err("err")

    # if we haven't looked at this person already, assume not special needs unless we find otherwise
    if not studyid in special_needs_flag_ever:
        # make sure this individual is represented in the output "table"
        special_needs_flag_ever[studyid] = False

    # same for "mental_health_flag" except this one is a map that takes values in maps..
    if not studyid in mental_health_flag_ever:
        # if the person isn't represented yet, give them a blank map (the four letter codes will go in there..)
        mental_health_flag_ever[studyid] = {}

    # special_codes is r,m,n,h
    if w[c2] in special_codes:
        # we got a mh related code
        # if value at position c2 (special_need_code_this_coll) is a mh related code, definitely special needs..
        special_needs_flag_ever[studyid] = True

        # if they do have an mh code, we can do mh related stuff..what is the code?
        mh_code = w[c2] # get the mh code..r, m , n, h  (w is all the fields in the record)

        # check the person's map of codes..
        if not mh_code in mental_health_flag_ever[studyid]:
            # put that code in the person's map of codes
            mental_health_flag_ever[studyid][mh_code] = 0

        # add one to the value of the person's map of codes (evaluated at that code)
        mental_health_flag_ever[studyid][mh_code] += 1

    # say my studyid was xxxxxxxx:
    # mental_health_flag_ever[xxxxxxxx]['r'] would be a count of "my" records that had the code 'r'

    # detect non-nonspecial needs (special needs):
    # check the c0: 'spec_need_perf_grp_this_coll' and the 'special_need_code_this_coll' and the 'special_need_this_coll' for non (everything except 'special_need_group_this_coll')
    if not(w[c0][0:3] == 'non' or w[c2][0:3] == 'non' or w[c3][0:3] == 'non'):
        # if there's no non at the start of the contents of any of those three fields, we're special.. (detects anybody with special needs)
        special_needs_flag_ever[studyid] = True

    # for gifted, start out by representing the person in the output..(default non-gifted)
    if not studyid in gifted_flag_ever:
        gifted_flag_ever[studyid] = False

    # now check the data and set to true if they are gifted ('spec_need_perf_grp_this_coll' or 'special_need_this_coll')
    if w[c0] == 'gifted' or w[c3] == 'gifted':
        gifted_flag_ever[studyid] = True

    # build histograms for the ('spec' prefixed) special needs col's
    # make sure this individual is represented (new histogram)
    if studyid not in col0_counts: col0_counts[studyid] = {}
    if studyid not in col1_counts: col1_counts[studyid] = {}
    if studyid not in col2_counts: col2_counts[studyid] = {}
    if studyid not in col3_counts: col3_counts[studyid] = {}

    # build histogram: update the count for each code, for each person, for the given data row:
    # for each of the 4 fields, look at the data. If the code's not in the histogram, put it in there..
    if w[c0] not in col0_counts[studyid]:
        col0_counts[studyid][w[c0]] = 0
    col0_counts[studyid][w[c0]] += 1 # increment the count (for that code, for that person)

    # same, field 2 of 4
    if w[c1] not in col1_counts[studyid]:
        col1_counts[studyid][w[c1]] = 0
    col1_counts[studyid][w[c1]] += 1

    # ...
    if w[c2] not in col2_counts[studyid]:
        col2_counts[studyid][w[c2]] = 0
    col2_counts[studyid][w[c2]] += 1

    # field 4 of 4
    if w[c3] not in col3_counts[studyid]:
        col3_counts[studyid][w[c3]] = 0
    col3_counts[studyid][w[c3]] += 1

# s = studyid
# col_counts is a map from studyid to histogram for that person (for a specific col. only)
# mode for one col., for one person, that only takes into account, the special codes..
# result is NA if all that person's codes (in that col.) did not reflect special-needs
# Note: have to run this for each person, on each of the four special-needs col.'s
def mode_special(s, col_counts, numeric = False):

    # if that person isn't in the histogram, no mode to calculate..
    if s not in col_counts:
        return 'NA'

    # assume NA until proven otherwise..
    max_code = 'NA' # code for most frequently occuring element..
    max_count = 0 # count for most frequently occuring element..

    # iterate over different codes observed for that person..
    for c in col_counts[s].keys(): # col_counts is a histogram (map from items to counts..) keys() gives you the items (ditch the count info..)
        # debug:
        #print "\t", c, col_counts[s][c] # print out the thing, then the count for the thing..

        # assume special until proven otherwise..
        non_special = False

        # for detecting non-non-special, two types of col's to check: numeric and not
        # so-called numeric variable, we detect non-special with 5, rather than 'non'
        if numeric:
            if c == '5':
                # 5 code is non-special
                non_special = True
        else:
            if c[0:3] == 'non': # c[0:3] is the first 3 letters in the string.
                # non code is non-special for this type of col.
                non_special = True

        #print "non_special=", non_special
        if not non_special:
            # if this code is special, if it's count for this person for this code (col_counts[s][c]) is bigger than the max. count so far,
            if col_counts[s][c] > max_count:
                # found a new maximum. update the max code and the count for that..
                max_code, max_count = c, col_counts[s][c]
                # we were operating over counts of all records for one person, for one col.
    # return the code that had the max. count
    # end result: most frequent non-non-special thing, this col., this person
    return max_code

# open a file to put the output in
out_file = open("educ_special.csv", "wb")

# write the col. names, which have to match the stuff in the output string
out_file.write("studyid,special_needs_ever,mental_health_flag_ever,r_flag_ever,h_flag_ever,m_flag_ever,n_flag_ever,gifted_ever,spec_need_perf_grp_this_coll_special_mode,special_need_group_this_coll_special_mode,special_need_code_this_coll_special_mode,special_need_this_coll_special_mode")

# iterate over all the people
for s in special_needs_flag_ever:

    # for this person,
    # calculate the "mode of special codes" for that person, for a given col. using the histograms we built in the last step..
    col0_special_most_frequent = mode_special(s, col0_counts)
    col1_special_most_frequent = mode_special(s, col1_counts, True) # special_need_group_this_coll needs special treatment as it's a number
    col2_special_most_frequent = mode_special(s, col2_counts)
    col3_special_most_frequent = mode_special(s, col3_counts)

    # output string
    output = [str(s), # studyid
              'Yes' if special_needs_flag_ever[s] else 'No', # special_needs_ever
              'Yes' if len(mental_health_flag_ever[s].keys()) > 0 else 'No', # ,mental_health_flag_ever. use keys() to extract the codes observed for that person, from the map for that person, which is: mental_health_flag_ever[s]. if the length of the py-list (R-vector) of mh codes for that person is > 0, they have an mh code
              'Yes' if 'r' in mental_health_flag_ever[s] else 'No', # r_flag_ever: check for the specific mh code 'r' for the person..
              'Yes' if 'h' in mental_health_flag_ever[s] else 'No', # same for h..
              'Yes' if 'm' in mental_health_flag_ever[s] else 'No', # same for m..
              'Yes' if 'n' in mental_health_flag_ever[s] else 'No', # same for n..
              'Yes' if gifted_flag_ever[s] else 'No', # gifted_ever:

              # modes for the person, with respect to the 4-"special" col's, with respect to "special needs" data only..i.e., non-non-special in the data..
              col0_special_most_frequent, # spec_need_perf_grp_this_coll_special_mode,
              col1_special_most_frequent, # special_need_group_this_coll_special_mode,
              col2_special_most_frequent, # special_need_code_this_coll_special_mode,
              col3_special_most_frequent] # special_need_this_coll_special_mode

    out_file.write("\n" + ",".join(output))

out_file.close()
print "done"
'''special needs records don't start with "non":
    (*) in one record, different things aren't mixed: only one code:
    (*) can't be flagged gifted at same time as having physical flag, or gifted at same time as having learning disability, etc.
    (*) not coded more than once in a given record!!!!!!!!!!!!!

Angus feedback:
 "set of concerns is empty"
 "set of comments finite and already expressed!"
 : )

'''
