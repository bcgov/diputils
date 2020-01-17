'''convert csv file to "fixed width" format, incl. data dictionary (metadata)
    
    this program is run automatically by make_fakedata.py
    
    python3 csv_to_fw.py [input csv file name]'''
from misc import *

if len(args) >= 2:
    csv_to_fixedwidth(args)

def csv_to_fixedwidth(args):
    if len(args) < 2:
        err('python3 csv_to_fw.py [input csv file]')
    
    inf, outf = args[1], ''
    if not os.path.exists(inf):
        err('failed to find input file' + inf)
    
    # check file is csv
    try:
        ext = inf[-4:]
    except Exception:
        err('expected .csv file')
    
    # filename for fixed-width format output file
    outfn = inf[:-4] + '.dat'
    out_mfn = inf[:-4] + '.dd'
    
    outfile = open(outfn, 'wb')
    out_metafile = open(out_mfn, 'wb')
    out_metafile.write(('start,stop,length,label').encode())
    
    hdr, data = None, []
    with open(inf, encoding="utf8", errors='ignore') as csvfile:
        csvreader, is_hdr = csv.reader(csvfile, delimiter=','), True
    
        # for each row in metadata file: header or row with field info
        for row in csvreader:
            row = [r.strip() for r in row]
            if is_hdr:
                hdr = row
                is_hdr = False
            else:
                data.append(row)
    
    n_fields = len(hdr)
    start, stop, length, label = [], [], [], []
    last_start, last_stop, last_length = 0, 0, 0
    
    for i in range(0, n_fields):
        this_start = last_stop + 1 if last_stop > 1 else 0
        this_length = 0
    
        # find longest length for this field
        for j in range(0, len(data)):
            ldi = len(data[j][i])
            this_length = ldi if ldi > this_length else this_length
    
        this_stop = this_start + this_length - 1
        print("start", this_start,
              "stop", this_stop,
              "length", this_length,
              "label", hdr[i])
    
        this_label = hdr[i]
        meta_line = [this_start, this_stop, this_length, this_label]
        meta_line = [str(ml) for ml in meta_line]
        out_metafile.write(('\n' + ','.join(meta_line)).encode())
    
        start.append(this_start)
        stop.append(this_stop)
        length.append(this_length)
        label.append(this_label)
    
        last_start = this_start
        last_stop = this_stop
        last_length = this_length
    
    for j in range(0, len(data)):
        outline = []
        for i in range(0, n_fields):
            outline.append(data[j][i].rjust(length[i]))
        outline = ('' if j == 0 else '\n') + ''.join(outline)
        outfile.write(outline.encode())
    
    
    print("number of fields", n_fields)
    outfile.close()
