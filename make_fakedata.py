'''python3 make_fakedata.py'''
debug = False # turn on for extra info

import string
import random
import calendar
from misc import *

print("metadata,fakedata")
intersect, union = None, None
files = os.popen('ls -1 metadata/')

# for each metadata file:
for f in files:
    f = f.strip()

    ci = 0 # row index
    lookup = {}
    n_fields, hdr = 0, []
    data = [] # data rows for reuse
    row_type = {} # type information for data

    fn = 'metadata/' + f
    with open(fn, encoding="utf8", errors='ignore') as csvfile:

        type_field_i = None # index of 'Field Type' attribute, if it exists
        csvreader, is_header = csv.reader(csvfile, delimiter=','), True
        
        # for each row in metadata file: header or row with parameters on data field
        for row in csvreader:
            row = [r.strip() for r in row]

            # process header
            if is_header:
                hdr, n_fields = row, len(row)
                lookup = {hdr[i]: i for i in range(0, len(row))}
                if debug:
                    print(n_fields, row, fn)

                if intersect is None:
                    intersect, union = set(row), set(row)
                else:
                    intersect = intersect.intersection(set(row))
                    union = union.union(set(row))

                # expect a field 'Field Name'
                if 'Field Name' not in hdr:
                    err('expected field: "Field Name"')
                
                # existing field type info ['string', 'date', 'number', 'boolean']
                if 'Field Type' in hdr:
                    type_field_i = lookup['Field Type']
                data.append(row)
                ci += 1
            else:
                # process non-header row, if it is nonempty
                if len(row) != n_fields:
                    err("expected: " + str(n_fields) + " got: " + str(len(row)))

                # skip empty row
                empty_row = True
                for i in range(0, len(row)):
                    if row[i] != '':
                        empty_row = False

                if not empty_row:
                    if type_field_i is not None:
                        row_type[ci] = row[type_field_i].lower().strip()
                    else:
                        # assume string with some name-based overrides
                        row_type[ci] = 'string'

                        if len(row[lookup['Field Name']].lower().split("number")) > 1:
                            row_type[ci] = 'integer'
    
                        if len(row[lookup['Field Name']].lower().split("amount")) > 1:
                            row_type[ci] = 'number'

                        # detect date type in the event date is present within field name
                        if len(row[lookup['Field Name']].lower().split("date")) > 1:
                            row_type[ci] = 'date'

                    if debug:
                        print("\t\t", row)

                    data.append(row)
                    ci += 1
            is_header = False # already visited header

    # write fake data for this file
    ofn = 'fakedata/' + f.replace('_metadata', '')
    outfile = open(ofn, 'wb')

    print(fn + "," + ofn)

    # make the csv header
    csv_hdr = []
    for i in range(1, ci):
        try:
            field_name = data[i][lookup['Field Name']].strip().upper()
            field_name = field_name.replace(',','_')
            csv_hdr.append(field_name) # assume field names are upper-case
        except:
            err('failed to parse field name')

    # write the csv header
    outfile.write((','.join(csv_hdr)).encode())


    def rand_date():
        year = random.randrange(1985, 2021)
        mont = random.randrange(1, 13)
        rng = calendar.monthrange(year, mont)
        day = random.randrange(rng[0], rng[0] + rng[1])
        return('-'.join([str(s) for s in [year, mont, day]]))


    def rand_string():
        r = ''
        for i in range(0, random.randrange(1, 11)):
            r += random.choice(string.ascii_letters)
        return(r)

    # random number of fake rows
    nrows_fake = random.randrange(1, 1000000)

    # write a bunch of rows of fake data
    for j in range(0, nrows_fake):
        fakerow = []
        for i in range(1, ci):
            t = None
            try:
                t = row_type[i]
            except:
                print("row_type", str(row_type), "ci", ci, "i", i, "nfields", n_fields)
                err('')

            if t == 'date':
                fakerow.append(rand_date())
            elif t == 'integer' or t == 'number':
                fakerow.append(str(random.randrange(1,200000)))
            elif t == 'boolean':
                fakerow.append('True' if random.randrange(0,2) == 1 else 'False')
            else:
                # incl. 'string' case
                fakerow.append(rand_string())

        # write a row of fake data
        outfile.write(('\n' + ','.join(fakerow)).encode())
    outfile.close()
