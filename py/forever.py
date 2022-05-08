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
'''forever.py: repeatedly execute a command every N-seconds..
..helpful for monitoring (large) output files as they are generated:
e.g:

    forever 1 ls -latrh
'''
import os
import sys
import time
from misc import *

default = 10
args = sys.argv
delay, arg = default, " ".join(args[1:])
if len(args) > 1:
    try:
        delay = int(args[1])
        arg = args[2:]
    except:
        pass

    print "sys.argv", args
    print "arg", arg

    cmds = " ".join(arg).split(";")
    print "cmds", cmds
    while(True):
        for c in cmds:
            print("\texec(" + c + ")")
            a = os.system(c)
            if a != 0:
                pass # could have a warning in here
        time.sleep(delay)
