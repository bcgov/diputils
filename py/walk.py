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
import sys
'''20190104 walk.py
traverse subfolders: find XLS metadata or files matching a pattern. This script
intented to be followed by by walk_unzip.py which would open the data. A subsequent
application would apply data dictionaries
'''
# entry point to file system
args = sys.argv
if len(args) < 2:
    pwd = os.getcwd()
else:
    os.chdir(args[1])
    pwd = os.getcwd()

c = 0L
ext = {}

# search term
search_term = None
if len(args) < 2:
    search_term =  "pharmacare2"
else:
    search_term = str(args[2])

search_override = len(args) < 2  #False # True # set True to ignore search term
count_records = False # True

# count records, lines in a CSV file
def wc(fn):
    f = open(fn)
    line = f.readline().split(",")
    n_fields = len(line); n_line = 0
    while True:
        line = f.readline()
        if not line: break
        n_line +=1
    print "\t", n_fields,"fields", n_line,"lines"
    return n_fields, n_line

# traverse present filesystem tree
for r, d, f in os.walk(pwd):
    for _file in f:
        # full path:filename for file/directory:
        p = os.path.join(r,_file) + os.linesep
        if search_override or p.count(search_term) > 0:
            print(p.strip())

            fwords = _file.split(".")

            if len(fwords) > 1:
                # count file sizes
                c += os.stat(p.strip()).st_size
                e = fwords[-1]
                ext[e] = ext[e] + 1 if (e in ext) else 1

                if count_records:
                    if e=="csv": # or e=="dat": is dat fixedwidth?
                        n_fields, n_line = wc(p)
                        print(str(p) + "," + str(n_fields) + "," + str(n_line) + "\n")

print("TOTAL Selection Size (GB)" + str(c/(1024. * 1024. * 1024.)) + " bytes: " + str(c) + " MB " + str(c / (1024. * 1024.)))
print("selected file  ext. count" + str(ext))

e = []
for ee in ext:
    e.append([ext[ee], ee])

e.sort(reverse=True)
print("")
print("Number of files selected, by extension:")
for ee in e:
    print("\t"+str(ee[1]) + "," + str(ee[0]))

# how to use unix find without showing a bunch of irrelevant messages: > find ./ -name "*.*" 2>&1 | grep -v "Permission denied"
