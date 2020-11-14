#!/usr/bin/env python
import os
import sys
from misc import *
'''simple indentation helper for c/c++ code, this implementation 20190121'''

# params -------->
spaces_per_tab = 2

args = sys.argv
if len(args) < 2:
    err("dent.py: simple formatting for C/C++ code. Usage:\n\tdent [infile.cpp]")

def exists(f):
    return os.path.exists(f)

# normalized file path (with slash, if directory)
def normpath(p):
    pp = os.path.abspath(p.strip())
    if os.path.isdir(pp):
        pp += '/'
    return pp

# extension for a file
def ext(fn):
    words = normpath(fn.strip()).split('.')
    return words[-1] if len(words) > 1 else None
    # e.g., ext('scm.py') == '.py'

# open write mode
def wopen(fn):
    f = open(fn, 'w')
    if(f is None):
        err('no write access to file: ' + fn)
    print(fn)
    return f

if len(args) < 2:
    err('dent.py: format C/C++ files for indentation (2 spaces per tab)' +
        '\n\tusage: dent [filename]')
in_file = normpath(args[1])

# there's a python version of this program, too:

if ext(in_file) == 'py':
    print('warning: python not supported yet')

if not exists(in_file):
    err("can't find file: " + str(in_file))

ext = in_file.split('.')[-1]
if not(ext =='h' or ext == 'c' or ext == 'cpp' or ext =='js'):
    print('warning: only c or cpp files supported')

n_indent = 0  # indentation level
indent = ' ' * spaces_per_tab
dat = open(in_file).read()
bak_file = in_file + '.bak'
wopen(bak_file).write(dat)

# after making the backup:
dat = dat.replace('}else{', '}\nelse{')
new_lines, lines = [], dat.strip().split('\n')

for i in range(0, len(lines)):
    line = lines[i].strip()
    line = ' '.join(line.split())
    reindent = (n_indent * indent) + line

    # red for lines that changed, green for unchanged
    if(reindent != lines[i].rstrip()):
        sys.stdout.write("***")
    else:
        sys.stdout.write("")

    # check if brackets are changing indentation level
    last_char = None
    last_chars = None
    try:
        last_chars = line[-2:]
    except:
        pass

    try:
        last_char = line[-1]
    except:
        pass

    if last_char == '{':
        n_indent += 1
    elif last_char =='}' or last_chars == '};':
        n_indent -= 1
        reindent = (n_indent * indent) + line

    print(reindent)
    if reindent.strip() != '':
        new_lines.append(reindent)
    else:
        new_lines.append('')

if(n_indent != 0):
    print("Error:")
    print("n_indent", n_indent, "algorithm may have missed a:")
    print("opening bracket" if n_indent <0 else "closing bracket")
    print('indentation level not 0: either open brackets or the logic of this program too simple')

# add a few filters
new_lines_filt = []
for i in range(0, len(new_lines)):
    if new_lines[i].strip() == '{':
        new_lines_filt[-1] += '{'
    else:
        new_lines_filt.append(new_lines[i])

out = '\n'.join(new_lines_filt).replace('\t', spaces_per_tab * ' ')
out = out.replace('\n\n\n', '\n\n')
wopen(in_file).write(out)
