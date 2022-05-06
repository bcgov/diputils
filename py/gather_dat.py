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
''' gather_dat.py (20190401):
      gather .dat files into a flat structure.
        Check for name collisions before executing!
          After, delete any empty subdirs'''
import os
import sys
import shutil

# default to present directory, if argument not supplied
pwd = os.getcwd() if len(sys.argv) <= 1 else sys.argv[1]

fn, tgt = {}, {}
# traverse subdirectories in filesystem tree
for r, d, f in os.walk(pwd):
        for _file in f:
            p = os.path.join(r,_file) # + os.linesep
            if os.path.isfile(p):
                fn[p] = 1 if not p in fn else fn[p] + 1
            tgt[p] = os.path.join(pwd, _file)

for p in fn:
    if not os.path.exists(tgt[p]):
        print p, "-->", tgt[p]
        shutil.move(p, tgt[p])
