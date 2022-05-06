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
'''Sort service utilization patterns:
    an attempt at full data integration'''
from misc import *
my_csv = os.popen("ls -1 sup_cohort_sort*csv").readlines()

for c in my_csv:
    run('rm -f ' + c.strip())

csv = os.popen("ls -1 *.csv").readlines()

n_d_files = 0
n_records = 0
n_headers = 0

next_ri = 0
records = {}
records_i = {}

next_fi = 0
d_files = {}
d_files_i = {}

next_hi = 0
headers = {}
headers_i = {}

ri_to_hi = {}
ri_to_dfi = {}

for c in csv:
    print "csv file", c
    fn = c.strip()
    if fn == "":
        continue

    n_d_files += 1

    # use data file name as table name
    dfn = fn.split(".dat")[0] + ".dat"

    # assign index to table
    if dfn not in d_files:
        d_files[dfn] = next_fi
        next_fi += 1

    fi = d_files[dfn]
    d_files_i[fi] = dfn

    # assign index to record

    lines = open(fn).read().strip().lower().split("\n")
    lines = [lines[i].strip() for i in range(0, len(lines))]

    if len(lines) > 1:
        print "len(lines)", len(lines), fn, dfn
        hdr = lines[0]
        n_headers += 1

        if hdr not in headers:
            headers[hdr] = next_hi

        next_hi += 1
        hdr_i = headers[hdr] # map the record onto this
        headers_i[hdr_i] = hdr

        for i in range(1, len(lines)):
            n_records += 1
            record = lines[i]
            if record not in records:
                records[record] = next_ri
                next_ri += 1
            record_i = records[record]
            ri_to_hi[record_i] = hdr_i
            records_i[record_i] = record
            ri_to_dfi[record_i] = fi

print "n_records_unique", next_ri, "n_records", n_records
print "n_headers_unique", next_hi, "n_headers", n_headers
print "n_datafil_unique", next_fi, "n_datafil", n_d_files


# 1) first sort for swim...
data_ts = []

# 2) also group by studyid (need to go back and do this after..)
for i in range(0, next_ri):
    record = records_i[i]
    hdr = headers_i[ri_to_hi[i]]
    print "\nri", i, "src", d_files_i[ri_to_dfi[i]]
    wh = hdr.split(",")
    wr = record.split(",")

    if len(wh) != len(wr):
        #print "record", record
        # err("wh " + str(wh) + " wr " + str(wr))
        in_quotes = False
        chars = list(record)
        for j in range(0, len(record)):
            if chars[j] == '"':
                in_quotes = not in_quotes
            else:
                if in_quotes and chars[j] == ',':
                    chars[j] = ';'
        record = ''.join(chars)
        wr = record.split(",")

        if len(wh) != len(wr):
            print hdr
            print "record", record
            err("failed to remediate record")


    # "jsonified" record..
    #print "\t", hdr
    #print "\t", record
    d = {}
    for j in range(0, len(wh)):
        float_zero = False
        try:
            if(float(wr[j]) == 0.):
                float_zero = True
        except:
            pass # not a number

        if wr[j] == '' or float_zero or wr[j] == 'unspecified' or wr[j] == 'not applicable':
            pass
        else:
            d[wh[j]] = wr[j]

    src_df_n = d_files_i[ri_to_dfi[i]]

    # find date info for sorting
    yyyy_mm, mm, dd = '', '', ''
    if ('c_dobyyyy' in d and 'c_dobmm' in d): # births record
        print "births file"
        yyyy_mm = d['c_dobyyyy'] + d['c_dobmm']
    elif 'servdate' in d or 'dtofserv' in d:
        print "health file"
        servdate = d['servdate' if 'servdate' in d else 'dtofserv']
        yyyy_mm = servdate[0:6]
        dd = servdate[6:9]
    elif 'school_year' in d:
        print "education file"
        school_year = d['school_year']
        start, end = school_year[0:4], school_year[5:9]
        yyyy = end
    elif src_df_n[0:6] == 'births' and len(src_df_n.split(".icd.")) == 2:
        print "births icd file"
        fn_yyyy = src_df_n[6:10]
        if fn_yyyy == d['ver_year']:
            yyyy = fn_yyyy
    elif 'credential_issue_month' in d:
        print "credential file"
        cim = d['credential_issue_month']
        yyyy, mm = cim[0:4], cim[5:7]
    elif 'pc.srv_date' in d or 'de.srv_date' in d:
        sd = d['pc.srv_date' if 'pc.srv_date' in d else 'de.srv_date']
        yyyy, mm, dd = sd[0:4], sd[5:7], sd[8:10]
    elif 'demographics' == src_df_n[0:12]:
        yyyy, mm = d['dobyyyy'], d['dobmm']
    elif 'active_status_date' in d:
        asd = d['active_status_date']
        yyyy, mm, dd = asd[0:4], asd[5:7], asd[8:10]
    elif 'sepdate' in d:
        sd = d['sepdate']
        yyyy, mm, dd = sd[0:4], sd[5:7], sd[8:10]
    elif len(src_df_n.split('all_client_export.A')) > 1:
        # no date info in this table
        pass
    elif 'call_date' in d:
        print "mcfd file"
        cd = d['call_date']
        yyyy, mm, dd = cd[0:4], cd[4:6], cd[6:8]
    elif 'icmpid_cord' in d and 'locstart' in d:
        ls = d['locstart']
        yyyy, mm, dd = cd[0:4], cd[4:6], cd[6:8]
    elif 'icmpid_cord' in d and 'cym' in d:
        ls = d['cym']
        yyyy, mm = cd[0:4], cd[4:6]
    elif 'registry' == src_df_n[0:8]:
        continue
        yyyy = src_df_n[8:12]
    elif 'rpblite' == src_df_n[0:7]:
        continue
        yyyy = src_df_n[7:11]
    else:
        print "record", str(d)
        err("couldn't find date field for record")

    # default month: june
    if mm == '':
        mm = '06'

    if yyyy_mm == '':
        yyyy_mm = yyyy + mm

    # default day: 15th of month
    if (dd == ''):
        dd = '15'

    yyyy_mm_dd = (yyyy_mm + dd).strip()

    print '[' + yyyy_mm + dd +  "] " + str(d)

    if len(yyyy_mm_dd) == 8:
        data_ts.append([yyyy_mm_dd, d])


import operator
data_ts = sorted(data_ts, key=operator.itemgetter(0), reverse=False) # in time order


yc = {}
for i in range(0, len(data_ts)):
    ds = data_ts[i][0]
    yyyy = ds[0:4]
    if yyyy not in yc:
        yc[yyyy] = 0
    yc[yyyy] += 1

xx = []
for x in yc:
    y = yc[x]
    xx.append([x,y])
    # f.write('\n' + str(x) + ',' + str(y))

xx = sorted(xx, key=operator.itemgetter(0), reverse=False) # in time order

f = open('sup_cohort_sort.csv', 'wb')
f.write('year,records')
for x in xx:
     f.write('\n' + str(x[0]) + ',' + str(x[1]))
f.close()

# plt.plot(yy, xx)
# plt.show()
'''
for record in records:
    record_i = records[record]
    hdr_i = ri_to_hi[record_i]
    hdr = headers_i[hdr_i]
    print record_i, hdr, record
    '''

run("rscript R:/$USER/bin/R/csv_plot.R sup_cohort_sort.csv
