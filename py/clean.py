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
'''updated 2019/03/13: clean up messy files: e.g., *~, .swp, .bak, .exe'''
import os
import sys
from misc import *

def yes_no(question):
    while True:
        reply = str(raw_input(question+' (y/n): ')).lower().strip()
        return True if reply[0] == 'y' else False

def find(ext):
    ret = {}
    cmd = 'find ./ -name "*' + ext + '"'
    lines = os.popen(cmd).read().strip().split("\n")
    for f in lines:
        ff = f.strip()
        if ff != "":
            ret[ff] = ""
    cmd = 'find ./ -name ".*' + ext + '"'
    lines = os.popen(cmd).read().strip().split("\n")
    for f in lines:
        ff = f.strip()
        if ff != "":
            ret[ff] = ""
    return ret

d = { }
for e in ["~", ".swp", ".bak", ".exe", ".pyc", "__pycache__"]:
    f = find(e)
    for ff in f:
        d[ff] = ""

if len(d) == 0:
    sys.exit(0)

for f in d:
    print(f.strip())

print("")

cmds = []
if yes_no("\ndelete the above files?"):
    for f in d:
        if os.path.exists(f):
            cmd = 'rm -rf "' + f + '"'
            cmds.append(cmd)

open("clean_jobs.sh", "wb").write("\n".join(cmds))
run("multicore clean_jobs.sh")
run("rm -f clean_jobs.sh") # clean up
