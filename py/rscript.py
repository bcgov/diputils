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
'''a method of accessing R from within the SRE

Not sure if Path hell is overcome by other scripts'''
import os
import sys
from misc import *
if len(sys.argv) < 2:
    err("rscript.py: usage: [name of R file to run] [first parameter for R script] ...[last parameter for R script]")

# convert to a path that works!
r_path = '/cygdrive/c/Program Files/R/R-3.5.3/bin/Rscript.exe'

if not exists(r_path):
    r_path = '/cygdrive/c/Program Files/R/R-3.6.1/bin/Rscript.exe'

cmd = os.popen("(cygpath -d '" + r_path + "')").read().strip()
a = os.system(cmd + " " + " ".join(sys.argv[1:]))
