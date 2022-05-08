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
'''grep a csv file for an expression and copy the csv header into the output
'''
import os
import sys
from misc import *

if len(sys.argv) < 3:
    err("usage: csv_grep [pattern] [input csv file]")

pattern, filename = sys.argv[1], sys.argv[2]
grep_file = filename + "_grep" # grep results go here
a = os.system("grep " + pattern + " " + filename + " > " + grep_file)

f = open(filename)
fields = f.readline().strip() + "\n"
f.close()
fields_file = filename + "_fields" # names of fields go in this file
open(fields_file, "wb").write(fields)

a = os.system("cat " + fields_file + " " + grep_file + " > " + filename + "_grep_" + pattern + ".csv")
run("rm -f " + grep_file)
run("rm -f " + fields_file)
