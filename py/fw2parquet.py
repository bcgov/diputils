'''20210326 convert .dat.gz file w start/stop/length/label data dictionary, to parquet format'''
import pyarrow.parquet as pq
import pyarrow as pa
import math
import zlib
import csv
import sys
import os
args = sys.argv

def err(m):
    print('Error: ' + m); sys.exit(1)

if len(args) < 3: err('usage:\n\t python fw2parquet.py [input dat.gz file] [input dd]')
if args[1][-6:] != 'dat.gz': err('dat.gz file extension expected')
pq_fn = args[1][:-6] + '.parquet' # output parquet file name

hdr, start, stop, length, label = None, [], [], [], []
for row in csv.reader(open(args[2])): # open 
    row = [x.strip() for x in row] # remove whitespace in case
    if hdr is None:
        hdr = [x.lower() for x in row] # convert header to lowercase for compare
    else:
        start.append(int(row[0]))
        stop.append(int(row[1]))
        length.append(int(row[2]))
        label.append(row[3])

expected = ['start', 'stop', 'length', 'label']
if hdr[0:4] != expected: err("unexpected header, expected: " + ",".join(expected))
CHUNK_SIZE, N, f_size = 0, len(start), os.path.getsize(args[1])
for i in range(N): CHUNK_SIZE += length[i]

fields = [pa.field(label[i], pa.string()) for i in range(N)]  # pyarrow schema
schema = pa.schema(fields)
writer = pq.ParquetWriter(sys.argv[1] + '.parquet', schema)
my_file = open(args[1], 'rb')

''' to (de-)compress deflate format, use wbits = -zlib.MAX_WBITS
    to (de-)compress zlib format, use wbits = zlib.MAX_WBITS
    to (de-)compress gzip format, use wbits = zlib.MAX_WBITS | 16 '''
dc = zlib.decompressobj(wbits = zlib.MAX_WBITS | 16) # might need to switch for other format
data, buf, rows, decompressed_data, ci = None, 0, [], None, 0
print("Fields:\n" + ','.join(label))

while buf is not None:
    ci += 1
    buf = my_file.read(CHUNK_SIZE)
    if ci % 1000 == 0: print('%', 100. * my_file.tell() / f_size)
    if buf is None: break
    if data is None: data = dc.decompress(buf).decode()
    else: data += dc.decompress(buf).decode()

    while len(data) >= CHUNK_SIZE:
        front, rest = data[0: CHUNK_SIZE], data[CHUNK_SIZE: ]
        row = [front[start[i] - 1: stop[i]] for i in range(N)]
        rows.append([x.strip() for x in row]) # print(','.join(row))
        data = rest
        data = '' if data is None else data

    if len(rows) > 0:
        arrays = [pa.array([rows[i][j] for i in range(len(rows))]) for j in range(len(rows[0]))]
        table = pa.Table.from_arrays(arrays=arrays, schema=schema)
        writer.write_table(table)
    rows = []
    if len(data) < CHUNK_SIZE and str(buf) == "b''": break
if data != '': err('') # whole file length should b some multiple of CHUNK_SIZE
writer.close()
