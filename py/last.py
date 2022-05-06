'''computing a graduation related statistic
'''
import os, math, pickle
gr12_yr = {} # last year of grade 12 for a person
if not os.path.exists("gr12_yr.p"): # registration for nongrad (excluded people in the student credit file):
    'idomed1991-2017.ft_schlstud.A.dat_dd_sliceapply.csv_select(exclude).csv'

    # nongrad reg for grade 12 (the above for gr 12 only)
    f = open('idomed1991-2017.ft_schlstud.A.dat_dd_sliceapply.csv_select(exclude)_gr12.csv')

    # want last reg for grade 12
    fields = f.readline().strip().split(",") # read the header
    field = {fields[i] : i for i in range(0, len(fields))}
    print(fields)

    j = 0
    while True: # for each line
        line = f.readline() # read line by line
        if not line: break # exit loop if no more lines       
        words = line.strip().split(",")
        i = words[field['studyid']] # studyid 
        # school year for june
        year = int(words[field['school_year']].split("/")[1]) # school year for jun
        # most recent grade 12 year
        gr12_yr[i] = year if i not in gr12_yr else (year if year > gr12_yr[i] else gr12_yr[i])
        j += 1 
    f.close()
    # do the pickling
    pickle.dump(gr12_yr, open('gr12_yr.p', 'wb')) # , encoding='utf8'))
else:
    #restore the pickle
    gr12_yr = pickle.load(open('gr12_yr.p', 'rb')) #encoding='utf8'))

msp_dates = {} # key = studyid, value = list of date ranges
if not os.path.exists('msp_dates.p'):
    # registry for nongrads (selected using the above file): all registry data for people in education who didn't graduate! Multiple records per studyid
    f = open('registry1991-2016_dd_apply_csv_slice_cat.csv_select.csv')
    fields = f.readline().strip().split(",") # read the header
    field = {fields[i] : i for i in range(0, len(fields))}
    print(fields)
    # ['startday', 'daysreg', 'year', 'studyid']

    # for nongrads that had grade 12 edc. registration:
    #    want to find them in the MSP registry and see if they were covered on Jun. 30 of the gr12 year:
    # we had a map gr12_yr: (i -> gr12_yr[i] is a map where the key is studyid and the value is year registered for gr_12 (if any))

    # now we're calculating the msp date ranges (if available) for that person, for the gr12 year (if it exists)
    # we are not storing the whole msp registry file in ram. we are only putting in RAM, date ranges for applicable students, for the gr12 year (if it exists)

    while True: # for each line
        line = f.readline()
        if not line: break 
        words = line.strip().split(",")
        msp_year = int(words[field['year']])
        i = words[field['studyid']] # studyid
        #print(str(i) + "," + str(msp_year) + "," + (str(gr12_yr[i]) if i in gr12_yr else "N/A"))
        gr12_yr_i = None if i not in gr12_yr else gr12_yr[i] # the grade 12 year for this person, if they had one
        if gr12_yr_i is None: continue # no gr12 data for this person (this might be N/A answer.. check later)
        if msp_year != gr12_yr[i]: # only want data from this msp record, if it was for the gr12 year
            continue # go to next iteration of loop (go back to line = f.readline())
        daysreg = int(words[field['daysreg']])
        if daysreg < 1: continue

        start_day = int(words[field['startday']])
        end_day = start_day + int(words[field['daysreg']]) - 1
        date_range = [gr12_yr_i, start_day, end_day]
        # print(str(i) + ',' + str(start_day) + "," + str(end_day) + "," + str(date_range))
        if i not in msp_dates:
            # don't have a list of msp dates for that person yet..
            msp_dates[i] = [] # start an empty list for them

# doesn't need to be in the condition because if a list wasn't there, we just added one:
        msp_dates[i].append(date_range) # add the date range we found, to the list..
    pickle.dump(msp_dates, open('msp_dates.p', 'wb'))
else:
    msp_dates = pickle.load(open('msp_dates.p','rb'))


import datetime
def jun30(year):
    jan1 = datetime.datetime(year, 1, 1)
    jun30 = datetime.datetime(year, 6, 30)
    d = datetime.timedelta(1) + jun30 - jan1
    return int(str(d).split(',')[0].split()[0])

j = 0
for i in msp_dates:
    # for this student, find out if msp said they were in BC on jun30:

    in_bc = False
    for date_range in msp_dates[i]:
        print(date_range)
    
    j += 1
    if j > 50:
        import sys; sys.exit(1)
