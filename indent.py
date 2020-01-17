import shutil
from misc import *

shift_width = 4

if len(args) < 2:
    err('indent [file name] # prefix file with tab')

in_fn = args[1]

if not os.path.exists(in_fn):
    err('could not find input file: ' + in_fn)

shutil.copyfile(in_fn, in_fn + '.bak')
print('+w', in_fn + '.bak')

in_f = open(in_fn, 'rb')
lines = in_f.readlines()
in_f.close()

lines = [((' ' * shift_width) +
         line.decode('utf-8').rstrip()) for line in lines]
open(in_fn, 'wb').write(('\n'.join(lines)).encode())

''' flesh this file out to be an example of "command-line
agnostic" pattern? key-value store of args, with default keys
applied to terms in form of x (should be y:x)'''
