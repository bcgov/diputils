import os
import sys
import csv


def err(m):
    print("Error: " + m)
    sys.exit(1)


def run(cmd):
    a = os.system(cmd)
    if a != 0:
        err("command failed: " + cmd.strip())
    return a


