# write new version of csv with numbered (not named) fields
import os
import sys
args = sys.argv

lines = open(args[1]).readlines()
lines = [line.strip() for line in lines]

hdr = lines[0].split(',')
hdr = ','.join([str(i) for i in range(len(hdr))])

open(args[1] + "_numbered_fields.csv", "wb").write(('\n'.join(lines)).encode())
