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

def load_fields(args): # load records and index by studyid
    print("load_fields " + str(args))
    dat, fn, load_fields = {}, args[0], args[1:]
    assert_exists(fn)
    f = open(fn)
    fields = f.readline().strip().split(",") # read the header
    field = {fields[i] : i for i in range(0, len(fields))}
    print("fields", fields)
    if 'studyid' not in fields: err("req'd field: studyid")
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
