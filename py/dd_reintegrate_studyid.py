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

from misc import *

if len(args) < 2:
    err("dd_reintegrate_studyid [csv2 file]")

fn = args[1]
if fn.split('.')[-1] != 'csv2':
    err("supposed to be run on csv2 file")

out_lines = []
dat = open(fn).read().strip().split("\n")
for i in range(0, len(dat)):
    w = dat[i].strip().split(',')
    if w[-1].lower() == 'studyida':
        continue
    if w[-1].lower() == 'studyid':
        if dat[i + 1].strip().split(',')[-1].lower() == 'studyida':
            out_lines.append(','.join([w[0], str(int(w[0]) + 9), str(10), 'STUDYID']))
    else:
        out_lines.append(','.join(w))
open(fn, 'w').write('\n'.join(out_lines))
