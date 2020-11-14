import os
import sys
import csv
import time
import pickle

args = sys.argv


def err(m):
    print("Error: " + m)
    sys.exit(1)


def run(cmd):
    print(cmd)
    a = os.system(cmd)
    if a != 0:
        err("command failed: " + cmd.strip())
    return a


def exists(f):
    return os.path.exists(f)

def assert_exists(f):
    if not exists(f):
        err("could not find req'd file: " + str(f))

def load_fields_and_index_by_studyid(args): # load records and index by studyid
    print("load_fields " + str(args))
    dat, fn, load_fields = {}, args[0], args[1:]
    assert_exists(fn)
    f = open(fn)
    fields = f.readline().strip().split(",") # read the header
    field = {fields[i] : i for i in range(0, len(fields))}
    print("fields", fields)
    if len(args) == 1:
        load_fields = fields
    # not in Kansas anymore: comment out: # if 'studyid' not in fields: err("req'd field: studyid")
    # make sure other required fields are present
    for lf in load_fields:
        if lf not in fields: err("req'd field: " + str(lf))
    ci = 0
    while True:
        line = f.readline()
        if not line: break
        words = line.strip().split(",")
        i, loaded = words[field['studyid']], []
        if i not in dat: dat[i] = []
        for lf in load_fields:
            loaded.append(words[field[lf]])
        dat[i].append(loaded)
        ci += 1
    print("loaded ", ci, " records")
    return dat, load_fields


def printw(fn):
    print("+w " + fn.strip())

def printr(fn):
    print("+r " + fn.strip())


# open required output file, assert open
def wopen(fn):
    o_f = open(fn, "wb")
    if not o_f:
        err("failed to open output file: " + fn)
    printw(fn)
    return o_f

def ropen(fn):
    i_f = open(fn)
    if not i_f:
        err("failed to open input file: " + fn)
    printr(fn)
    return i_f


args = sys.argv

# calculate histogram for a list of values
def hist(x):
    h = {}
    for i in range(0, len(x)):
        d = x[i]
        if d not in h:
            h[d] = 0.
        h[d] += 1.
    return h




# stopwatch / progress meter
tick_last, tick_first = None, None

def tick(index=None, total=None, message=None):
    global tick_last, tick_first

    if tick_last is None:
        tick_last = time.time()
        tick_first = tick_last
    else:
        t = time.time()
        dt = t - tick_last
        tick_last = t
        pct = 100. * (index + 1) / total

        if index is not None and total is not None:
            elapsed = t - tick_first
            time_per_index = elapsed / (index + 1)
            expected_total_time = time_per_index * total
            eta = expected_total_time - elapsed
            message = '' if message is None else message
            info = ['\t', message,
                    '%', round(pct, 4), 'of', total,
                    'eta:', round(eta, 2), 's\n']
            sys.stderr.write(' '.join([str(i) for i in info]))
        else:
            print("dt", dt)


# move towards: "in-memory agnostic"

# determine whether parameter is a file or in-memory / data
class csv_reader: # benchmark it
    def __init__(self, data):
        self.ci = 0
        self.data = data
        self.fields = None
        self.n_fields = -1
        self.data_file = None
        csv.register_dialect('my',
                             delimiter = ",",
                             quoting = csv.QUOTE_ALL,
                             skipinitialspace = True)
        if type(data) == str:
            if exists(data):
                self.data_file = open(data)
            else:
                err("failed to open input file: " + data)
        else:
            if type(data) == list:
                self.data_file = None
            else:
                err("unknown data type: " + str(type(data)))

    def hdr(self):
        if self.data_file:
            fields = self.data_file.readline().strip().split(',')
            self.n_fields = len(fields)
            return fields
        else:
            return self.row()

    def row(self):
        line = (self.data_file.readline() if (self.data_file is not None)
                else (self.data[self.ci] if self.ci < len(self.data)
                else None))
        if not self.data_file:
            self.ci += 1
        if not line:
            return line
        fields = line.strip().split(',')
        if len(fields) == self.n_fields:
            return fields
        else:
            return [row for row in csv.reader([line])][0]


'''
r = csv_reader("test/test.csv")
fields = r.hdr()
print(fields)
while True:
    row = r.row()
    if row:
        print(row)
    else:
        break
'''
'''
r = csv_reader(["fieldname_bo,fieldname_bo", "mo,bo", "ho,zo", "fo,po"])
fields = r.hdr()
print(fields)
while True:
    row = r.row()
    if row:
        print(row)
    else:
        break
'''

