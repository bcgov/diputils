'''python3 make_fakedata.py'''
import string
import random
import calendar
from misc import *
from zipfile import ZipFile as zip_file
import csv_to_fixedwidth

debug = False  # turn on for extra info

# for each file, generate a random number of fake rows
min_rows, max_rows = 1000, 1000000
if len(sys.argv) >= 3:
    try:
        min_rows = int(sys.argv[1])
        max_rows = int(sys.argv[2])
    except Exception:
        err('failed to parse inputs')


# make fakedata folder
if not os.path.exists("fakedata") or not os.path.isdir("fakedata"):
    os.mkdir("fakedata")
else:
    print("done")
    sys.exit(0)

print("metadata,fakedata")
intersect, union = None, None
files = os.listdir('metadata')

# for each metadata file:
for f in files:
    f = f.strip()
    if f[-4:] != '.csv':
        continue

    ci = 0  # row index
    lookup = {}
    n_fields, hdr = 0, []
    data = []  # data rows for reuse
    row_type = {}  # type information for data

    fn = 'metadata' + os.path.sep + f
    with open(fn, encoding="utf8", errors='ignore') as csvfile:

        type_field_i = None  # index of 'Field Type' attribute, if it exists
        csvreader, is_header = csv.reader(csvfile, delimiter=','), True

        # for each row in metadata file: header or params on data field
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

                # existing field type info:
                # ['string', 'date', 'number', 'boolean']
                if 'Field Type' in hdr:
                    type_field_i = lookup['Field Type']
                data.append(row)
                ci += 1
            else:
                # process non-header row, if it is nonempty
                if len(row) != n_fields:
                    err("expected: " + str(n_fields) +
                        " got: " + str(len(row)))

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
                        rlfn = row[lookup['Field Name']]
                        if len(rlfn.lower().split("number")) > 1:
                            row_type[ci] = 'integer'
                        if len(rlfn.lower().split("_count")) > 1:
                            row_type[ci] = 'integer'
                        if len(rlfn.lower().split("amount")) > 1:
                            row_type[ci] = 'number'

                        # detect date type, if present within field name
                        if len(rlfn.lower().split("date")) > 1:
                            row_type[ci] = 'date'

                    if debug:
                        print("\t\t", row)

                    data.append(row)
                    ci += 1
            is_header = False  # already visited header

    # write fake data for this file
    ofn = 'fakedata' + os.path.sep + f.replace('_metadata', '')
    outfile = open(ofn, 'wb')

    print(fn + "," + ofn)

    # make the csv header
    csv_hdr = []
    for i in range(1, ci):
        try:
            field_name = data[i][lookup['Field Name']].strip().upper()
            field_name = field_name.replace(',', '_')
            csv_hdr.append(field_name)  # assume field names are upper-case
        except Exception:
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
    nrows_fake = random.randrange(min_rows, max_rows)

    # write a bunch of rows of fake data
    for j in range(0, nrows_fake):
        fakerow = []
        for i in range(1, ci):

            # simulate the type of data indicated for this field
            t = row_type[i]
            if t == 'date':
                fakerow.append(rand_date())
            elif t == 'integer' or t == 'number':
                fakerow.append(str(random.randrange(1, 200000)))
            elif t == 'boolean':
                fakerow.append('True' if random.randrange(0, 2) == 1
                               else 'False')
            else:
                # incl. 'string' case
                fakerow.append(rand_string())

        # write a row of fake data
        outfile.write(('\n' + ','.join(fakerow)).encode())

        if j % 1111 == 0 and nrows_fake > 1111:
            tick(j, nrows_fake, ofn)
    outfile.close()

    csv_to_fixedwidth.csv_to_fixedwidth(['csv_to_fixedwidth', ofn])
    # run('python3 csv_to_fw.py ' + ofn)

    ff_n = ofn[:-4] + '.dat'
    ddfn = ofn[:-4] + '.dd'
    zfn = ofn[:-4] + '.zip'

    # write zip file
    my_zip = zip_file(zfn, 'w')
    for f in [ff_n, ddfn]:
        my_zip.write(f)
    my_zip.close()

    # clean up unzipped files
    os.remove(ff_n)
    os.remove(ddfn)
