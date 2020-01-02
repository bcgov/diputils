import os
import sys
import urllib3

def err(m):
    print("Error: " + m)
    sys.exit(1)

def get_lines(url):
    # get lines from a web page
    http = urllib3.PoolManager()
    html = http.request('GET', url).data
    return str(html).split("\\n")

# get dip metadata
url = "https://catalogue.data.gov.bc.ca/group/data-innovation-program?tags=DIP"
msg = 'unanticipated data stream'
lines = get_lines(url)

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

'''
python3 data_list.py
Metadata for Child Welfare Program,https://catalogue.data.gov.bc.ca/dataset/metadata-for-child-welfare-program
Metadata for K-12 student demographics and achievements,https://catalogue.data.gov.bc.ca/dataset/metadata-for-k-12-student-demographics-and-achievements
Metadata for BC Benefits Program,https://catalogue.data.gov.bc.ca/dataset/metadata-for-bc-benefits-program
Metadata for Labour Market Programs,https://catalogue.data.gov.bc.ca/dataset/metadata-for-labour-market-programs
Metadata for BC Employment and Assistance,https://catalogue.data.gov.bc.ca/dataset/metadata-for-bc-employment-and-assistance
'''
