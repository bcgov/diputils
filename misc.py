import os
import sys
import csv
import time

args = sys.argv


def err(m):
    print("Error: " + m)
    sys.exit(1)


def run(cmd):
    a = os.system(cmd)
    if a != 0:
        err("command failed: " + cmd.strip())
    return a


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
