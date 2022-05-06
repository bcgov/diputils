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

import os
'''20190104 find.py: directory/ files listing, recursive (before we learned
cygwin available'''
from misc import *

file_types = ["py", "R", "Rmd", "md", "cpp", "c", "h", "bat", "sh", "js", "Rhistory"]
args = sys.argv
if len(args) < 2:
    err("usage: find [path]")

pwd = sys.argv[1].strip()
if not os.path.exists(pwd) and not os.path.isdir(pwd):
    print "Error: directory does not exist", pwd

log = wopen('count_code.csv')
log.write('lines,bytes,file,ext')
ext = {}
count = {} # count lines
bcount = {} # count bytes
for r, d, fs in os.walk(pwd):
    for f in fs:
        # output full path
        p = os.path.join(r,f) + os.linesep # print p.strip()

        # file-ext count
        fw = f.split(".")
        if len(fw) > 1:
            e = fw[-1]
            if e in file_types:
                lc = os.popen("lc " + p.strip()).read().strip()
                fs = str(os.stat(p.strip()).st_size)
                log.write('\n' + ','.join([lc, fs, os.path.abspath(p.strip()), e]))
                ext[e] = ext[e] + 1 if (e in ext) else 1
                count[e] = count[e] + int(lc) if (e in count) else int(lc)
                bcount[e] = bcount[e] + int(fs) if (e in bcount) else int(fs)

print count
e = [[ext[ee],ee] for ee in ext]

e.sort(reverse=True)
print ""
print "file count, by extension, line count"
for ee in e:
    s = "\t"+ (','.join([str(ee[1]), str(ee[0]), str(count[ee[1]])]))
    print s
log.close()

log = wopen("code_count_total.csv")
log.write("filetype,lines,bytes")
total_lines = 0
for e in file_types:
    total_lines += count[e]
    log.write("\n" + ','.join([str(e), str(count[e]), str(bcount[e])]))
log.close()

print "total lines of code," + str(total_lines)
