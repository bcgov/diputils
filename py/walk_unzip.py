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
'''20190104 traverse and unzip datasets'''
import os
import sys
import tarfile
from misc import *
# base = "R:\\" + os.popen("whoami").read().strip() + "\\"
# entry point to file system
args = sys.argv
if len(args) < 3:
    err("usage: walk_unzip.py [input directory] [output directory]")

pwd = args[1]
os.chdir(pwd)

# print "pwd", pwd
# ff = open(base + "log\\log_xls.txt", "wb")
c = 0
ext = {}

# search term example
search_term =  ".dat."
if len(args) >= 4:
    search_term = str(args[2])

search_override = len(args) < 4
count_records = False

xform  = args[2] # xform = base + "TRANSFORM\\"
xform = os.path.abspath(xform) + "\\"

# print "out",xform

if os.path.abspath(xform) == os.path.abspath(pwd):
    err("please enter paths explicitly")

if not os.path.exists(xform):
    os.mkdir(xform)

if not os.path.exists(xform):
    err("could not create: " + xform)

if not os.path.isdir(xform):
    err("")

# traverse present filesystem tree
for r, d, f in os.walk(pwd):
    for _file in f:
        # full path:filename for file/directory:
        p = os.path.join(r,_file) + os.linesep
        if search_override or p.count(search_term) > 0:
            # log all files and folders visited..
            # ff.write(p.encode('utf8'))

            # count file sizes
            c += os.stat(p.strip()).st_size

            fwords = _file.split(".")
            if len(fwords) > 1:
                e = fwords[-1]
                if e not in ext:
                    ext[e] = 1
                else:
                    ext[e] += 1
                if e!="gz":
                    continue

            # perform unzip
            p = p.replace("\\","/")
            z_file = p.strip()
            p = xform.replace("\\","/") + p[len(pwd):]
            # print p
            xf_dir = p.replace(pwd.replace("/","\\"), xform) # p.replace("DATA\\", "TRANSFORM\\")
            out_dir = xf_dir.strip().strip(".gz")+"/"
            #z_file = p.strip()
            #out_dir = os.path.abspath(out_dir) + "\\"
            #print "out_dir", out_dir
            if not os.path.exists(out_dir):
                words = out_dir.split("/")
                mypath = ""
                for i in range(0, len(words)):
                    mypath += words[i] + "\\"
                    if not os.path.exists(mypath):
                        #print "mypath", mypath
                        os.mkdir(mypath)

            # extract zip to folder
            cmd = '"C:\\Program Files\\7-Zip\\7z.exe" e ' + z_file.strip() + ' -o' + out_dir
            #z_file = z_file.replace("R:", "/cygdrive/r")
            #out_dir = out_dir.replace("R:", "/cygdrive/r/")
            #cmd = "tar xvf " + z_file + " --directory " + out_dir
            print(cmd)
            try:
                a = os.system(cmd)
            except:
                err("Error: failed to extract zipfile: " + z_file.strip())

print("TOTAL Selection Size (GB)" +str(c/1000000000.))
print("selected file  ext. count" + str(ext))
# ff.close()
