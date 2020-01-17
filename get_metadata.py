'''instructions to run: posix-style terminal:

python3 metadata_list.py'''

import shutil
import urllib3
from misc import *
sep = os.path.sep


def get_lines(url):
    # get lines from a web page
    http = urllib3.PoolManager()
    html = http.request('GET', url).data
    return str(html).split("\\n")


def get(url):
    http = urllib3.PoolManager()
    html = http.request('GET', url).data
    return str(html)


def get_lines(url):
    # get lines from a web page
    return get(url).split("\\n")


# make metadata/ folder
if not os.path.exists("metadata") or not os.path.isdir("metadata"):
    os.mkdir("metadata")
else:
    print("done")
    sys.exit(0)

def mv_csv_to_folder():
    # stuff metadata files in a folder
    for f in os.listdir('.'):
        try:
            if f[-4] == '.csv':
                shutil.move(f, 'metadata' + sep + f)
        except Exception:
            pass

mv_csv_to_folder()

# get dip metadata
url = "https://catalogue.data.gov.bc.ca/group/data-innovation-program?tags=DIP"
msg = 'unanticipated data stream'
lines = get_lines(url)

'''
Metadata for Child Welfare Program
    https://catalogue.data.gov.bc.ca/dataset/metadata-for-child-welfare-program
Metadata for K-12 student demographics and achievements
    https://catalogue.data.gov.bc.ca/dataset/metadata-for-k-12-student-demographics-and-achievements
Metadata for BC Benefits Program
    https://catalogue.data.gov.bc.ca/dataset/metadata-for-bc-benefits-program
Metadata for Labour Market Programs
    https://catalogue.data.gov.bc.ca/dataset/metadata-for-labour-market-programs
Metadata for BC Employment and Assistance
    https://catalogue.data.gov.bc.ca/dataset/metadata-for-bc-employment-and-assistance
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

        ds_lines = [line.rstrip() for
                    line in os.popen("wget -qO- " + dataset).readlines()]

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

                if not os.path.exists("metadata" + sep + fname):
                    run(cmd)

# stuff metadata files into folder
mv_csv_to_folder()
print("done")

# ls -1 metadata/
'''
educ_dip_cb_fnlmrk_ft_fnlmrk_vwd_metadata.csv
educ_dip_cb_slscb_ft_anon_rspdnt_vwd_metadata.csv
educ_dip_cb_slscb_ft_idnt_rspdnt_vwd_metadata.csv
educ_dip_cb_slscb_ft_response_vwd_metadata.csv
educ_dip_cb_stulvlcb_ft_crsmrk_vwd_metadata.csv
educ_dip_cb_stulvlcb_ft_fsasclsm0_vwd_metadata.csv
educ_dip_cb_stulvlcb_ft_fsasclsm8_vwd_metadata.csv
educ_dip_cb_stulvlcb_ft_schlstud_vwd_metadata.csv
educ_dip_cb_stulvlcb_ft_studcrd_vwd_metadata.csv
educ_dip_dm_dimstud_metadata.csv
lmid_dip_exit_metadata.csv
lmid_dip_intake_metadata.csv
lmid_dip_participant_metadata.csv
lmid_dip_training_metadata.csv
mcfd_dip_actv_stage_7_metadata.csv
mcfd_dip_all_client_export_metadata.csv
mcfd_dip_cs_clients_parental_metadata.csv
mcfd_dip_cysn_clients_metadata.csv
mcfd_dip_intake_export_metadata.csv
mcfd_dip_location_history_metadata.csv
mcfd_dip_mcfd_fs_case.csv
mcfd_dip_mis_fs_list_export.csv
mcfd_dip_subsidy_metadata.csv
sdpr_dip_bcea_cases_idd_metadata.csv
sdpr_dip_bcea_famtype_codes_metadata.csv
sdpr_dip_bcea_involvement_idd_metadata.csv
sdpr_dip_bcea_program_codes_metadata.csv
sdpr_dip_case_address.csv
sdpr_dip_case_aka.csv
sdpr_dip_case_demograph.csv
sdpr_dip_case_detail.csv
sdpr_dip_case_header.csv
sdpr_dip_case_involve.csv
'''
