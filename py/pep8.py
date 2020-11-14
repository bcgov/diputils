from misc import *
files = os.listdir('.')

for f in files:
    f = f.strip()
    if f[-3:] == '.py':
        run('pep8 ' + f)
