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
'''get and unzip most recent SRE datafile
'''
import pickle
from misc import *
args = sys.argv

if len(args) < 2:
    err("get and unzip most recent datfile\nusage:\n\tdf_get [dat file name: .gz or .dat]")

if not os.path.exists("recent_datfile_names.p"):
    run("df_list")

[recent_datfile_names] = pickle.load(open("recent_datfile_names.p"))

fn = args[1]
if fn not in recent_datfile_names:
    fn = fn + ".gz"
if fn not in recent_datfile_names:
    err(args[1] + " not found")

remote = recent_datfile_names[fn]
run("cp -v " + remote + " .")
run("unzp " + fn)
