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

# 20190910 transpose a csv file
from misc import *

if len(args) < 2:
    err("transpose.py: transpse csv\n\ttranspose [csv input file name")

lines = open(args[1]).readlines()
fields = lines[0].strip().split(',')
n_row = len(lines)

di = []
for i in range(0, len(lines)):
    di.append(lines[i].strip().split(','))

ofn = args[1] + "_transpose.csv"
o_f = wopen(ofn)

ci = 0
js = []
for j in range(0, len(fields)):
    js.append(j)

js.reverse()

for j in js:
    if ci > 0:
        o_f.write("\n")
    ci += 1

    datarow = [di[i][j] for i in range(0, len(lines))]
    o_f.write(','.join(datarow))

o_f.close()