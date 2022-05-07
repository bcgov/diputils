'''20220506 terrible join:
For file 1 and file 2, create a new file where line-i of the result is
[line-i from file 1],[line-i from file 2]

e.g. if file one is:
    a,b
    1,2

and file two is:
    c,d
    3,4

the result is:
    a,b,c,d
    1,2,3,4

Yikes!
'''
import os
import sys
args = sys.argv
exist = os.path.exist

def err(m):
    print('Error: ' + m); sys.exit(1)

if len(args) < 3:
    err('python3 csv_hcat.py')

if not exist(args[1]) or not exist(args[2]):
    err('please check input files')

of = 'csv_hcat.csv'
if exist(of): 
    err('output file exists:' + of)

def get(f):
    Z = [x.strip() for x in open(f).read().strip().split('\n')]

X, Y = [get(x) for x in args[1:3]]

if len(X) != len(Y):
    err('files are of different length')

print('+w', of)
open(of, 'wb').write(('\n'.join([x[i] + ',' + y[i] for i in range(max(len(X), len(Y)))])).encode())
print('success')
