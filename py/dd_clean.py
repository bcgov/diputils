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
import os
import sys
import csv
from misc import *
''' Workflow: 
#   1) dd_list.py
#   2) dd_apply.py
#   3) dd_clean.py
#   4) dd_examine.py
Yikes some bad programming style in this! Learned a lot since I wrote this.'''
csv.register_dialect('my', delimiter=",", quoting=csv.QUOTE_ALL, skipinitialspace=True)
if not os.path.exists('./dd/') or not os.path.isdir('./dd/'):
    err("run dd_list.py first")

print "cleaning data dictionaries"

# traverse present filesystem tree
for r, d, f in os.walk('./dd/'):
    for ff in f:
        print ff.strip()
        if len(ff.strip().split(' ')) > 1:
            cmd = "mv ./dd/'" + ff.strip() + "' ./dd/" + ff.strip().replace(' ','_')  +  " "
            print "***", cmd
            a = os.system(cmd)

csvf = os.popen('find ./dd/ -name "*.csv"').read().strip().split("\n")

for i in range(0, len(csvf)):
    csvf[i] = csvf[i].strip()
    cleanlines = []
    #print "\t", csvf[i]
    lines = open(csvf[i]).read().strip().replace('\r\n',';').split('\n')

    def clean(s):
        return s.strip().replace('"','').strip(',').strip()
    lines[0] = clean(lines[0])
    fields = lines[0].split(',')
    nf = len(fields)
    for j in range(0, len(fields)):
        fields[j] = fields[j].strip().strip('"').strip()
    cleanlines.append(','.join(fields))

    # print "\t\t" + str(fields)
    for j in range(1, len(lines)):
        lines[j] = lines[j].replace("''", '').replace("'\'",'').replace('""','')
        # lines[j] = clean(lines[j])
        w = lines[j].split(',')

        if len(w) != nf:
            open("./.tmp1234.csv","wb").write(",".join(fields)+"\n"+lines[j])
            tf = open("./.tmp1234.csv")
            reader = csv.reader(tf, dialect='my')
            hdr, w = reader
            tf.close()
        if len(w) != nf and w[0].strip().strip('"').strip() == str(j):
            w = w[1 : nf + 1]
        if len(w) != nf:
            print "Error: ", w
            print len(w), nf
            print [lines[j]]
            print [lines[j+1]]
            print [lines[j+2]]
            sys.exit(1)
        for k in range(0, len(w)):
            w[k] = w[k].strip().strip('"').strip()
            w[k] = w[k].replace(',',';')
        cleanlines.append(','.join(w))
    open(csvf[i] + "2", "wb").write('\n'.join(cleanlines))

print "verifying apparent cleanliness..."

csvf = os.popen('find ./dd/ -name "*.csv2"').read().strip().split("\n")
for i in range(0, len(csvf)):
    f = csvf[i] = csvf[i].strip()
    print "\t",f
    lines = open(f).read().strip().split('\n')
    fields = lines[0].strip().split(',')

    for i in range(1, len(lines)):
        if len(lines[i].split(',')) != len(fields):
            err("")

print "pass"
a = os.system("rm -f ./.tmp1234.csv")
a = os.system('rm -f ./dd/*.csv')
