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
'''Visualize correlations in a large table:
combinatorically generate:

0) detect categorical vs. numeric data

from csv of heterogeneous types (numeric, categorical)
 geo: special case of categorical

1) scatter plots of numerics (each numeric vs. the other numeric)
     with linear fit and R^2 and variable names as labels

2) categorical vs. numeric: numeric average over category:
 bar plot labelled with category/count and sorted from lowest to highest

3) categorical vs. categorical:
contingency table represented as multi-bar plot?

4)
 numeric vs. geo:
 plot numeric average on geo area (this is categorical, hence
 already covered: need second script to convert geo categories
 (via shapefile) to plots

 multicore plot creation: speed up'''
from misc import *

if len(args) < 2:
    err("csv_visualize [input csv file]")

print "read csv.."
lines = open(args[1]).readlines()
hdr, lines = lines[0].strip().lower().split(','), lines[1:]
f_i = {hdr[i]: i for i in range(0, len(hdr))}
i_f = {i: hdr[i] for i in range(0, len(hdr))}
data, ncol = {}, -1
if False: #exists(args[1] + '.pkl'):
   print "load pickle"
   data = pickle.load(open(args[1] + '.pkl'))
else:
    for i in range(0, len(lines)):
        w = lines[i].strip().split(',')
        if len(w) != len(hdr):
            err(str(len(w)) + " len(w) " + line)
        for j in range(0, len(hdr)):
            field = i_f[j]
            if field not in data:
                data[field] = []
            data[field].append(w[j])
        #print "save pickle"
        #pickle.dump(data, open(args[1] + '.pkl', 'wb'))

print "data read success"
# print data["msp_total_ami_visits"]

numeric_fields = []
categorical_fields = []
count = {}

for i in range(0, len(hdr)):
    field = i_f[i]
    #print field
    is_numeric = True
    is_categorical = True
    ncol = len(data[field])
    for j in range(0, ncol):
        try:
            if(data[field][j] ==''):
                data[field][j] = 0.
            d = float(data[field][j])
            is_categorical = False
            data[field][j] = d
        except:
            is_numeric = False
    if is_numeric:
        numeric_fields.append(field)

    if is_categorical:
        categorical_fields.append(field)
        count[field] = len(histo(data[field]).keys())

categorical_fields.append("ha")

print "fields", len(hdr)
print "numeric", len(numeric_fields)
print "categorical", len(categorical_fields)
num = set(numeric_fields)
cat = set(categorical_fields)
fld = set(hdr)

#print "numeric", num
#print "categorical", cat
unclassed = (fld - cat) - num # put these into categorical, except the large ones

exclude_fields = ['studyid', 'diagnosis_date', 'date_of18th_bday', 'dob']
for field in unclassed:
    if field not in exclude_fields: #['studyid', 'diagnosis_date', 'date_of18th_bday', 'dob']:
        if field not in categorical_fields:
            categorical_fields.append(field)

# {'in_sdpr': 2, 'e_expected_to_work_sdpr_percentile': 4, 'data_source': 2, 'dpno_grouping': 5, 'date_of18th_bday': 370, 'dob': 370, 'diagnosis_text_description': 4, 'days_on_n05a_cat': 5, 'famtype_grouped': 4, 'pssg': 2, 'alive': 2, 'sex': 3, 'diagnosis_date': 5778, 'emplstat_pssg_detail': 4, 'i_persistent_multiple_barriers_sdpr_percentile': 2, 'f_temporarily_excused_from_work_sdpr_percentile': 3, 'm_expected_to_work_medical_condition_sdpr_percentile': 3, 'studyid': 77256, 'marital_pssg_detail': 5, 'h_persons_with_disabilities_sdpr_percentile': 3}
#print count

# 1) iterate the numeric variables:
print "numeric", len(numeric_fields)
print "categorical", len(categorical_fields)
if not exists("plot_jobs.sh"):
    plot_jobs = open("plot_jobs.sh", "wb")
    for i in range(0, len(numeric_fields)):
        for j in range(0, i):
            if i != j:
                idx = 'pair,' + str(i) +"," + str(j)
                field1, field2 = numeric_fields[i], numeric_fields[j] #i_f[i], i_f[j]
                print "*", field1, field2
                nrow = len(data[field1])
                ofn = idx + ".csv"
                o_f = wopen(ofn)
                o_f.write(",".join([field1, field2]))
                for k in range(0, nrow):
                    o_f.write("\n" + str(data[field1][k]) + ',' + str(data[field2][k]))
                o_f.close()
                plot_jobs.write('rscript R:/' + os.popen("whoami").read().strip() + '/bin/R/csv_plot.R ' + ofn + '\n')
    plot_jobs.close()
    #run("multicore plot_jobs.sh")

# 2) iterate the categorical vs. numerical:
if not exists("plot_jobs2.sh"):
    plot_jobs2 = open("plot_jobs2.sh", "wb")
    for i in range(0, len(categorical_fields)):
        field1 = categorical_fields[i]
        if field1 in exclude_fields:
            continue
        for j in range(0, len(numeric_fields)):
            idx = 'catnum,' + str(i) + ',' + str(j)
            field2 = numeric_fields[j]
            print "*", field1, field2
            average = {}
            count = {}
            nrow = len(data[field1])
            for k in range(0, nrow):
                cat_key = data[field1][k]
                num_key = data[field2][k]

                if cat_key not in average:
                    average[cat_key] = 0.
                    count[cat_key] = 0.

                average[cat_key] += num_key
                count[cat_key] += 1.

            averages = {}
            for k in average:
                if count[k] > 0.:
                    averages[k] = (average[k] / count[k])
                    #averages[k] = average[k]

            ofn = idx + '.csv'
            o_f = wopen(ofn)
            o_f.write(','.join([field1, field2]))

            for k in averages:
                o_f.write('\n' + (','.join([str(k), str(averages[k])])))
            o_f.write("\n")
            o_f.close()
            plot_jobs2.write('rscript R:/' + os.popen("whoami").read().strip() + '/bin/R/csv_bplot.R ' + ofn + '\n')
    err("end")
    plot_jobs2.close()
