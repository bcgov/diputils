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
'''
2019 07 26 pssg data dictionary has multiple files in it:
    convert this to multiple csv2 files in the format that health
        and education use! '''
from misc import *
if len(args) < 2:
    err("dd_convert_pssg_summary_to_csv [input file.txt]")

fn = args[1]
if not os.path.exists(fn):
    err("could not open input file: " + fn)

dat = open(fn).read().strip().split("\n")

n_observ, n_variables, obs_nchar = None, None, None
i = 0
while i < len(dat):
    if i > 0: dat[i] = dat[i].lower()
    dat[i] = dat[i].strip()
    dot = dat[i].split('.')
    if dot[-1] == 'gz' and dot[-2] == 'dat':
        # new file
        fn = dat[i]
    spc = dat[i].strip().split()
    if len(spc) > 0:
        if spc[0].strip() == 'observations':
            n_observ = int(spc[-1])
        if spc[0].strip() == 'variables' and spc[1] != 'in':
            n_variables = int(spc[-1])
        if spc[0].strip() == 'observation' and spc[1] == 'length':
            obs_nchar = int(spc[-1])
            # print fn, n_observ, n_variables, obs_nchar
            i += 3
            if dat[i].strip().split() != ['#', 'Variable', 'Type', 'Len']:
                err("unexpected format")
            start_pos, end_pos = 1, 1
            ofn = args[1] + '_' + fn + '.csv2'
            print('+w ' + ofn)
            o_f = open(ofn, "wb")
            o_f.write("Start,Stop,Length,Name Abbrev")
            for j in range(1, n_variables + 1):
                i += 1
                w = dat[i].strip().split()
                if w[0] != str(j):
                    err("unexpected format")
                name, var_type, n_char = w[1], w[2], int(w[3])
                end_pos = start_pos + n_char - 1
                out_dat = ",".join([str(start_pos), str(end_pos), str(n_char), name])
                o_f.write('\n' + out_dat)
                start_pos = end_pos + 1

            # pssg file doesn't count EOF / LINEFEED. Here we follow the convention used elsewhere
            out_dat = ",".join([str(end_pos + 1), str(end_pos + 1), str(1), 'LINEFEED'])
            o_f.write('\n' + out_dat)
            o_f.close()
    i += 1
