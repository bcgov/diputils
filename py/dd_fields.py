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
''' list the fields in a cleaed dd file
'''
import os
import sys

if len(sys.argv) < 2:
    print "dd_fields.py [cleaned data dictionary file]"
    sys.exit(1)

lines = open(sys.argv[1]).read().strip().split('\n')
def pr(i):
    labels = []
    for line in lines:
        labels.append(line.strip().split(',')[i])
    s = ""
    for i in range(1, len(labels)):
        s += labels[i] + " "
    print s
print "field names:"
pr(3)
