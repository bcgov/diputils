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
'''Open a bunch of data dictionary cleaned files, in a loop:

# examine data dictionary cleaned files, after processing by:
#   1) dd_list.py
#   2) dd_apply.py
#   3) dd_clean.py
#   4) dd_examine.py
'''
import os
import sys

fn = os.popen('ls -1 ./dd/*.csv2')

for f in fn:
    f = f.strip()
    a = os.system('vi ' + f)
