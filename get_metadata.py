'''instructions to run: posix-style terminal:

python3 metadata_list.py'''

import os
import sys
import urllib3


def err(m):
    print("Error: " + m)
    sys.exit(1)


def run(cmd):
    a = os.system(cmd)
    if a != 0:
        err("command failed: " + cmd.strip())
    return a


def get_lines(url):
    # get lines from a web page
    http = urllib3.PoolManager()
    html = http.request('GET', url).data
    return str(html).split("\\n")

# make metadata/ folder
if not os.path.exists("metadata") or not os.path.isdir("metadata"):
    os.mkdir("metadata")

# stuff metadata files in a folder
run("mv -f *.csv metadata/")

# get dip metadata
url = "https://catalogue.data.gov.bc.ca/group/data-innovation-program?tags=DIP"
msg = 'unanticipated data stream'
lines = get_lines(url)

'''
Metadata for Child Welfare Program,https://catalogue.data.gov.bc.ca/dataset/metadata-for-child-welfare-program
Metadata for K-12 student demographics and achievements,https://catalogue.data.gov.bc.ca/dataset/metadata-for-k-12-student-demographics-and-achievements
Metadata for BC Benefits Program,https://catalogue.data.gov.bc.ca/dataset/metadata-for-bc-benefits-program
Metadata for Labour Market Programs,https://catalogue.data.gov.bc.ca/dataset/metadata-for-labour-market-programs
Metadata for BC Employment and Assistance,https://catalogue.data.gov.bc.ca/dataset/metadata-for-bc-employment-and-assistance
'''

for line in lines:
    if len(line.split('<a href="/dataset/')) > 1:
        line = line.strip()

        # check expected formatting
        if line[0:7] != '<a href':
            err(msg)
        words = line.split('"')
        if len(words) != 3:
            err(msg)

        # url for dataset page
        dataset = "https://catalogue.data.gov.bc.ca" + words[1]

        # name of dataset
        name = line.split('>')[1].split('<')[0]

        print(name + ',' + dataset)

        ds_lines = [line.rstrip() for line in os.popen("wget -qO- " + dataset).readlines()]

        for ds_line in ds_lines:
            if len(ds_line.split("/download/")) > 1:
                ds_line = ds_line.strip()
                # print("\t" + ds_line)

                # check expected formatting
                if ds_line[0:7] != '<a href':
                    err(msg)
                words = ds_line.split('"')
                if len(words) < 2:
                    err(msg)

                fpath = words[1].strip()
                fname = fpath.split("/")[-1].strip()

                print('\t' + fname)
                cmd = "wget " + fpath

                if not os.path.exists("metadata/" + fname):
                    run(cmd)

# stuff metadata files into folder
run("mv -f *.csv metadata/")

# next: classify field types: nominal, ordinal, date?
