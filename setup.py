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

#!/usr/bin/env python
import os
import sys
from py.misc import *
from py.ansicolor import *

print("py/setup.py..")

job_file = open("compile_jobs.sh", "wb")
clean_file = open("clean_jobs.sh", "wb")

def add_job(cmd):
    job_file.write((cmd + "\n").encode())

def add_clean_job(cmd):
    clean_file.write((cmd + "\n").encode())

# need to be able to detect python, R, and vim (if exist)
# need to do the wrapping (as we did for py) for R programs, too!

sys_s, sys_n = os.popen("uname -a").read().strip().lower(), None
if sys_s[0:6] == 'cygwin': sys_n = 'cygwin'
elif sys_s[0:5] == 'mingw': sys_n = 'mingw'
elif sys_s[0:5] == 'linux': sys_n = 'linux'
else: err("system type: " + sys_s.split()[0] + " not yet supported")

file_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))  # where the file is
pwd = os.popen("pwd").read().strip()

if sys_n == "cygwin": pwd = os.popen("cygpath -w -a ./").read().strip()

work_dir = os.path.abspath(pwd)
if not file_dir == work_dir: err("file dir: " + file_dir + "\nwork_dir: " + work_dir + "\nrun setup.py from the directory it's in")

build = sys.argv[1] if len(sys.argv) > 1 else None # if len(sys.argv) > 1: build = sys.argv[1]
user_name = os.popen("whoami").read().strip()

# need to actually adjust these for the python / R vim paths found..
profile = ['alias vim="/cygdrive/c/Program\ Files\ \(x86\)/Vim/vim81/vim.exe"',
           'alias Rscript="/cygdrive/c/Program\ Files/R/R-3.5.2/bin/Rscript.exe"',
           'alias python="/cygdrive/c/Program\ Files/Python35/python/" #alias python="/cygdrive/c/Python27/python.exe"',
           'export PATH="$PATH:$(pwd)"']

compiled = {}
line_count = 0

def compile(f):
    print("compile " + f)

    f = f.strip()
    global build, compiled
    ext = f.strip().split('.')[-1].strip()
    fn = f.split('/')[-1].strip().split('.')[0]
    # print("fn", fn)
    if ext == 'py' and build is not None and build != fn: return

    # don't compile helper funcs as a binary; no main()
    if fn == "misc" or fn == "__init__" or fn == "wrap_py": return

    if not fn in compiled:
        compiled[fn] = True
    else:
        return

    clean_cmds = ('ws ' + f)
    cmds = ''

    if ext == 'c' or ext == 'cpp':
        clean_cmds += ("; dent " + f)
        cmd = 'g++ -w -O4 -march=native -flto -o ' + fn + '.exe ' + f
        if ext == 'cpp': cmd += ' cpp/misc.cpp'
        cmd += ' -lopengl32 -lglu32 -lgdi32'
        if (not build) or (fn == build):
            print('\t' + cmd)
            cmds += " " + cmd # add_job(cmd) # a = os.system(cmd) # note: didn't use run because compiling might break   
    elif ext =='h':
        clean_cmds += ("; dent " + f)
    elif ext == 'py':
        wrap_file = 'wrap-py_' + fn + '.cpp'
        # for py files, write a cpp wrapper so we can call from bin folder
        cf = open(wrap_file, 'wb') #'wrap_py.cpp', 'wb')
        lines = ['#include<stdlib.h>',
                 '#include<iostream>',
                 '#include<string>',
                 'using namespace std;',
                 'int main(int argc, char ** argv){',
                 #'  string cmd("/cygdrive/c/Program\\\\ Files/Python35/python.exe ");',
                 '  string cmd("/cygdrive/c/Python27/python.exe ");',
                 '  cmd += string("R:/' + os.popen("whoami").read().strip() + '/bin/py/' + fn + '.py");',
                 '  for(int i=1; i<argc; i++){',
                 '    cmd += string(" ") + string(argv[i]);',
                 '  }',
                 'std::cout << cmd << endl;',
                 'system(cmd.c_str());',
                 'return(0);',
                 '}']
        cf.write('\n'.join(lines).encode())
        cf.close()
        cmd = 'g++ -w -O3 -o ' + fn + '.exe ' + ' ' + wrap_file #wrap_py.cpp '
        print('\t' + cmd)
        cmds += " " + cmd # a = os.system(cmd)
        if(True): # 20191113 might set to true later?
            cmd =  ("rm -f " + wrap_file) #wrap_py.cpp")
            cmds += "; " + cmd;
    elif ext.lower() == 'r':
        wrap_file = 'wrap-r_' + fn + '.cpp'
        print(wrap_file)
        # for py files, write a cpp wrapper so we can call from bin folder
        cf = open(wrap_file, 'wb')
        lines = ['#include<stdlib.h>',
                 '#include<iostream>',
                 '#include<string>',
                 'using namespace std;',
                 'int main(int argc, char ** argv){',
                 '  string cmd("rscript ");',
                 '  cmd += string("R:/' + os.popen("whoami").read().strip() + '/bin/R/' + fn + '.R");',
                 '  for(int i=1; i<argc; i++){',
                 '    cmd += string(" ") + string(argv[i]);',
                 '  }',
                 'std::cout << cmd << endl;',
                 'system(cmd.c_str());',
                 'return(0);',
                 '}']
        cf.write('\n'.join(lines).encode())
        cf.close()
        cmd = 'g++ -w -O3 -o ' + fn + '.exe ' + ' ' + wrap_file #wrap_py.cpp '
        print('\t' + cmd)
        cmds += " " + cmd # a = os.system(cmd)
        if(True): # 20191113 set this back to true later?
            cmd =  ("rm -f " + wrap_file) #wrap_py.cpp")
            cmds += "; " + cmd;
 
    add_job(cmds)
    add_clean_job(clean_cmds)

if not build:
    cpp = py = c = R = []
    # find source files and compile
    cpp = os.popen('find ./cpp/ -name "*.cpp"').read().strip().split('\n')
    print(str(cpp))
    py = os.popen('find ./py/ -name "*.py"').read().strip().split('\n')
    print(str(py))
    c = os.popen('find ./c/ -name "*.c"').read().strip().split('\n')
    print(str(c))
    R = os.popen('find ./R/ -name "*.R"').read().strip().split('\n')
    print(str(R))
    n = len(cpp) + len(py) + len(c) + len(R)

    for f in R: compile(f)
    for f in py: compile(f)
    for f in c: compile(f)
    for f in cpp: compile(f)
else:
    print("build", build)
    c_file = 'c/' + build + '.c'
    cpp_file = 'cpp/' + build + '.cpp'
    py_file = 'py/' + build + '.py'
    r_file = 'R/' + build + '.R'
    if exists(cpp_file):
        compile(cpp_file)
    elif exists(c_file):
        compile(c_file)
    elif exists(py_file):
        compile(py_file)
    elif exists(r_file):
        compile(r_file)
    else:
        err("failed to find file for: " + build +
            ". N.b., py goes in py folder, " +
            "cpp goes in cpp folder, etc.")

job_file.close()
clean_file.close()
