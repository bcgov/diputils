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
''' 20190725  convert nflt (sdpr, mcfd) data dictionaries:
to match the csv format used by EDUC and HLTH '''
from misc import *
from ansicolor import *

if len(args) < 2:
    err("dd_convert_nflt_to_csv2 [input file .nflt]")

fn = args[1]

lines = open(fn).read().strip().split("\n")
n_fields = len(lines) - 1 # assuming the file has the kind of integrity we expect
dat = [lines[i].strip().split() for i in range(0, len(lines))]
hdr, dat = dat[0], dat[1:]
fixedw_nchar = None
try:
    fixedw_nchar = int(hdr[0])
except:
    err("failed to parse nflt file")
if hdr[1] != "*":
    err("unexpected nflt format")

print "hdr", hdr

last_stop = -1
out_lines = ["Start,Stop,Length,Name Abbrev"]
whack = False
check_rows = []
for i in range(0, len(dat)):
    #print dat[i], "input"
    di = dat[i]
    start, length, name = di[0], di[1], di[3]
    if i > 0 and not (int(start) == last_stop + 1):
        whack = True
        check_rows.append(i)
    start = int(start) if i == 0 else (last_stop +1)
    stop = (int(start) + int(length) - 1)
    last_stop = stop
    nsl = name.strip().lower()

    if nsl == 'eol':
        name = 'LINEFEED'
    # if nsl == 'linefeed': # or nsl == 'eol':
    #     continue
    out_rec = [str(start), str(stop), str(length), str(name)]
    out_lines.append(",".join(out_rec))
    #print "\t", out_rec
out_dat = "\n".join(out_lines).strip()

if whack:
    print("ERROR: nflt file is WHACK: " + fn)
    print("check rows: " + str(check_rows))
    for i in range(0, len(dat)):
        print i, dat[i]

ofn = fn + ".csv2"
try:
    outf = open(ofn, "wb")
    outf.write(out_dat)
    outf.close()
except:
    err("failed to write output file")

if len(out_dat.lower().split('studyida')) > 1:
    run('dd_reintegrate_studyid ' + ofn)
