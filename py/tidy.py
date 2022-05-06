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

# 20190711 : tidy up the folders by executing ws and dent
import os
import sys
from misc import *

if not (os.path.exists('R') and os.path.exists('c') and os.path.exists('cpp') and os.path.exists('py')):
    err("must execute from within bin folder")

py = os.popen("find ./ -name '*.py'").readlines()
py = [py[i].strip() for i in range(0, len(py))]
for p in py:
    run("ws " + p)

c = os.popen("find ./ -name '*.cpp'").readlines()
c = [c[i].strip() for i in range(0, len(c))]
for cc in c:
    run("dent " + cc)
    run("ws " + cc)

c = os.popen("find ./ -name '*.c'").readlines()
c = [c[i].strip() for i in range(0, len(c))]
for cc in c:
    run("dent " + cc)
    run("ws " + cc)