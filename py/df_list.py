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
''' 20190725 list data ".dat" files '''
import os
import sys
import pickle
from misc import *
debug = False

datafiles = []
recent_datfile_names = {}

if not os.path.exists("datafiles.p"):
    pwd = "R:/DATA/"
    # traverse present filesystem tree
    for root, folder, files in os.walk(pwd):
        for f in files:
            p = (os.path.join(root, f) + os.linesep).strip() # full path for file/folder
            if p[-3:] == '.gz': datafiles.append([os.stat(p).st_size, p])
    datafiles = sorted(datafiles, key=lambda x: x[0], reverse=False) # smallest first
    pickle.dump([datafiles], open("datafiles.p", "wb"))
else:
    [datafiles] = pickle.load(open("datafiles.p"))

[files] = pickle.load(open("datafiles.p", "rb"))
# get modification times
mtime = {}
datfile_names = {}

if not os.path.exists("recent_datfile_names.p"):
    for f in files:
        s = str(f[1]).strip()
        s = os.path.normpath(s)
        mtime[s] = os.path.getmtime(s)
        #print(s, mtime[s])
        datfile_name = s.split("\\")[-1]
        if datfile_name not in datfile_names:
            datfile_names[datfile_name] = []
        datfile_names[datfile_name].append(s)
    # pick most recent mod time
    for datfile_name in datfile_names:
        if debug:
            print(datfile_name)
        ci, maxi = 0, 0
        for d in datfile_names[datfile_name]:
            if debug:
                print("\t" + str(mtime[d]) + " " + str(d))
            if ci == 0: maxi= d
            else:
                if mtime[d] > mtime[maxi]: maxi = d
            ci += 1
        if debug:
            print("\t**** " + str(mtime[maxi]) + " " + str(maxi))
        recent_datfile_names[datfile_name] = maxi
    pickle.dump([recent_datfile_names], open("recent_datfile_names.p", "wb"))
else:
    [recent_datfile_names] = pickle.load(open("recent_datfile_names.p"))

print("number of data files: " + str(len(files)))
print("number of unique data files: " + str(len(recent_datfile_names)))
