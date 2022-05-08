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

#!/usr/bin/env python2.7
''' ws.py: remove trailing whitespace and systematic left-whitespace'''
import os
import sys
import ntpath
from misc import *

args, max_spaces = sys.argv, 0
if len(args) < 2:
    msg = 'ws.py: usage: ws.py [input file name].\n\t'
    err(msg + 'removes trailing right-space and systematic left-space')

def f_base(fn):
    return ntpath.basename(fn)

try:
    fn = os.path.abspath(args[1].strip())
except:
    err('could not parse filename')

if not exists(fn):
    err('file [' + str(fn) + '] not found.')

lines = open(fn).readlines()
for i in range(0, len(lines)):
    lines[i] = lines[i].rstrip()
    l_i = lines[i]
    l_spaces = len(l_i) - len(l_i.lstrip())
    if(l_spaces > max_spaces):
        max_spaces = l_spaces

min_spaces = max_spaces
for i in range(0, len(lines)):
    l_i = lines[i]
    l_spaces = len(l_i) - len(l_i.lstrip())
    if(l_spaces < min_spaces):
        if(l_i.strip() != ''):
            min_spaces = l_spaces

print "min_spaces", min_spaces
head, tail = ntpath.split(fn)
head = head.strip() + '/'
head = os.path.abspath(head) + '/'
print 'head', head
bfn = fn + '.bak'  # head + '.' + f_base(fn)
print 'bfn', bfn

# save a backup
open(bfn, 'wb').write(open(fn).read())
printw(bfn)

write_ln = []
for i in range(0, len(lines)):
    line = lines[i]
    write_ln.append(line[min_spaces:])

# write the result.
open(fn, 'wb').write(('\n').join(write_ln))
printw(fn)
