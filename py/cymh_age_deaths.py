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
definition of study pop includes: April 1, 2001 to March 31, 2017
'''
import os
import sys
import datetime
from misc import *

# start by slicing out fields of interest
table = "merge_table_with_clusters_13September2019.csv"
if len(args) > 1:
    table = args[1]
    if not exists(table):
        err("input file not found: " + table)

slice_table = table + '_slice.csv'
slc_args = ['csv_slice', table, 'dob dod cluster_id_from_hdb']
if not exists(slice_table): run(' '.join(slc_args))

lines = open(slice_table).readlines()
hdr, lines = lines[0].strip().split(','), lines[1:]
f_i = {hdr[i]: i for i in range(0, len(hdr))}

pop_size, deaths = len(lines), 0
deaths_cluster = {i: 0 for i in range(-1, 6)}
n_cluster = {i: 0 for i in range(-1, 6)}

n_age, age, age_cluster =0, 0, {i: 0 for i in range(-1, 6)}
n_age_cluster = {i: 0 for i in range(-1, 6)}

n_age_death, age_death, age_death_cluster = 0, 0, {i: 0 for i in range(-1, 6)}
n_age_death_cluster = {i: 0 for i in range(-1, 6)}

min_age, max_age = None, None
min_age_cluster = {i: None for i in range(-1, 6)}
max_age_cluster = {i: None for i in range(-1, 6)}

for i in range(0, pop_size):
    d  = lines[i]
    w = d.strip().split(",")
    w = [w[j].strip() for j in range(0, len(w))]

    # reference date
    refdate = datetime.datetime(2017, 3, 31)

    dob, dod = w[f_i['dob']].split('-'), w[f_i['dod']].split('-')
    idx = int(w[f_i['cluster_id_from_hdb']])
    n_cluster[idx] += 1

    # convert to int
    dob = [int(d) for d in dob]
    try: dod = [int(d) for d in dod]
    except: pass

    age_at_death = None
    secs_per_year = 60. * 60. * 24 * 365.
    dob = datetime.datetime(dob[0], dob[1], dob[2])
    age_at_refdate_if_alive = ((refdate - dob).total_seconds()) / secs_per_year

    if len(dod) > 1:
        dod = datetime.datetime(dod[0], dod[1], dod[2])
        deaths += 1
        deaths_cluster[idx] += 1
    dod_ts = str(type(dod)).strip()

    if not (dod_ts == "<class 'datetime.datetime'>" or dod_ts == "<type 'datetime.datetime'>"):
        # didn't die
        n_age += 1
        age += age_at_refdate_if_alive

        n_age_cluster[idx] += 1
        age_cluster[idx] += age_at_refdate_if_alive

        min_age = age_at_refdate_if_alive if min_age is None else min_age
        max_age = age_at_refdate_if_alive if max_age is None else max_age

        min_age = age_at_refdate_if_alive if age_at_refdate_if_alive < min_age else min_age
        max_age = age_at_refdate_if_alive if age_at_refdate_if_alive > max_age else max_age

        min_age_cluster[idx] = age_at_refdate_if_alive if min_age_cluster[idx] is None else min_age_cluster[idx]
        max_age_cluster[idx] = age_at_refdate_if_alive if max_age_cluster[idx] is None else max_age_cluster[idx]

        min_age_cluster[idx] = age_at_refdate_if_alive if age_at_refdate_if_alive < min_age_cluster[idx] else min_age_cluster[idx]
        max_age_cluster[idx] = age_at_refdate_if_alive if age_at_refdate_if_alive > max_age_cluster[idx] else max_age_cluster[idx]
    else:
        # died
        age_at_death = (dod - dob).total_seconds() / secs_per_year

        n_age_death_cluster[idx] += 1
        age_death_cluster[idx] += age_at_death

        if dod < refdate:
            n_age += 1
            age += age_at_refdate_if_alive

            n_age_cluster[idx] += 1
            age_cluster[idx] += age_at_refdate_if_alive
        else:
            n_age_death += 1
            age_death += age_at_death

# age range, mean for members in ref date
log = open('age_deaths.csv', 'wb')
log.write("statistic,cluster_label,value".encode())

def wl(dat): # write to log
    global log
    s = '\n' + ','.join([str(d) for d in dat])
    log.write(s.encode())

# deaths for each cluster and studypop as a whole
wl(['death_total', '', deaths])
wl(['age_refdate_min', '', min_age])
wl(['age_refdate_max', '', max_age])
wl(['age_refdate_avg', '', age / n_age])
wl(['age_death_avg', '', age_death / n_age_death])

for i in deaths_cluster:
    wl(['n_deaths', i, deaths_cluster[i]])
    wl(['cluster_size', i, n_cluster[i]])
    wl(['deaths_as_percent_of_cluster_size', i, round(100. * deaths_cluster[i] / n_cluster[i], 3)])
    wl(['age_refdate_min', i, min_age_cluster[i]])
    wl(['age_refdate_max', i, max_age_cluster[i]])
    wl(['age_refdate_avg', i, age_cluster[i] / n_age_cluster[i]])
    try:
        wl(['age_death_avg', i, age_death_cluster[i] / n_age_death_cluster[i]])
    except:
        pass

log.close()
