# list fields in a csv file
import sys
from misc import *

args = sys.argv
if len(args) < 2:
    err("usage: fields [input csv file name] [optional parameter: display vertically if present]")

fields = open(args[1]).readline().strip().split(",")

if len(args) <= 2:
    s = ""
    for f in fields:
        s += " " + f
    print s
else:
    for f in fields:
        print "  ", f.strip()
