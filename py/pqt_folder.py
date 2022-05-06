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

# 20190617 apply pqt (faux parquet) command to all files in a folder
import os
import sys
from misc import *

if len(sys.argv) != 1:
    err("apply pqt.cpp to all files in present folder.")

run("mkdir pqt")

files = os.popen("ls -1 *csv*").readlines()

for f in files:
    run("pqt " + f.strip())

run("mv -v *.pqt pqt")

# new pattern: commands always produce results in a (sub) folder,
# where the subfolder has the name of the command applied : )
