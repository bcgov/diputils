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
'''bytes and number of lines tally for data holdings (need to extract)'''
from misc import *
log_fn = "data_count_bytes_lines.csv"

def f_s(fn):
    return os.stat(fn).st_size

tar_gz = os.popen('find R:/DATA/ -name "*.dat.gz"').readlines()
log_f = open(log_fn, "ab") # write file append mode
log_f.write("original_file_size,dat_file_size,dat_file_n_lines,original_file")
log_f.close() # write csv col names

for f in tar_gz: # for each dat.gz file
    fn, lc = f.strip(), 0 # strip whitespace from filename
    base, fs = fn.split("/")[-1], f_s(fn) # short filename, size of orig. file
    dat_fn = ".".join(base.split(".")[0:-1]) # dat file name when extracted

    run("rm -f " + base + " " + dat_fn) # make sure the files don't already exist
    run("cp " + fn + " " + base) # copy the dat.gz file over
    run("unzp " + base) # unzip the dat.gz file to produce the dat file
    try:  lc = int(os.popen("lc " + dat_fn).read().strip()) # line count
    except:  pass

    data = [str(fs),str(f_s(dat_fn)), str(lc), fn] # string to write to csv table
    run("rm -f " + base + " " + dat_fn) # make sure dat and dat.gz file are gone!
    out = ",".join(data) # join string array on comma
    print "\n" + out # display the info as we go

    log_f = open(log_fn, "ab") # append mode doesn't overwrite old runs
    log_f.write("\n" + out) # write the info to file
    log_f.close()
