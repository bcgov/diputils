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

# qc by checking number of fields per line
import os
import sys
f = open("School_Student.csv","rb")
ci = 0
line_last, nfl = None, None
while True:
    line = f.readline()
    if line.strip() == "": continue
    if not line:
        break
    lines = line.strip().split(",")
    nf = len(lines)
    #print nf

    ##if nf != 63:
    #    print nf, line

    ci += 1

    if nf != 63:
        print nf
        print line

    line_last = line
    nfl = nf
    #if ci > 500:
    #    break