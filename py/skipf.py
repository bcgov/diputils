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
'''data subsampling by skip factor'''
from misc import *

if len(args) < 3:
    err("\n\tskipf [csv file] [skip factor]")

in_f = args[1]
skip_f = int(args[2])

print "input file: ", in_f
print "skip factor: ", skip_f

lines = open(in_f).readlines()

out_f = open(in_f + '_skipf.csv', 'wb')

if not out_f:
    err("failed to open output file")

out_f.write(lines[0].strip())

rc = 0
for i in range(1, len(lines)):
    if i % skip_f == 0:
        out_f.write('\n' + lines[i].strip())
        rc += 1

out_f.close()

print "non-header data lines written: ", rc
